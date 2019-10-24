
wrong_command = "Кажется команда указанна неверно"


main_help = '''
Я умею работать с разными компонентами, такими как:
1.Jenkins
2.Сервера
3.BitBukcet
Для того, чтобы получить справку о компоненте задай команду "Справка <Наименование компоненты>"'''

first_help = 'Привет! Я Фиксик, твой универсальный помощник.' + main_help

help_context = {
    'JENKINS': '''Справка Jenkins
Для доступа к Jenkins необходимо зарегестировать учетные данные задав команду:
- "Регистрация Jenkins <Логин> <Пароль>"

Чтобы получить информацию или управлять сборками, нужно задать определенную команду.
Команды запроса информации:
- "Проекты Jenkins" Я верну список доступных проектов
- "Сборки для проекта <наименование проекта>" Я верну список наименования(ий) сборок, доступных для управления, у выбранного проекта.
- "Статус сборки <наименование Сборки>" Я верну статус сборки.
Команды управления:
- "Запусти сборку <название Сборки>" 
- "Останови сборку <название Сборки>" 
- "Перезапусти сборку <название Сборки>"
   При вызове команд: запуск, остановка или перезапуск я выполню команду и пришлю ссылку для мониторинга. По завершении пришлю информацию о статусе выполнения.
''',

    'BITBUCKET': '''Справка Bitbucket
Для доступа к BitBucket необходимо зарегестировать учетные данные задав команду:
- "Регистрация BitBucket <Логин> <Пароль>"

Чтобы оформить подписку или запросить информацию, нужно задать определенную команду.
Команды для оформления подписки:
-"Подписка commit" Я буду отправлять оповещения о новых коммитах.
-"Подписка Pull Request" Я буду отправлять оповещения о новых Pull Requst, об изменении статуса Pull Request.
Команды запроса информации:
-"Статус Сонар" Я верну статистику по проекту из SonarQube.''',

    'СЕРВЕРА': '''Справка Сервера
Для доступа к Серверу необходимо зарегестировать учетные данные и данные сервера, задав команду:
- "Регистрация Сервера <Имя> <Адрес> <Логин> <Пароль>"

Чтобы получить инфломацию или управлять сервером, нужно задать определенную команду.
Команды запроса информации:
- "Запущенные процессы сервера <имя сервера>" Я верну список всех запущенных процессов на указанном сервере.
- "Состояние сервера <имя сервера>" Я верну список состояний ресурсов на указанном сервере.
- "Статус WildFly <имя сервера>" Я верну статус WildFly указанного сервера.
Крманды управления:
- "Перезагрузи сервер <имя сервера>" Я верну статус о выполнении команды. 
- "Перезагрузи WildFly сервера <имя сервера>" Я верну статус о выполнении команды. 
- "Очисти temp директории сервера <имя сервера>" Я выполню команду без ответа.'''
}


info_update = 'Информация обновленна'
info_insert = 'Информация сохранена'

cred_error = 'Отсутствуют учетные данные'
command_error = 'Ошибка выполнения команды'

server_connection_fail = 'Не удалось подключится к серверу'
server_connection_denied = 'Отказанно в доступе (проверьте логин и пароль)'
