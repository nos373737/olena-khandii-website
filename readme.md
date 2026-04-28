# Olena Khandii Website

Personal Django website for an English teacher. The site is designed to work as a public profile, blog, service catalogue, reviews page, and a future base for monetisation through groups, digital products, newsletters, or paid learning content.

## Stack

- Python / Django
- SQLite for local development
- Bootstrap 4 vendor assets plus custom CSS
- Django Unfold for the admin interface
- django-import-export and django-tinymce for content management
- django-axes for admin login throttling
- Gunicorn for production-style serving
- WhiteNoise for static files

## Local Setup

The Makefile is the source of truth for day-to-day commands.

```bash
make install
make migrate
make run-dev
```

Open the site at:

```text
http://127.0.0.1:8000/
```

Open the Django admin at:

```text
http://127.0.0.1:8000/studio/
```

Create an admin user when needed:

```bash
venv/bin/python manage.py createsuperuser
```

## Makefile Commands

```bash
make install-venv
```

Creates the local `venv`.

```bash
make install-deps-in-venv
```

Installs Python dependencies into `venv`.

```bash
make install
```

Creates the virtual environment if needed and installs dependencies.

```bash
make migrate
```

Applies database migrations.

```bash
make collectstatic
```

Collects static assets for production-style serving.

```bash
make test
```

Runs the Django test suite.

```bash
make run-dev
```

Runs the Django development server on `0.0.0.0:8000`.

```bash
make run-webserver
```

Runs migrations, collects static files, and starts Gunicorn with `gunicorn_config.py`.

```bash
make run-webserver-bg
```

Starts Gunicorn in the background and writes output to `gunicorn.log`.

## Content Workflow

1. Create categories in Django admin.
2. Add blog posts with title, category, content, and image.
3. Use the public blog page to validate how posts appear.
4. Keep service, pricing, rules, and review pages updated as the business offer changes.

## Admin Configuration

The admin runs on Django Unfold and is configured for editorial work:

- `/studio/` replaces the default `/admin/` path.
- Blog, category, comment, and contact models support CSV/XLSX import/export.
- Blog content uses TinyMCE in the admin editor.
- Failed login attempts are throttled by django-axes when `DEBUG=False`.

The admin URL is configurable through `DJANGO_ADMIN_URL`.

```bash
DJANGO_ADMIN_URL=studio/
```

Useful production security environment variables:

```bash
DJANGO_DEBUG=False
DJANGO_AXES_ENABLED=True
DJANGO_AXES_FAILURE_LIMIT=5
DJANGO_AXES_COOLOFF_HOURS=1
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=3600
```

After installing or deploying these dependencies, run:

```bash
make migrate
make collectstatic
```

Use a non-default admin path in production, keep `DEBUG=False`, and serve admin only over HTTPS.

## Frontend Direction

The current design is built around a personal teacher brand rather than a generic blog template:

- clear hero with Olena as the first-viewport signal
- direct paths to services, prices, reviews, and blog
- modern editorial blog cards with image fallbacks
- placeholders that make future newsletter or paid content features straightforward

## Notes

- `db.sqlite3` is suitable for local development. Use a production database before serious monetisation.
- Move sensitive settings such as `SECRET_KEY` and `DEBUG` to environment variables before production hardening.
- Add real tests around post creation, comments, contact requests, and auth flows as the project grows.
