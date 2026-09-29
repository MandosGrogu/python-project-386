FROM python:3.14-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH" \
    DEBUG=False \
    SECRET_KEY=django-insecure-dev-key-change-in-production

COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

RUN uv pip install -e . --no-deps

RUN python manage.py collectstatic --noinput

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 call_calendar.wsgi:application"]
