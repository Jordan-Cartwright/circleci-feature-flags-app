.PHONY: help venv install run test clean

PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
PYTEST ?= .venv/bin/pytest

PORT ?= 8080
FLASK_DEBUG ?= true
FLASK_ENV ?= development

help:
	@echo "Available targets:"
	@echo "  make venv        Create virtual environment"
	@echo "  make install     Install dependencies"
	@echo "  make run         Run app in dev mode"
	@echo "  make test        Run tests"
	@echo "  make clean       Remove caches and temp files"

venv:
	@python -m venv .venv

install: venv
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@$(PIP) install -r requirements-dev.txt

run:
	@FLASK_DEBUG=$(FLASK_DEBUG) \
	PORT=$(PORT) \
	$(PYTHON) main.py

test:
	@$(PYTHON) -m pytest --cov=demo tests/ --cov-report=term-missing --cov-report=html --cov-fail-under=65 --junitxml=test-results/junit.xml

clean:
	@rm -rf .pytest_cache
	@rm -rf __pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} +
