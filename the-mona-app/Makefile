VENV?=.venv
PY=python3

setup:
	$(PY) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -U pip && pip install -r requirements.txt

run:
	. $(VENV)/bin/activate && python -m apps.main

web:
	. $(VENV)/bin/activate && uvicorn mona.web.api:app --host 0.0.0.0 --port 8080 --reload

lint:
	. $(VENV)/bin/activate && echo "add ruff/black later"

test:
	. $(VENV)/bin/activate && pytest -q || true
