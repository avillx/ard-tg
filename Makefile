SHELL := /bin/bash

.PHONY: help
help: ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


.PHONY: apigen
apigen: ## Regenerate api bindings from openapi file "./agent-api.yml"
	@openapi-python-client generate --path ./agent-api.yml --meta none --output-path ./src/ard --overwrite


.PHONY: lint
lint: ## Format with ruff and lint with pyright
	@echo "=> Running format and lint"
	@ruff format
	@basedpyright
	@echo "=> Format and lints complete"


.PHONY: test
test: ## Run tests
	@echo "=> Running test cases"
	@pytest tests
	@echo "=> Tests complete"


.PHONY: clean
clean: ## Cleanup temporary build artifacts
	@echo "=> Cleaning working directory"
	@rm -rf .pytest_cache .ruff_cache .hypothesis build/ -rf dist/ .eggs/
	@find . -name '*.egg-info' -exec rm -rf {} +
	@find . -type f -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name '.ipynb_checkpoints' -exec rm -rf {} +
	@rm -rf .coverage coverage.xml coverage.json htmlcov/ .pytest_cache tests/.pytest_cache tests/**/.pytest_cache .mypy_cache
