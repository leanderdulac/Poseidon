#!/usr/bin/env bash
# Portões rápidos de qualidade determinística. Sai ≠0 se algum falhar.
# Sem LLM no laço. Artefactos sob reports/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$(command -v python3)"
fi
mkdir -p reports

echo "==> lint (ruff)"
"$PYTHON" -m ruff check src tests

echo "==> typecheck (mypy)"
"$PYTHON" -m mypy src/poseidon

echo "==> complexity (xenon)"
"$PYTHON" -m xenon --max-absolute B --max-modules A --max-average A src/poseidon

echo "==> security (bandit)"
"$PYTHON" -m bandit -r src/poseidon -ll -f txt -o reports/bandit.txt
"$PYTHON" -m bandit -r src/poseidon -ll

echo "==> coverage (pytest --cov, fail_under via pyproject)"
"$PYTHON" -m pytest --cov=poseidon \
  --cov-report=term-missing \
  --cov-report=xml:reports/coverage.xml \
  --cov-report=json:reports/coverage.json

echo "OK: todos os portões rápidos verdes."
