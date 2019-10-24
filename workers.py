import re
import const
from threading import Thread
from dialog_bot_sdk.bot import DialogBot
from db_utils import db
from templates import get_cred_info


class DefaultWorker(Thread):
    def __init__(self, param, c_bot):
        super().__init__()
        self.param = param
        self.bot: DialogBot = c_bot

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


class HelpWorker(DefaultWorker):
    reg_exp = re.compile(r'^\s*(справка|помощь|help)\s*(\S*)?', re.IGNORECASE)

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
    reg_exp = re.compile(r'^\s*(регистрация|reg)\s+(info|информация)', re.IGNORECASE)

    def run(self):
        self.reply(get_cred_info(self.param.sender_uid))


workers = [
    HelpWorker,
    CredentialsWorker,
    CredentialsServerWorker,
    CredentialsPrintWorker,
    DefaultWorker
]
