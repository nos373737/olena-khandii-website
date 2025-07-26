# Simple Makefile example

.PHONY: run-webserver

install-venv:
	@echo "Creating virtual environment..."
	python3 -m venv venv

install-deps-in-venv:
	@echo "Activating virtual environment..."
	. venv/bin/activate
	@echo "Installing dependencies..."
	pip install -r requirements.txt

collectstatic: install-venv install-deps-in-venv
	python manage.py collectstatic --noinput

run-webserver: collectstatic
	gunicorn myproject.wsgi:application -c gunicorn_config.py

# If we want to run as a background process
run-webserver-bg: collectstatic
	nohup gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 --workers 3 > gunicorn.log 2>&1 &