import grpc
from dialog_bot_sdk.bot import DialogBot

from workers import workers


def get_worker(param, c_bot):
    for Worker in workers:
        if Worker.test(param.message.textMessage.text):
            return Worker(param, c_bot)


def on_msg(*params):
    worker = get_worker(params[0], bot)
    worker.run()


if __name__ == '__main__':
    bot = DialogBot.get_secure_bot(
        'hackathon-mob.transmit.im',
        grpc.ssl_channel_credentials(),
        '7d099430b2a5d78e713aef40018ecfb44f89d5db'
    )

    bot.messaging.on_message(on_msg)
