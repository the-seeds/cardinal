.PHONY: quality style

check_dirs := src

quality:
    black --check $(check_dirs)
    ruff $(check_dirs)

style:
    black $(check_dirs)
    ruff $(check_dirs) --fix
