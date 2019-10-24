from chatterbot import ChatBot
from chatterbot import languages
from chatterbot.trainers import ChatterBotCorpusTrainer

import const

c_bot = ChatBot(
    'Фиксик',
    storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.MathematicalEvaluation',
            'language': languages.RUS
        },
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': const.wrong_command
        }
    ],
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace'
    ],

)

# trainer = ChatterBotCorpusTrainer(c_bot)
#
# trainer.train(
#     "chatterbot.corpus.russian"
# )
