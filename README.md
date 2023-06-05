# wav_to_mp3_convertor

## Описание задания

API-сервис, позволяющий зарегистрированным пользователям конвертировать аудио файлы из формата 'wav' в формат 'mp3'. Сервис реализует следующие основные функции:
1. Регистрация пользователя - осуществляется POST-запросом клиента, содержащим имя пользователя либо в querry-параметре запроса (как "path?name='user name'"), либо в теле запроса: {"name": "user name"}.

    В результате успешной регистрации пользователь получает уникальный идентификатор в виде строки формата Base32 и временный токен доступа в виде строки формата UUID.

2. Конвертация аудиозаписи из формата 'wav' в 'mp3' и сохранение в базе данных - осуществляется POST-запросом зарегистрированного клиента. Запрос должен содержать токен (bearer token) и идентификатор пользоваталя (id), а также аудиозапись (file) в формате 'wav'.

    При успешной обработке запроса в ответе пользователь получает ссылку для скачивания файла в формате 'mp3'. Ссылка для скачивания имеет следующий вид:
    'http://host:port/record?id=id_record&user=id_user'

3. Зарегистрированный пользователь GET-запросом может получить список своих сохраненных записей.

##  Использованный стек

- Python 3 - версии 3.10+s
- Flask - Python фреймворк
- PostgreSQL - база данных
- SQLAlchemy - ORM (flask-sqlalchemy)
- Alembic - миграции для ORM (flask-migrate)
- pydub (вместе с ffmpeg) - работа с аудифайлами
- pytest - тестирование основного функционала
- gunicorn - WSGI сервер для работы с Flask
- Nginx - веб-сервер
- Docker - проект разворачивается с помощью docker-compose

##  Установка и запуск

Команды в терминале должны выполняться из основной директории проекта (директория с файлом docker-compose.yml). 

```
# Переименовать файл .env-example в .env командой:
mv ./services/web/converter/.env-example ./services/web/converter/.env

# Сборка образов и запуск сервисов в контейнерах:
docker-compose up -d --build

# Проверка запущенных контейнеров (должно быть 3 сервиса: web, nginx и db)
docker ps
```

После запуска контейнеров будет автоматически выполнена инициализация базы данных (применена сохраненная миграция alembic).

## Использование с Postman

1. Регистрация пользователя. 
    Направить POST-запрос:
    - URL:  http://127.0.0.1/get-token
    - Тело запроса в формате JSON:  {"name": "user name"}
    
    Будет получен ответ в формате JSON:  {"id": "base32 string", "token": "UUID string"}

    Пример:

    <img src="https://github.com/wenerikk5/task_12_converter/blob/12f12547e3b6060544ccee1ccf241e7947e2c69c/services/web/converter/data/registration.png">


2. Для авторизации пользователя запросы должны содержать:
    - Токен в заголовоке Authorization в формате 'Bearer token'
    - id пользователя должно быть передано либо в заголовке запроса, либо в форме запроса.

    Пример передачи токена (token) и идентификатора пользователя (id) в заголовке запроса:

    <img src="https://github.com/wenerikk5/task_12_converter/blob/0cd2d42ff5ecfe6845e5861844d98c0bf0127643/services/web/converter/data/authorization.png" alt="2" width="800" height="230">


3. Запрос на передачу 'wav'-аудиозаписи, конвертацию и сохранение в 'mp3'.
    Направить POST-запрос:
    - URL:  http://127.0.0.1/record
    - Запрос должен содержать данные для аутентификации (согласно п. 2) и прикрепленную аудиозапись (file в форме запроса).
    
    При успешной обработке будет получен ответ с ссылкой для скачивания файла в формате 'mp3'. Загрузка файла по ссылке не потребует авторизации.

    Пример запроса на конвертацию и сохранение аудиозаписи:

    <img src="https://github.com/wenerikk5/task_12_converter/blob/0cd2d42ff5ecfe6845e5861844d98c0bf0127643/services/web/converter/data/post_record.png" alt="3" width="800" height="440">

4. Запрос на получение списка сохраненных аудиозаписей пользователя.
    Направить GET-запрос:
    - URL:  http://127.0.0.1/get-records
    - Запрос должен содержать данные для аутентификации (согласно п. 2).

    При успешной обработке будет получен JSON-ответ в виде списка сохранненных записей пользователя.

    Пример запроса списка записей:

    <img src="https://github.com/wenerikk5/task_12_converter/blob/0cd2d42ff5ecfe6845e5861844d98c0bf0127643/services/web/converter/data/get_records.png" alt="4" width="800" height="740">

5. Обновление токена. 
    Токен может быть обновлен в любой момент. Для обновления токена необходимо направить POST-запрос:
    - URL:  http://127.0.0.1/update-token
    - Тело запроса в формате JSON: {"id": "user id", "token": "UUID token"}

    Необходимо направить последний токен пользователя (даже если он просрочен). 
    Будет получен ответ в формате JSON: {"id": "base32 string", "token": "UUID string"}

ПРИМЕЧАНИЕ:
Приложение настроено на использование незащищенного http протокола только в целях демонстрации. В реальном проекте обеспечение безопасности данных пользователей потребует использования протокола https.


## Детали реализации и ограничения

Хранение файлов на сервере обычно организуется либо записью в бинарном виде (BLOB) в базе данных, либо хранением файла в отдельной директории и записью ссылки на файл в базе данных. Второй вариант более предпочтителен, т.к. не требует затрат ресурсов на перевод файла в бинарный формат (при сохранении) и обратно (при передаче). Ввиду того что проект выполнен в демонстративных целях, хранение аудиозаписей в приложении осуществляется непосредственно в базе данных.

Установленные ограничения и особенности реализации:
- Максимальный допустимый размер файла для передачи - 10 Мб;
- Название передаваемого файла должно иметь расширение '.wav';
- При сохранении файла в БД безопасно сохраняется его исходное имя (с расширением '.mp3');
- Ложные файлы с расширением 'wav' вызовут ошибку 400 с соответствующим сообщением;
- Срок действия токена - 24 часа;
- Для тестирования работы конвертора может быть использована запись из директории 'services/web/converter/data/wav1.wav'.


## Тестирование

Приложение содержит функциональные тесты, покрытие 92%.
```
# Для запуска тестов необходимо установить необходимые зависимости из файла requirements.txt,
# активировать виртуальное окружение и перейти в директорию папки converter:
cd /sevices/web/converter

# Запуск тестов
python3 -m pytest -v

# Проверка coverage
python3 -m pytest --cov-report term-missing --cov=app
```
