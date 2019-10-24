import grpc
from hendlers.help_hendler import get_help
from chatterbot import ChatBot
from chatterbot import languages
from dialog_bot_sdk.bot import DialogBot


def on_msg(*params):
    print('='*40)
    print('on msg', params)
    in_text = params[0].message.textMessage.text
    if in_text == '/start':
        resp_text = get_help(in_text)
    elif in_text == '/stop':
        resp_text = 'Пращай (('
    else:
        resp_text = str(c_bot.get_response(in_text, tags=[params[0].sender_uid]))

    bot.messaging.send_message(
        params[0].peer, resp_text
    )


if __name__ == '__main__':
    c_bot = ChatBot(
        'Фиксик',
        storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
        logic_adapters=[
            {
                'import_path': 'call_function.CallFunctionAdapter'
            },
            {
                'import_path': 'chatterbot.logic.MathematicalEvaluation',
                'language': languages.RUS
            },
            {
                'import_path': 'chatterbot.logic.BestMatch',
                'default_response': 'Я еще не все понимаю.'
            }
        ],
        preprocessors=[
            'chatterbot.preprocessors.clean_whitespace'
        ]
    )

    # trainer = ChatterBotCorpusTrainer(c_bot)
    #
    # trainer.train(
    #     "chatterbot.corpus.russian"
    # )

    bot = DialogBot.get_secure_bot(
        'hackathon-mob.transmit.im',
        grpc.ssl_channel_credentials(),
        '7d099430b2a5d78e713aef40018ecfb44f89d5db'
    )

    bot.messaging.on_message(on_msg)
