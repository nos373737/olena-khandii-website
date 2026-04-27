PYTHON ?= python3
VENV := venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

.PHONY: install-venv install-deps-in-venv install migrate collectstatic test run-dev run-webserver run-webserver-bg

$(VENV_PYTHON):
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)

install-venv: $(VENV_PYTHON)

install-deps-in-venv: install-venv requirements.txt
	@echo "Installing dependencies..."
	$(VENV_PIP) install -r requirements.txt

install: install-deps-in-venv

migrate: install
	$(VENV_PYTHON) manage.py migrate

collectstatic: install
	$(VENV_PYTHON) manage.py collectstatic --noinput

test: install
	$(VENV_PYTHON) manage.py test

run-dev: migrate
	$(VENV_PYTHON) manage.py runserver 0.0.0.0:8000

run-webserver: migrate collectstatic
	$(VENV)/bin/gunicorn myproject.wsgi:application -c gunicorn_config.py

run-webserver-bg: migrate collectstatic
	nohup $(VENV)/bin/gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 --workers 3 > gunicorn.log 2>&1 &
