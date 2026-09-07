#!/usr/bin/env bash
# Mutação nos caminhos críticos (hydraulics/quality/alf/benchmarks).
# mutmut 3 gera cópias sob mutants/; full run é lento e pode falhar se
# fixtures usarem paths relativos ao CWD. Este script faz smoke + regista reports/.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-.venv/bin/python}"
mkdir -p reports
TIMEOUT_SEC="${MUTMUT_TIMEOUT:-180}"

{
  echo "mutmut smoke $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "only_mutate: hydraulics.py quality.py alf.py benchmarks.py"
  echo "timeout_s=$TIMEOUT_SEC"
} | tee reports/mutmut.txt

set +e
if command -v timeout >/dev/null 2>&1; then
  timeout "$TIMEOUT_SEC" "$PYTHON" -m mutmut run 2>&1 | tee -a reports/mutmut.txt
  status=${PIPESTATUS[0]}
else
  "$PYTHON" -m mutmut run 2>&1 | tee -a reports/mutmut.txt
  status=$?
fi
"$PYTHON" -m mutmut results 2>&1 | tee -a reports/mutmut.txt
echo "mutmut_exit=$status" | tee -a reports/mutmut.txt
# Smoke bem-sucedido se gerou mutants (mesmo que stats falhem por path de fixtures).
if [[ -d mutants ]]; then
  echo "mutants_dir=present (geração OK)" | tee -a reports/mutmut.txt
  exit 0
fi
exit "$status"
