ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

ARTIFACTS_DIR ?= ${ROOT_DIR}/artifacts

VENV_DIR ?= /venv
VENV_BIN := ${VENV_DIR}/bin
VENV_PYTHON := ${VENV_BIN}/python
VENV_PYTEST := ${VENV_BIN}/pytest
VENV_FLAKE8 := ${VENV_BIN}/flake8
VENV_MYPY := ${VENV_BIN}/mypy
VENV_DJANGO := ${VENV_BIN}/django-admin
VENV_BLACK := ${VENV_BIN}/black
VENV_ISORT := ${VENV_BIN}/isort

DJANGO_SETTINGS_MODULE ?= 'pdf_gen_poc.settings'

.DEFAULT_GOAL := help

.PHONY: help
help:
	@ grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

################
# Run test suite
################

.PHONY: test_flake8
test_flake8: ## run flake8 tests
	${VENV_FLAKE8}

.PHONY: test_black
test_black: ## run black test
	${VENV_BLACK} --check .

.PHONY: test_isort
test_isort: ## run isort test
	${VENV_ISORT} --check-only .

.PHONY: test_python
test_python: ## run python tests
	AUTHENTICATION_BACKENDS=django.contrib.auth.backends.ModelBackend COVERAGE_FILE=.unit.coverage \
	${VENV_PYTEST} -vv --capture=sys --junitxml=${ARTIFACTS_DIR}/pytest/unit-report.xml \
	--cov=${ROOT_DIR}/pdf_gen_poc --cov-report=term-missing:skip-covered ${ROOT_DIR}/pdf_gen_poc

.PHONY: test_makemigrations
test_makemigrations: ## Check if all migrations have been created
	DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} ${VENV_PYTHON} ${ROOT_DIR}/manage.py makemigrations --dry-run --check

.PHONY: test_mypy
test_mypy: ## run mypy type checks
	${VENV_MYPY} --version
	@sh -c 'mkdir -p ${ARTIFACTS_DIR}/mypy/pdf_gen_poc'
	${VENV_MYPY} -p pdf_gen_poc

.PHONY: test
test: test_flake8 test_black test_isort test_mypy test_python test_makemigrations ## run all tests


##################
# Project specific
##################

# If the first argument is "django"...
ifeq (django,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "django"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

.PHONY: django
django: ## run django management command
	DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
	${VENV_DJANGO} ${RUN_ARGS}
