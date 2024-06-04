.PHONY: quality style test

check_dirs := src example

quality:
	ruff $(check_dirs)
	ruff format --check $(check_dirs)

style:
	ruff $(check_dirs) --fix
	ruff format $(check_dirs)

test:
	python -m pytest tests/