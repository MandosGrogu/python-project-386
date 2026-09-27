# Календарь звонков

Учебный проект Хекслета — сервис бронирования календаря. В проекте нет авторизации, личных кабинетов и интеграций с внешними календарями. Пользователь видит свободные слоты по 30 минут, может выбрать время и оформить запись, а владелец календаря смотрит список предстоящих встреч.

## Стек

- Python 3.14+
- Django 6.1+
- Tailwind CSS
- PostgreSQL (продакшн) / SQLite (разработка)
- uv — менеджер зависимостей
- gunicorn — WSGI-сервер

## Команды

```bash
# Установка зависимостей
uv sync

# Запуск сервера разработки
uv run manage.py runserver

# Миграции
uv run manage.py makemigrations
uv run manage.py migrate

# Сборка стилей
uv run manage.py tailwind build

# Лinting
uv run ruff check

# Продакшн-запуск
gunicorn call_calendar.wsgi
```

## Структура проекта

```
src/call_calendar/   # Настройки Django-проекта
bookings/            # Приложение бронирований
pages/               # Приложение главной страницы
templates/           # Шаблоны
assets/              # Исходники статических файлов (Tailwind)
tests/               # Тесты
```

## Соглашения

- Код и комментарии — на русском языке
- Коммиты — на русском,  формат сообщений коммитов по спецификации Conventional Commits (feat:, fix: и т.д.), стиль: "добавить форму бронирования", "исправить валидацию даты"
- Зависимости — через uv (uv.lock)
- Переменные окружения — в файле .env (не коммитить)
- Приложение должно собираться в Docker-образ и запускаться в контейнере

## CI

Тесты Хекслета запускаются на каждый пуш через `.github/workflows/hexlet-check.yml`.
Не удалять и не переименовывать workflow-файл.
На основе коммитов работает утилита `release-please`.
Процесс `release-please` настроен как **отдельный GitHub Workflow** (`release.yml`). При обновлении CI/CD конфигурации запрещено переносить шаги релиза в общий файл тестирования. Убедитесь, что у этого workflow настроены права `contents: write` и `pull-requests: write`

## Текущее состояние

Реализованы бронирования (модель, форма с валидацией, CRUD-представления), календарь месяца, страница слотов дня, список предстоящих бронирований, главная страница, авто-генерация ссылки на запись (см. `docs/adr/0001-auto-generated-recording-url.md`), Docker-образ. Тесты — в `tests/test_calls.py`.

## Agent skills

### Issue tracker

Issues live in the repo's GitHub Issues (uses the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
