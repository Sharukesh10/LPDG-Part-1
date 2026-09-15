PYTHON ?= python3

.PHONY: all run test clean

all: run

run:
	$(PYTHON) -m gateway_priority.pipeline --data data --out predictions.csv
	$(PYTHON) validate_submission.py predictions.csv

test:
	$(PYTHON) -m pytest

clean:
	rm -f predictions.csv
	rm -rf .pytest_cache __pycache__ src/gateway_priority/__pycache__ tests/__pycache__
