SHELL := /bin/bash


all: init format lint

check: format lint

init:
	@command -v pdm >/dev/null 2>&1 || (echo "PDM not installed. Installing..." && pip install pdm && echo "PDM is installed!")
	pdm install
	pdm run pre-commit install

format:
	pdm run black .
	pdm run isort . --skip-gitignore --profile black

format-check:
	pdm run black . --check
	pdm run isort . --skip-gitignore --profile black --check

lint:
	pdm run pyright src
	pdm run ruf src --fix

tree:
	tree -I "*data|.pkl|*.png|*.txt|$(shell cat .gitignore | tr -s '\n' '|' )"


help:
	@echo "Usage: make [target]"
	@echo
	@echo "Available targets:"
	@echo "  init:"
	@echo "    Initialize poetry project"
	@echo "  format:"
	@echo "    Format the code"
	@echo "  tree:"
	@echo "    Show the directory tree"
	@echo
	@echo "  help:"
	@echo "    Show this help message"
