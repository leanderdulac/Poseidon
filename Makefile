# Poseidon — portões de qualidade determinísticos (sem LLM no laço).
.PHONY: install-dev test coverage lint typecheck complexity security mutate quality

PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip

install-dev:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest

coverage:
	mkdir -p reports
	$(PYTHON) -m pytest --cov=poseidon --cov-report=term-missing --cov-report=xml:reports/coverage.xml --cov-report=json:reports/coverage.json

lint:
	$(PYTHON) -m ruff check src tests

typecheck:
	$(PYTHON) -m mypy src/poseidon

complexity:
	$(PYTHON) -m xenon --max-absolute B --max-modules A --max-average A src/poseidon

security:
	mkdir -p reports
	$(PYTHON) -m bandit -r src/poseidon -ll -f txt -o reports/bandit.txt
	$(PYTHON) -m bandit -r src/poseidon -ll

# Mutação só nos caminhos críticos. Completa é lenta — ver docs/agents/03.
mutate:
	bash scripts/mutate.sh

quality:
	bash scripts/quality.sh
