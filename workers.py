import json, time
import re
import subprocess
import urllib.request
from threading import Thread

from dialog_bot_sdk.bot import DialogBot
from chat_bot import c_bot

import const
from db_utils import db
from templates import get_cred_info


class DefaultWorker(Thread):
    def __init__(self, param, bot):
        super().__init__()
        self.param = param
        self.bot: DialogBot = bot

    reg_exp = re.compile(r'.*', re.IGNORECASE)

    @classmethod
    def test(cls, msg):
        return cls.reg_exp.match(msg)

    def run(self):
        self.reply(const.wrong_command)

    def reply(self, text):
        self.bot.messaging.reply(self.param.peer, [self.param.mid], text)

    def send(self, text):
        self.bot.messaging.send_message(self.param.peer, text)


class AnekdotWorker(DefaultWorker):
    reg_exp = re.compile(r'(анекдот)', re.IGNORECASE)

    def run(self):
        data = {}
        for _ in range(4):
            with urllib.request.urlopen("http://rzhunemogu.ru/RandJSON.aspx?CType=1") as url:
                try:
                    data = json.loads(url.read().decode('cp1251'), strict=False)
                    break
                except:
                    pass
        self.reply(data.get('content', 'Не прошло ('))


class HelpWorker(DefaultWorker):
    reg_exp = re.compile(r'^\s*(справка|помощь|help|/start)\s*(\S*)?', re.IGNORECASE)

    def run(self):
        msg = self.param.message.textMessage.text
        if msg == '/start':
            self.send(const.first_help)
            return

        exp = self.reg_exp.match(msg)
        if exp and exp.group(2):
            self.reply(const.help_context.get(exp.group(2).upper(), const.wrong_command))
            return

        self.reply(const.main_help)


class CredentialsWorker(DefaultWorker):
    reg_exp = re.compile(r'^\s*(регистрация|reg)\s+(jenkins|bitbucket)\s+(\S+)\s+(\S+)', re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        res = db.upsert_cred(
            user_id=self.param.sender_uid,
            system=exp.group(2).upper(),
            login=exp.group(3),
            passwd=exp.group(4)
        )
        self.reply(const.info_update if res else const.info_insert)


class CredentialsServerWorker(DefaultWorker):
    reg_exp = re.compile(r'^\s*(регистрация|reg)\s+(сервер[а]?|server)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        res = db.upsert_cred(
            user_id=self.param.sender_uid,
            system='SRV',
            alias=exp.group(3),
            ip=exp.group(4),
            login=exp.group(5),
            passwd=exp.group(6)
        )
        self.reply(const.info_update if res else const.info_insert)


class CredentialsPrintWorker(DefaultWorker):
    reg_exp = re.compile(r'^\s*(информация\s+о\s+регистрации|reg\s+info)', re.IGNORECASE)

    def run(self):
        self.reply(get_cred_info(self.param.sender_uid))


class AnsibleWorker(DefaultWorker):
    file_name = ''
    command = 'ansible-playbook {file} -e ' \
              '"ansible_connection=ssh ansible_ssh_user={login} ansible_ssh_pass={passwd}" -i {ip},'

    def exec(self, alias):
        cred = db.get_cred_by_alias(self.param.sender_uid, alias)
        if cred:
            command = self.command.format(file=self.file_name,
                                          login=cred['login'],
                                          passwd=cred['passwd'],
                                          ip=cred['ip'])

            process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            output, _ = process.communicate()
            output = output.decode('ascii')
            if 'Failed to connect to the host' in output:
                return False, const.server_connection_fail

            if 'Permission denied' in output:
                return False, const.server_connection_denied

            return True, output
        return False, const.cred_error

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        _, data = self.exec(exp.group(2))
        self.reply(data)


class HostInfoWorker(AnsibleWorker):
    file_name = './ansible/host_info.yaml'
    reg_exp = re.compile(r'^\s*(Состояние\s+использования\s+ресурсов\s+сервера|server\s+info)\s+(\S+)', re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        res, data = self.exec(exp.group(2))
        if res:
            tmp = str(data).splitlines()
            try:
                self.reply("\n".join([tmp[i] for i in range(1, 6)]))
            except IndexError:
                print(tmp)
                self.reply(const.command_error)
        else:
            self.reply(data)


class RebootWorker(AnsibleWorker):
    file_name = './ansible/reboot.yaml'
    reg_exp = re.compile(r'^\s*(перезагрузи\s+сервер|server\s+reboot)\s+(\S+)', re.IGNORECASE)


class FastRebootWorker(AnsibleWorker):
    file_name = './ansible/fast_reboot.yaml'
    reg_exp = re.compile(r'^\s*(перезагрузи\s+сервер|server\s+reboot)\s+(\S+)\s+(тихо|fast)', re.IGNORECASE)


class ProcessListWorker(AnsibleWorker):
    file_name = './ansible/process_list.yaml'
    reg_exp = re.compile(r'^\s*(запущенные\s+процессы\s+сервера|server\s+proc)\s+(\S+)', re.IGNORECASE)


class WildflyWorker(AnsibleWorker):
    file_name = './ansible/check_wf.yaml'
    reg_exp = re.compile(r'^\s*(статус\s+wildfly|status\s+wildfly)\s+(\S+)', re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        res, data = self.exec(exp.group(2))
        if res:
            tmp = str(data).splitlines()
            if tmp[-1] == 'true':
                self.reply('Wildfly запущен')
            else:
                self.reply('Wildfly остановлен')
        else:
            self.reply(data)


class ChatBotWorker(DefaultWorker):
    def run(self):
        self.send(str(c_bot.get_response(self.param.message.textMessage.text)))


class JenkinsWorker(DefaultWorker):
    command = 'java -cp ./jar/jenkinsadapter.jar ru.sberbank.hackathon.jenkins.Main http://192.168.31.105:8080 ' \
              '{login} {passwd} {command} {param}'

    def exec(self, command, param):
        cred = db.get_cred(self.param.sender_uid, 'JENKINS')
        if cred:
            command = self.command.format(login=cred['login'],
                                          passwd=cred['passwd'],
                                          command=command,
                                          param=param)

            process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            if error:
                return False, error.decode('utf-8')
            return True, output.decode('utf-8')
        return False, const.cred_error


class JenkinsStatusWorker(JenkinsWorker):
    reg_exp = re.compile(r'^\s*(статус\s+сборки|job\s+status)\s+(\S+)', re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        res, data = self.exec('status', exp.group(2))
        self.reply(data)


class JenkinsRunWorker(JenkinsWorker):
    reg_exp = re.compile(r'^\s*(запусти\s+сборку|job\s+run)\s+(\S+)', re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        res, data = self.exec('build', exp.group(2))
        self.reply(data)
        i = 0
        while i < 12:
            time.sleep(4)
            res, data = self.exec('status', exp.group(2))
            i += 1
            if data in ['FAILURE', 'SUCCESS']:
                self.reply("Результат сборки: " + data)
                return
        self.reply('Привышен интервал ожидания сборки')


workers = [
    HelpWorker,
    CredentialsWorker,
    CredentialsServerWorker,
    CredentialsPrintWorker,
    HostInfoWorker,
    RebootWorker,
    FastRebootWorker,
    ProcessListWorker,
    WildflyWorker,
    JenkinsStatusWorker,
    JenkinsRunWorker,
    AnekdotWorker,
    ChatBotWorker
]
