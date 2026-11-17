# Ticketing

A small support/bug-tracking ticket system built with Django + HTMX: filterable ticket list, inline status changes and live comments — all without a full page reload, no SPA framework.

Demo: https://ticketing.javid-space.cloud/ (no login required — public demo data)

## Getting Started

```bash
cp .env.example .env
docker compose up -d
```

Then open `http://localhost:8010/tickets/`.

The container seeds demo data automatically on first start (idempotent — use `python manage.py seed_demo_data --flush` to regenerate).

### Django admin

```bash
docker compose exec web python manage.py createsuperuser
```

Then open `http://localhost:8010/admin/`.

## Production Build

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

## Quality & Testing

```bash
docker compose run --rm --entrypoint "" web pytest
```

## Features

- Ticket list with live filters (status/priority/category), no page reload (HTMX)
- Ticket creation form
- Ticket detail: inline status change with history, live comments
- Django admin for categories/tickets
- Idempotent demo data seeding (Faker)

## Stack

- Django 5, django-htmx
- PostgreSQL, Gunicorn, Whitenoise
- TailwindCSS (standalone CLI, compiled at build time — no Node runtime in the final image)
- pytest + pytest-django

---

## Contact

**Contact :** **Javid Mougamadou** — [Site web](https://javid-mougamadou.pro/) · [GitHub](https://github.com/javid-mougamadou) · [LinkedIn](https://www.linkedin.com/in/mougamadoujavid/) · [Discord](https://discord.gg/8rK6CKGb) · [Email](mailto:javid.mougamadou2@gmail.com)
