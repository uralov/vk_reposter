# Настройка приложения

## Подготовка Вконтакте
Перед инсталяцией необходимо зарегистрировать «Standalone-приложение» Вконтакте https://vk.com/apps?act=manage.
Необходимо запомнить "ID приложения".

Затем используем ссылку
https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall&response_type=token
для получения прав доступа на пост на стены. Вместо {APP_ID} необходимо подставить "ID приложения".
Необходимо разрешить приложению публиковать посты.

ВНИМАНИЕ: VK имеет ограничение в 50 репостов в день.

## Конфигурация
Перед работой с приложением необходимо произвести его конфигурацию в разделе [Настройки](http://grigory.keeper.fvds.ru/constance/config/)

Каждый параметр конфигурационного файла документирован и не нуждается в более детальном описании

По умолчанию приложение запускает парсинг и репостинг один раз в час. Если необходимо изменить частоту запуска нужно отредактировать файл конфигурации прилоежния.
Редактировать файл можно любым текстовым редактором, например nano
```nano /home/reposter/vk_reposter/src/conf/settings_local.py```

ВНИМАНИЕ: Что бы изменения в конфигурации вступили в силу необходимо рестартовать приложение
```sudo supervisorctl restart reposter:```

## Интерфейс администратора
Система имеет [интерфейс администратора](http://grigory.keeper.fvds.ru/).
Авторизация осуществляется по логину и паролю.

Паблики для парса необходимо добавлять в разделе [Паблики](http://grigory.keeper.fvds.ru/reposter/public/).
Паблики должны иметь полный путь, например https://vk.com/it_61

Спарсенные для репоста посты можно видеть в разделе [Посты](http://grigory.keeper.fvds.ru/reposter/post/)

### Создание нового пользователя
Если необходимо создать нового пользователя для доступа к системе, это можно сделать в разделе [Пользователи](http://grigory.keeper.fvds.ru/auth/user/).
Поскольку интерфейс релазиован через админку Django, после создания пользователя требуется поставить галочки "Статус персонала" и "Статус суперпользователя".


# Установка проекта

## Требования
Python 3

Supervisor - для демонизации gunicorn

Nginx - для раздачи статики

Redis - Необходим для управления задачами Celery

## Установка
Что бы развернуть ещё одну копию проекта необходимо:

0. Направить новый домен на сервер

1. Скопировать директорию /home/reposter/vk_reposter/

2. Запустить файл ~/vk_reposter/vk_reposter/etc/install.sh

3. Скопировать конфигурацию Nginx /etc/nginx/sites-enabled/reposter и адаптировать абсолютные пути в нём до нового проекта. Так же не забыть поправить server_name.
Учитывате, что /etc/nginx/sites-enabled/reposter - ссылка на файл /etc/nginx/sites-available/reposter.

4. Обновить конфигурацию nginx ```sudo service nginx restart```

5. Скопировать конфигурацию Supervisor /etc/nginx/sites-enabled/reposter и адаптировать абсолютные пути в нём до нового проекта.

6.  Обновить конфигурацию supervisor ```sudo supervisorctl update```


# Запуск сервера
Для запуска сервера используется [Supervisor](http://supervisord.org/).
При старте сервера демон супервизора автоматически запустит необходимые процессы.

```sudo supervisorctl status - отображает состояние процессов```

```sudo supervisorctl restart reposter: - рестартует проект reposter```

```sudo supervisorctl restart all - рестартует проект все проекты```
