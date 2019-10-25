import json, time
import re
import subprocess
import time
import urllib.request
from threading import Thread

import stashy
from dialog_bot_sdk.bot import DialogBot

import const
from chat_bot import c_bot
from db_utils import db
from templates import get_cred_info, diff


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


class ClearTempWorker(AnsibleWorker):
    file_name = './ansible/clean_temp.yaml'
    reg_exp = re.compile(r'^\s*(Очисти\s+temp\s+директории\s+сервера|temp\s+clean)\s+(\S+)', re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        res, data = self.exec(exp.group(2))
        if res:
            self.reply('Готово')
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


class StashRepoNotifyWorker(DefaultWorker):
    url = "http://52.164.121.202:7990"
    reg_exp = re.compile(r'^\s*(подписка\s+commit|подписка\s+на\s+коммиты)\s+в\s+проекте(\S+)\s+,\s+репозитории(\S+)',
                         re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        project, repo = exp.group(2), exp.group(3)

        if not project or not repo:
            self.reply('Укажи данные существующего проекта и репо Stash')
            return

        cred = db.get_cred(self.param.sender_uid, 'BITBUCKET')
        if not cred:
            self.reply('Не удалось авторизоваться в BitBucket укажи другой логин и пароль')

        stash = stashy.connect(self.url, cred['login'], cred['passswd'])

        prev_commits = []
        intro = 'В репозитории #{}_{} получены новые изменения:'.format(repo, project)
        while True:
            removed_commits_msg, added_commits_msg = '', ''
            commits = list(stash.projects[project].repos[repo].commits())
            if not prev_commits and prev_commits != commits:
                removed_commits = diff(prev_commits, commits)

                if len(removed_commits) > 0:
                    removed_commits_msg = 'Удалены коммиты: {}'.format(" ".join(removed_commits))

                added_commits = diff(commits, prev_commits)
                if len(added_commits) > 0:
                    added_commits_msg = 'Добавлены коммиты: {}'.format(" ".join(added_commits))

                self.reply("\n".join((intro, removed_commits_msg, added_commits_msg)))
                prev_commits = commits

            time.sleep(500)


class StashPrsNotifyWorker(DefaultWorker):
    url = "http://52.164.121.202:7990"
    reg_exp = re.compile(
        r'^\s*(подписка\s+pull\s+request[s]?|подписка\s+на\s+PR)\s+в\s+проекте(\S+)\s+,\s+репозитории(\S+)',
        re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        project, repo = exp.group(2), exp.group(3)

        if not project or not repo:
            self.reply('Укажи данные существующего проекта и репо Stash')
            return

        cred = db.get_cred(self.param.sender_uid, 'BITBUCKET')
        if not cred:
            self.reply('Не удалось авторизоваться в BitBucket укажи другой логин и пароль')

        stash = stashy.connect(self.url, cred['login'], cred['passswd'])

        prev_prs = list(stash.projects[project].repos[repo].pull_requests())
        intro = 'В репозитории #{}_{} получены новые изменения Pull Request:'.format(repo, project)
        while True:
            declined_prs_msg, opened_prs_msg, merged_prs_msg = '', '', ''
            prs = list(stash.projects[project].repos[repo].pull_requests())
            if not prev_prs and prev_prs != prs:
                diff_prs = diff(prs, prev_prs)

                opened_prs = list(filter(lambda x: x.state is 'OPEN', diff_prs))
                if len(opened_prs) > 0:
                    opened_prs_msg = 'Открыты новые pull request\'ы: {}'.format(" ".join(opened_prs))

                merged_prs = list(filter(lambda x: x.state is 'MERGED', diff_prs))
                if len(merged_prs) > 0:
                    merged_prs_msg = 'Вмержены pull request\'ы: {}'.format(" ".join(merged_prs))

                declined_prs = list(filter(lambda x: x.state is 'DECLINED', diff_prs))
                if len(declined_prs) > 0:
                    declined_prs_msg = 'Вмержены pull request\'ы: {}'.format(" ".join(declined_prs))

                self.reply("\n".join((intro, opened_prs_msg, merged_prs_msg, declined_prs_msg)))
                prev_prs = prs

            time.sleep(500)


class StashSinglePrNotifyWorker(DefaultWorker):
    url = "http://52.164.121.202:7990"
    reg_exp = re.compile(
        r'^\s*(подписка\s+pull\s+request[s]?|подписка\s+на\s+PR)\s+с\s+ID\s+(\S+)\s+в\s+проекте(\S+)\s+,\s+репозитории(\S+)',
        re.IGNORECASE)

    def run(self):
        exp = self.reg_exp.match(self.param.message.textMessage.text)
        pr_id, project, repo = exp.group(2), exp.group(3), exp.group(4)

        if not pr_id or not project or not repo:
            self.reply('Укажи данные существующего проекта, репо и PR в Stash')
            return

        cred = db.get_cred(self.param.sender_uid, 'BITBUCKET')
        if not cred:
            self.reply('Не удалось авторизоваться в BitBucket укажи другой логин и пароль')

        stash = stashy.connect(self.url, cred['login'], cred['passswd'])

        prev_pr = stash.projects[project].repos[repo].pull_requests[pr_id].get()
        intro = 'В репозитории #{}_{}_PR{} получены новые изменения Pull Request:'.format(repo, project, pr_id)
        while prev_pr and prev_pr.state != 'MERGED':
            pr = stash.projects[project].repos[repo].pull_requests[pr_id].get()
            if pr != prev_pr:
                diff_info = 'Текущие изменения в PR:\n{}'.format(pr.diff())
                merge_info = 'Информация о доступности слияния:\n{}'.format(pr.merge_info())
                can_merged = 'Слияние можно проводить' if pr.can_merge() else 'Слияние запрещено'

                self.reply("\n".join((intro, diff_info, merge_info, can_merged)))
                prev_pr = pr

            time.sleep(500)




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
    ClearTempWorker,
    JenkinsStatusWorker,
    JenkinsRunWorker,
    AnekdotWorker,
    ChatBotWorker,
    StashRepoNotifyWorker,
    StashPrsNotifyWorker,
    StashSinglePrNotifyWorker
]
