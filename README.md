

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
