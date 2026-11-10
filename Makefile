PYTHON = .venv/bin/python3
MAIN = main.py
ARGS =
 
install:
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install pydantic flake8 mypy
 
run:
	$(PYTHON) $(MAIN) $(ARGS)
 
debug:
	$(PYTHON) -m pdb $(MAIN) $(ARGS)
 
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

fclean: clean
	rm -rf .venv

lint:
	$(PYTHON) -m flake8 . --exclude .venv
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 . --exclude .venv
	$(PYTHON) -m mypy . --strict --python-version 3.10

.PHONY: install run debug clean fclean lint lint-strict