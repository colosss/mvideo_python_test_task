# MVideo Python test task

Это тестовое задание на Python.

Проект собирает HTTP логи, сохраняет их в базу и отдельно выгружает их в файл.

В проекте есть 3 сервиса:

- web-api-service принимает логи и сохраняет их в PostgreSQL
- client-service генерирует логи и отправляет их в web-api-service
- background-processing-service забирает логи из web-api-service и пишет их в файл

Пример лога:

```text
192.168.1.1 GET /api/users 200
```

## Стек

- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy
- asyncpg
- PostgreSQL
- httpx
- Docker
- Docker Compose

## Архитектура

Проект разделен на несколько слоев.

- core - основные модели и интерфейсы
- application - основная логика приложения
- infrastructure - работа с базой, файлами и HTTP клиентами
- interfaces - API, worker и запуск сервисов
- config - настройки из переменных окружения

Я сделал такое разделение, чтобы логика приложения не зависела напрямую от FastAPI, SQLAlchemy и других внешних библиотек.

## Что делает проект

web-api-service:

- принимает POST запрос с логом
- проверяет формат лога
- разбирает лог на ip, method, uri и status_code
- сохраняет данные в PostgreSQL
- возвращает сохраненные логи через GET запрос
- отдает статистику через отдельный endpoint

client-service:

- генерирует случайные HTTP логи
- отправляет их в web-api-service
- работает в несколько потоков
- пишет отправленные сообщения в файл

background-processing-service:

- периодически делает GET запрос к web-api-service
- получает новые логи
- сохраняет их в файл в Docker volume
- может запускаться в нескольких экземплярах

Для общего файла используется блокировка через fcntl.flock, чтобы несколько background сервисов не писали в файл одновременно.

## Запуск

Сначала нужно создать .env файл:

```bash
cp .env.example .env
```

Запустить все сервисы:

```bash
docker compose up --build
```

Web API будет доступен здесь:

```text
http://localhost:8000
```

Остановить проект:

```bash
docker compose down
```

Остановить проект и удалить данные из volume:

```bash
docker compose down -v
```

Запустить несколько background сервисов:

```bash
docker compose up --build --scale background-processing-service=3
```

## API

Создать лог:

```bash
curl -X POST http://localhost:8000/api/data \
  -H 'Content-Type: application/json' \
  -d '{"log":"192.168.1.1 GET /api/users 200"}'
```

Получить логи:

```bash
curl 'http://localhost:8000/api/data?limit=10&order=desc'
```

Получить статистику:

```bash
curl http://localhost:8000/api/stats
```

Пример ответа статистики:

```json
{
  "methods": {
    "GET": 120,
    "POST": 95
  },
  "status_codes": {
    "200": 210,
    "404": 15
  }
}
```

## Параметры GET /api/data

- limit - сколько записей вернуть
- offset - сколько записей пропустить
- method - фильтр по HTTP методу
- status_code - фильтр по статусу
- created_after - получить записи после указанного времени
- created_before - получить записи до указанного времени
- order - сортировка asc или desc

## Переменные окружения

PostgreSQL и Web API:

- DB_NAME - имя базы данных
- DB_USER - пользователь базы данных
- DB_PASSWORD - пароль базы данных
- DB_PUBLIC_PORT - порт PostgreSQL на компьютере
- DB_ECHO - выводить SQL запросы или нет
- WEB_API_PUBLIC_PORT - порт Web API на компьютере

Client service:

- CLIENT_WORKERS - количество потоков
- CLIENT_MAX_DELAY_MS - максимальная задержка между запросами
- CLIENT_REQUESTS_PER_WORKER - количество запросов на один поток, 0 значит без лимита
- CLIENT_HTTP_TIMEOUT_SECONDS - timeout для HTTP запроса

Background service:

- FETCH_INTERVAL_SECONDS - как часто забирать данные
- EXPORT_BATCH_LIMIT - сколько записей забирать за один раз
- BACKGROUND_HTTP_TIMEOUT_SECONDS - timeout для HTTP запроса

## Файлы

Client service пишет отправленные логи сюда:

```text
/var/log/client-service/sent_logs.jsonl
```

Background service пишет выгруженные логи сюда:

```text
/data/http_logs.jsonl
```

## Решения и допущения

- таблица http_logs создается при старте web-api-service
- миграции Alembic не используются, потому что для тестового задания проще создать таблицу автоматически
- лог должен состоять из ip, method, uri и status_code
- uri должен начинаться с /
- status_code должен быть от 100 до 599
- статистика считается через SQL запросы с группировкой
- background service хранит last_created, чтобы не выгружать одни и те же записи снова
- общий файл защищен через fcntl.flock

## Проверка без Docker

Проверить, что код компилируется:

```bash
python -m compileall \
  services/web_api_service/src services/web_api_service/main.py \
  services/client_service/src services/client_service/main.py \
  services/background_processing_service/src services/background_processing_service/main.py
```

Запустить тесты web-api-service:

```bash
cd services/web_api_service
PYTHONPATH=. python -m unittest discover -s tests
```
