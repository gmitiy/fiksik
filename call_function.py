import json, re
import urllib.request
from hendlers import cred_handler, help_hendler, srv_hendler

from chatterbot.conversation import Statement
from chatterbot.logic import LogicAdapter


class CallFunctionAdapter(LogicAdapter):

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.known_commands = {
            'АНЕКДОТ': self.get_funny_story,
            'ТОСТ': self.get_tost,
            'СПРАВКА': self.get_help,
            'РЕГИСТРАЦИЯ': self.process_cred,
            'ЗАПУЩЕННЫЕ ПРОЦЕССЫ СЕРВЕРА': self.process_srv,
            'СОСТОЯНИЕ РЕСУРСОВ СЕРВЕРА': self.process_srv,
            'ПЕРЕЗАГРУЗИ СЕРВЕР': self.process_srv
        }

    @staticmethod
    def process_srv(statement):
        return srv_hendler.process_host_info(statement)

    @staticmethod
    def process_cred(statement):
        return cred_handler.process_cred(statement)

    @staticmethod
    def get_help(statement):
        return help_hendler.get_help(statement)

    @staticmethod
    def get_funny_story(statement):
        with urllib.request.urlopen("http://rzhunemogu.ru/RandJSON.aspx?CType=1") as url:
            data = json.loads(url.read().decode('cp1251'), strict=False)
            print(data)
        return data.get('content', 'Не прошло (')

    @staticmethod
    def get_tost(statement):
        with urllib.request.urlopen("http://rzhunemogu.ru/RandJSON.aspx?CType=6") as url:
            data = json.loads(url.read().decode('cp1251'), strict=False)
            print(data)
        return data.get('content', 'Не прошло (')

    def can_process(self, statement):
        return any(com in str(statement).upper() for com in self.known_commands)

    def process(self, statement, additional_response_selection_parameters=None):
        response = Statement('Что-то не выходит!')
        response.confidence = 0.1
        statement_text = str(statement).upper()
        try:
            for com in self.known_commands:
                if com in statement_text:
                    response.text = self.known_commands[str(com)](statement)
                    response.confidence = 1.0
                    return response
        except Exception as e:
            print(e)

        return response
