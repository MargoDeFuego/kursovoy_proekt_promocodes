## Реализованные учебные требования

- Бизнес-логика и валидация промокодов описаны в `docs/technical_spec.md`.
- Добавлены роли: администратор, покупатель, гость.
- Использованы `select_related`, `prefetch_related`, аннотации `Count`.
- Добавлены DRF-сериализаторы с `SerializerMethodField` и контекстом.
- Добавлен `django-filter` для фильтрации промокодов.
- Добавлена Postman-коллекция: `postman_collection.json`.
- Добавлены Sentry, Django Silk, Celery, Redis, Mailhog, OAuth2 Google.
- Добавлены тесты: `promocode/tests.py`.

## Полезные команды

```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
docker compose exec web python manage.py deactivate_expired_promos
```

Адреса:

- сайт: http://localhost:8000
- админка: http://localhost:8000/admin/
- API: http://localhost:8000/api/promos/
- Silk: http://localhost:8000/silk/
- Mailhog: http://localhost:8025
- pgAdmin: http://localhost:5050

## Demo data and empty pages
Если сайт открывается, но списки пустые — создайте демо‑данные:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo_data
```

После этого откройте:

- http://localhost:8000/
- http://localhost:8000/promos/
- http://localhost:8000/shops/

## Production deployment

Проект полностью готов к продакшен‑развёртыванию и включает отдельные конфигурации для dev/prod окружений.

Стек продакшена
Docker + Docker Compose
Gunicorn — WSGI‑сервер
Nginx — reverse proxy
PostgreSQL — основная БД
Redis — брокер задач
Celery + Celery Beat — фоновые задачи
Mailhog / SMTP — тестовая почта
Sentry — мониторинг ошибок

1. Подготовка окружения
Создайте файл .env.prod:
DEBUG=0
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@postgres:5432/dbname
REDIS_URL=redis://redis:6379/0

2. Сборка и запуск продакшен‑контейнеров
docker compose -f docker-compose.prod.yml up --build -d
Контейнеры:
web — Django + Gunicorn
nginx — reverse proxy
postgres — база данных
redis — брокер задач
celery — воркер
celery-beat — планировщик

3. Сбор статики
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

4. Применение миграций
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

5. Перезапуск сервиса
docker compose -f docker-compose.prod.yml restart

6. Проверка логов
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f celery

SSL (опционально)
Если сервер поддерживает Certbot:
sudo certbot --nginx -d yourdomain.com

7. Проверка работоспособности
После запуска проект будет доступен по адресу:
https://yourdomain.com
Проверьте:
/api/promos/
/admin/
/promos/

8. Обновление проекта
git pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput