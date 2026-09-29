# Календарь звонков


[![hexlet-check](https://github.com/MandosGrogu/python-project-386/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/MandosGrogu/python-project-386/actions)

Сервис бронирования встреч: клиент видит свободные слоты по 30 минут и оформляет запись, владелец календаря смотрит список предстоящих бронирований. Авторизации нет — все действия доступны любому посетителю.

Учебный проект Хекслета: https://ru.hexlet.io/programs/python

**Демо:** https://python-project-386-production.up.railway.app

## Стек

- Python 3.14+, Django 6.1+
- Tailwind CSS
- PostgreSQL (продакшн) / SQLite (разработка)
- uv — менеджер зависимостей
- gunicorn — WSGI-сервер

## Установка

```bash
git clone https://github.com/MandosGrogu/python-project-386.git
cd python-project-386
uv sync
```

Переменные окружения (необязательны, есть значения по умолчанию):

| Переменная           | По умолчанию                            | Назначение                              |
| -------------------- | --------------------------------------- | --------------------------------------- |
| `SECRET_KEY`         | небезопасный ключ для разработки        | ключ Django                             |
| `DEBUG`              | `True`                                  | режим отладки                           |
| `DATABASE_URL`       | `sqlite:///db.sqlite3`                  | подключение к базе данных               |
| `RECORDING_URL_BASE` | `https://recordings.example.com/`       | префикс ссылок на записи                |

Для продакшена задайте `DEBUG=False`, собственный `SECRET_KEY` и `DATABASE_URL`
в формате `postgres://user:password@host:5432/dbname`.

## Использование

```bash
# Применение миграций (при первом запуске)
uv run manage.py migrate

# Сборка стилей (необязательно — собранный tailwind.css уже в репозитории)
uv run manage.py tailwind build

# Сервер разработки
uv run manage.py runserver
```

Основные страницы:

- `/` — главная страница
- `/calendar/` — календарь месяца с бронированиями
- `/calendar/ГГГГ/ММ/ДД/` — свободные слоты выбранного дня
- `/calendar/booking/add/` — форма нового бронирования
- `/upcoming/` — предстоящие бронирования (страница владельца календаря)

## Docker

```bash
docker build -t call-calendar .
docker run -p 8000:8000 -e SECRET_KEY=<секретный-ключ> call-calendar
```

Приложение поднимется на http://localhost:8000. Для базы данных PostgreSQL
передайте `DATABASE_URL`, например:

```bash
docker run -p 8000:8000 \
  -e SECRET_KEY=<секретный-ключ> \
  -e DATABASE_URL=postgres://user:password@host:5432/dbname \
  call-calendar
```

Миграции в контейнере:

```bash
docker run --rm -e SECRET_KEY=<секретный-ключ> call-calendar python manage.py migrate
```

## Разработка

```bash
uv run pytest        # тесты
uv run ruff check    # линтер
```

---

<details>
<summary>Автоматические тесты Хекслета</summary>

Тесты запускаются на каждый коммит. За запуск отвечает файл `.github/workflows/hexlet-check.yml` — не удаляйте и не переименовывайте ни его, ни репозиторий.

</details>

## О Хекслете

[Хекслет](https://ru.hexlet.io/) — школа программирования: авторские программы обучения с практикой, поддержкой наставников и реальными проектами, которые остаются в резюме. Этот репозиторий — один из таких проектов.
