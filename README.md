# RESTful API

Это демонстрационное API. В роли веб-сервера выступает Gunicorn, обрабатывает запросы фреймворк flask. Работы с базой
данных осуществляется с помощью SQLAlchemy. 

## Запуск ##

Сбор образов,запуск всех необходимых контейнеров осуществляется с помощью команды:
```
docker-compose up -d
```

## Pre-commit hook ##

```
make pre-commit
```

API доступно по URL: 
*http://localhost:7500/api/v1.0/*

### HTTP аутентификация ###
Доступ к порталу ограничивается базовой HTTP аутентификацией. Для добавления пользователя необходимо сгенерировать SHA512 хэш из пароля:
```
# echo -n "password" | openssl dgst -sha512
(stdin)= b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86
```
и добавить логин и хэш в файл конфигурации *config.ini* в раздел *Users*:
```
[Users]
user: b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86
```
чтение конфигурационного файла происходит один раз при запуске. Дефолтные реквизиты: user/user

### Данные для демонстрации ###

Таблица network.devices заполняется из файла *example_data.csv* (вымышленные устройства)
В вызове функций имитируются подключение и конфигурирование сетевых устройств.

### Логи ###

Директория с логами из контейнера монтируется по пути
```
/var/log/confapi/
```

# Примеры запросов #

## Посмотреть доступный функционал ##

HTTP-метод GET

Пример URL:

```bash
curl -u user:user -i -X GET "http://localhost:7500/api/v1.0/functions"
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 135
Server: Werkzeug/2.0.2 Python/3.10.0
Date: Sun, 09 Jan 2022 16:09:25 GMT

{
  "api_version": "0.0.1", 
  "data": [
    "/devices", 
    "/status", 
    "/execute"
  ], 
  "msg": "OK", 
  "status": "success"

```

## Запросить список устройств ##

HTTP-метод GET

Пример Query string:

```bash
curl -u user:user -i -X GET "http://localhost:7500/api/v1.0/devices"
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 1146
Server: Werkzeug/2.0.2 Python/3.10.0
Date: Sun, 09 Jan 2022 17:59:16 GMT

{
  "api_version": "0.0.1", 
  "data": [
    {
      "description": "TOR for dedicated servers", 
      "id": 1, 
      "ip": "10.1.1.192", 
      "location": "1-1-25", 
      "model": "EX3400", 
      "name": "TOR-25", 
      "role": "access", 
      "type": "switch", 
      "vendor": "juniper"
    }, 
    {
      "description": "Aggregation for shared hosting", 
      "id": 2, 
      "ip": "10.1.0.50", 
      "location": "1-1-1", 
      "model": "NEXUS6001", 
      "name": "AGGREGATION-2", 
      "role": "aggregation", 
      "type": "switch", 
      "vendor": "cisco"
    }, 
    {
      "description": "First spine for cloud", 
      "id": 3, 
      "ip": "10.2.0.10", 
      "location": "2-2-1", 
      "model": "QFX5120-32C", 
      "name": "SPINE-1", 
      "role": "spine", 
      "type": "switch", 
      "vendor": "juniper"
    }, 
    {
      "description": "Border router in DC2", 
      "id": 4, 
      "ip": "10.2.0.2", 
      "location": "2-1-1", 
      "model": "MX-480", 
      "name": "ASBR-4", 
      "role": "asbr", 
      "type": "router", 
      "vendor": "juniper"
    }
  ], 
  "msg": "OK", 
  "status": "success"
}

```

## Выполнить команду на устройств ##

HTTP-метод POST

Обязательные параметры:
**id**  - идентификатор устройства в базе
**command** - комманда на исполнение

Пример JSON:

```bash
curl -u user:user -i -H "Content-Type: application/json" -X POST -d '{"id": 2, "command": "show version" }' http://localhost:7500/api/v1.0/execute
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 104
Server: Werkzeug/2.0.2 Python/3.10.0
Date: Sun, 09 Jan 2022 18:04:34 GMT

{
  "api_version": "0.0.1", 
  "data": {
    "task_id": 4
  }, 
  "msg": "OK", 
  "status": "success"
}
```
Возвращает *task_id* - номер задачи по настройке

## Узнать статус настройки ##

HTTP-метод GET
Обязательные параметры:
**task_id**  - идентификатор задачи в базе

Пример JSON:

```bash
curl -u user:user -i -H "Content-Type: application/json" -X POST -d '{"task_id": 9}' http://localhost:7500/api/v1.0/status
```

Пример Query string:

```bash
curl -u user:user -i -X GET "http://localhost:7500/api/v1.0/status?task_id=1"
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 324
Server: Werkzeug/2.0.2 Python/3.10.0
Date: Sun, 09 Jan 2022 17:58:53 GMT

{
  "api_version": "0.0.1", 
  "data": {
    "command": "show version", 
    "created_at": "Sun, 09 Jan 2022 17:58:46 GMT", 
    "device_id": 2, 
    "last_changed": "Sun, 09 Jan 2022 17:58:47 GMT", 
    "msg": "DeviceConnectionError", 
    "status": "error", 
    "task_id": 1
  }, 
  "msg": "OK", 
  "status": "success"
}

```