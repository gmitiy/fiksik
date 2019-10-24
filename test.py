import grpc, time, re
from threading import Thread
from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk.interactive_media import *

class HelpWorker(object):
    pass

def get_worker(msg):
        workers = (
            {
                'name': 'Help Worker',
                'reg_exp': re.compile(r'.*(справка|помощь)\s*(\S*)?', flags=re.IGNORECASE),
                'class': HelpWorker
            }
        )
        for worker in wo




def main_handler(param, bot: DialogBot):
    pass


def on_msg(*params):
    proc = Thread(target=main_handler, args=(params[0], bot,))
    proc.run()


def on_click(*params):
    print(params)


if __name__ == '__main__':
    bot = DialogBot.get_secure_bot(
        'hackathon-mob.transmit.im',
        grpc.ssl_channel_credentials(),
        '7d099430b2a5d78e713aef40018ecfb44f89d5db'
    )

    bot.messaging.on_message(on_msg, on_click)
