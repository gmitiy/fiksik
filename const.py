
wrong_command = "Кажется команда указанна неверно"


main_help = '''
Я умею работать с разными компонентами, такими как:
1.Jenkins
2.Сервер
3.BitBucket
Для того, чтобы получить справку о компоненте задай команду "Справка <Наименование компоненты>"'''

first_help = 'Привет! Я Фиксик, твой универсальный помощник.' + main_help

help_context = {
    'JENKINS': '''Справка Jenkins
Для доступа к Jenkins необходимо зарегистрировать учетные данные задав команду:
- "Регистрация Jenkins <Логин> <Пароль>"
Чтобы узнать свои зарегистрированные данные, задай команду-"Reg info" или "Информация о регистрации"

Чтобы получить информацию или управлять сборками, нужно задать определенную команду.
Команды запроса информации:
- "Статус сборки <название Сборки>" Я верну актуальный статус сборки.
Команды управления:
- "Запусти сборку <название Сборки>" 
   При вызове команды я пришлю ссылку для мониторинга. По завершении пришлю информацию о статусе выполнения.
''',

    'BITBUCKET': '''Справка BitBucket
Для доступа к BitBucket необходимо зарегистрировать учетные данные задав команду:
- "Регистрация BitBucket <Логин> <Пароль>"
Чтобы узнать свои зарегистрированные данные, задай команду-"Reg info" или "Информация о регистрации"

Чтобы оформить подписку или запросить информацию, нужно задать определенную команду.
Команды для оформления подписки:
- "Подписка commit" Я буду отправлять оповещения о новых коммитах.
- "Подписка Pull Request" Я буду отправлять оповещения о новых Pull Requst, об изменении статуса Pull Request.
Команды запроса информации:
- "Статус SonarQube" Я верну статистику по проекту из SonarQube. 
Команды запуска:
- "Запусти сборку релиза <наимнование Pull Request>" Я запущу сборку релиза и верну ответ о ее выполнении.''',

    'СЕРВЕР': '''Справка Сервера
Для доступа к Серверу необходимо зарегистрировать учетные данные и данные сервера, задав команду:
- "Регистрация Сервера <Имя> <Адрес> <Логин> <Пароль>"
Чтобы узнать свои зарегистрированные данные, задай команду-"Reg info" или "Информация о регистрации"

Чтобы получить информацию или управлять сервером, нужно задать определенную команду.
Команды запроса информации:
- "Запущенные процессы сервера <имя сервера>" Я верну список всех запущенных процессов на указанном сервере.
- "Статистика использования ресурсов сервера <имя сервера>" Я верну статистику использования ресурсов на указанном сервере.
- "Статус WildFly <имя сервера>" Я верну статус WildFly указанного сервера.
Команды управления:
- "Перезагрузи сервер <имя сервера>" Я верну статус о выполнении команды. 
- "Перезагрузи сервер <имя сервера> тихо" Я перезагружу сервер, без возврата статуса.
- "Очисти temp директории сервера <имя сервера>" Я выполню команду без ответа.'''
}


info_update = 'Информация обновленна'
info_insert = 'Информация сохранена'

cred_error = 'Отсутствуют учетные данные'
command_error = 'Ошибка выполнения команды'

server_connection_fail = 'Не удалось подключится к серверу'
server_connection_denied = 'Отказанно в доступе (проверьте логин и пароль)'
