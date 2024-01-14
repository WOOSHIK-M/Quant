SHELL := /bin/bash


all: init format lint

check: format lint

init:
	ls

format:
	poetry run black .
	poetry run isort . --skip-gitignore --profile black

format-check:
	poetry run black . --check
	poetry run isort . --skip-gitignore --profile black --check

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
