# PyForge CLI - Makefile for development and deployment

# Variables
# Use Python 3.10 for Databricks compatibility
PYTHON := python3.10
UV := uv
PACKAGE_NAME := pyforge-cli
SRC_DIR := src
TEST_DIR := tests
DIST_DIR := dist
DOCS_DIR := docs
VENV_NAME := .venv
VENV_BIN := $(VENV_NAME)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

.PHONY: help install install-dev clean test lint format type-check build publish publish-test dev setup-dev pre-commit docs docs-install docs-serve docs-build docs-deploy docs-clean all venv venv-clean venv-activate test-env test-quick test-all test-report

help: ## Show this help message
	@echo "$(BLUE)PyForge CLI - Available commands:$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Virtual Environment Management
venv: ## Create virtual environment using Python 3.10 for Databricks compatibility
	@echo "$(BLUE)Creating virtual environment...$(RESET)"
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "$(YELLOW)Virtual environment already exists. Use 'make venv-clean' to recreate.$(RESET)"; \
	else \
		if command -v python3.10 >/dev/null 2>&1; then \
			echo "$(GREEN)Using Python 3.10 for Databricks Serverless V1 compatibility$(RESET)"; \
			python3.10 -m venv $(VENV_NAME); \
		else \
			echo "$(RED)ERROR: Python 3.10 is required for Databricks compatibility$(RESET)"; \
			echo "$(YELLOW)Please install Python 3.10 and try again$(RESET)"; \
			exit 1; \
		fi; \
		$(VENV_PIP) install --upgrade pip setuptools wheel; \
		echo "$(GREEN)Virtual environment created with Python 3.10!$(RESET)"; \
		echo "$(YELLOW)Activate with: source $(VENV_NAME)/bin/activate$(RESET)"; \
	fi

venv-clean: ## Remove virtual environment
	@echo "$(BLUE)Removing virtual environment...$(RESET)"
	@rm -rf $(VENV_NAME)
	@echo "$(GREEN)Virtual environment removed!$(RESET)"

venv-activate: ## Show activation command
	@echo "$(YELLOW)To activate the virtual environment, run:$(RESET)"
	@echo "$(GREEN)source $(VENV_NAME)/bin/activate$(RESET)"
	@echo ""
	@echo "$(YELLOW)To deactivate, run:$(RESET)"
	@echo "$(GREEN)deactivate$(RESET)"

# Development Setup
setup-dev: venv ## Set up complete development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	@$(VENV_PIP) install -e ".[dev,test,all]"
	@if [ -f requirements-dev.txt ]; then \
		$(VENV_PIP) install -r requirements-dev.txt; \
	fi
	@echo "$(GREEN)Development environment ready!$(RESET)"
	@echo "$(YELLOW)Activate with: source $(VENV_NAME)/bin/activate$(RESET)"

test-env: ## Create dedicated test environment
	@echo "$(BLUE)Creating test environment...$(RESET)"
	@if [ -d ".testenv" ]; then \
		echo "$(YELLOW)Test environment already exists. Removing...$(RESET)"; \
		rm -rf .testenv; \
	fi
	@if command -v python3.10 >/dev/null 2>&1; then \
		echo "$(GREEN)Using Python 3.10 for compatibility with PyArrow 8.0.0$(RESET)"; \
		python3.10 -m venv .testenv; \
	else \
		echo "$(YELLOW)Python 3.10 not found, using default Python$(RESET)"; \
		$(PYTHON) -m venv .testenv; \
	fi
	@.testenv/bin/pip install --upgrade pip
	@.testenv/bin/pip install -e ".[dev,test,databricks]"
	@.testenv/bin/pip install pytest-html pytest-json-report
	@echo "$(GREEN)Test environment created!$(RESET)"
	@echo "$(YELLOW)Run tests with: make test-all$(RESET)"

install: ## Install package dependencies
	@echo "$(BLUE)Installing package dependencies...$(RESET)"
	$(UV) pip install -e .
	@echo "$(GREEN)Package installed successfully!$(RESET)"

install-dev: ## Install package with development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(UV) pip install -e ".[dev]"
	@echo "$(GREEN)Development dependencies installed!$(RESET)"

# Code Quality
lint: ## Run linting with ruff
	@echo "$(BLUE)Running linter...$(RESET)"
	$(UV) run ruff check $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)Linting completed!$(RESET)"

format: ## Format code with black and ruff
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(UV) run black $(SRC_DIR) $(TEST_DIR)
	$(UV) run ruff check --fix $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)Code formatted!$(RESET)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checker...$(RESET)"
	$(UV) run mypy $(SRC_DIR)
	@echo "$(GREEN)Type checking completed!$(RESET)"

# Testing
test: ## Run tests with pytest in virtual environment (includes PySpark tests)
	@echo "$(BLUE)Running tests...$(RESET)"
	@if [ -d "$(VENV_NAME)" ] && [ -f "$(VENV_BIN)/pytest" ]; then \
		$(VENV_BIN)/pytest -v --run-pyspark; \
	else \
		echo "$(RED)Virtual environment not found. Run 'make setup-dev' first.$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Tests completed!$(RESET)"

test-quick: ## Run quick tests (exclude slow and integration tests)
	@echo "$(BLUE)Running quick tests...$(RESET)"
	@if [ -d "$(VENV_NAME)" ] && [ -f "$(VENV_BIN)/pytest" ]; then \
		$(VENV_BIN)/pytest -v -k "not slow and not integration and not pyspark"; \
	else \
		echo "$(RED)Virtual environment not found. Run 'make setup-dev' first.$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Quick tests completed!$(RESET)"

test-all: ## Run all tests using test environment with full reporting (includes PySpark tests)
	@echo "$(BLUE)Running all tests with reporting...$(RESET)"
	@if [ -d ".testenv" ]; then \
		.testenv/bin/pytest tests/ \
			--run-pyspark \
			--junit-xml=junit/test-results.xml \
			--html=pytest_html_report.html \
			--self-contained-html \
			--json-report \
			--json-report-file=test-report.json \
			--cov=pyforge_cli \
			--cov-report=xml \
			--cov-report=html:htmlcov \
			--cov-report=term-missing \
			-v --tb=short; \
		echo "$(GREEN)Test reports generated:$(RESET)"; \
		echo "  - HTML: pytest_html_report.html"; \
		echo "  - XML: junit/test-results.xml"; \
		echo "  - JSON: test-report.json"; \
		echo "  - Coverage: htmlcov/index.html"; \
	else \
		echo "$(RED)Test environment not found. Run 'make test-env' first.$(RESET)"; \
		exit 1; \
	fi

test-cov: ## Run tests with coverage report (includes PySpark tests)
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	@if [ -d "$(VENV_NAME)" ] && [ -f "$(VENV_BIN)/pytest" ]; then \
		$(VENV_BIN)/pytest -v --cov=pyforge_cli --cov-report=html --cov-report=term-missing --run-pyspark; \
		echo "$(GREEN)Coverage report generated in htmlcov/$(RESET)"; \
	else \
		echo "$(RED)Virtual environment not found. Run 'make setup-dev' first.$(RESET)"; \
		exit 1; \
	fi

test-no-slow: ## Run all tests except slow ones (includes PySpark tests)
	@echo "$(BLUE)Running all tests except slow (including PySpark)...$(RESET)"
	@if [ -d "$(VENV_NAME)" ] && [ -f "$(VENV_BIN)/pytest" ]; then \
		$(VENV_BIN)/pytest -v -m "not slow" --run-pyspark; \
	else \
		echo "$(RED)Virtual environment not found. Run 'make setup-dev' first.$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Tests completed!$(RESET)"

test-no-databricks: ## Run all tests except databricks ones 
	@echo "$(BLUE)Running tests without Databricks tests...$(RESET)"
	@if [ -d "$(VENV_NAME)" ] && [ -f "$(VENV_BIN)/pytest" ]; then \
		$(VENV_BIN)/pytest -v -m "not databricks"; \
	else \
		echo "$(RED)Virtual environment not found. Run 'make setup-dev' first.$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Tests completed!$(RESET)"

test-no-databricks-cov: ## Run tests with coverage excluding databricks tests
	@echo "$(BLUE)Running tests with coverage (excluding Databricks)...$(RESET)"
	@if [ -d "$(VENV_NAME)" ] && [ -f "$(VENV_BIN)/pytest" ]; then \
		$(VENV_BIN)/pytest -v -m "not databricks" --cov=pyforge_cli --cov-report=html --cov-report=term-missing; \
		echo "$(GREEN)Coverage report generated in htmlcov/$(RESET)"; \
	else \
		echo "$(RED)Virtual environment not found. Run 'make setup-dev' first.$(RESET)"; \
		exit 1; \
	fi

test-report: test-all ## Generate test report summary
	@echo "$(BLUE)Test Report Summary:$(RESET)"
	@if [ -f "test-report.json" ]; then \
		python -c "import json; \
		with open('test-report.json', 'r') as f: \
			data = json.load(f); \
			summary = data.get('summary', {}); \
			print(f'Total Tests: {summary.get(\"total\", 0)}'); \
			print(f'Passed: {summary.get(\"passed\", 0)}'); \
			print(f'Failed: {summary.get(\"failed\", 0)}'); \
			print(f'Skipped: {summary.get(\"skipped\", 0)}'); \
			print(f'Duration: {data.get(\"duration\", 0):.2f} seconds')"; \
	else \
		echo "$(RED)No test report found. Run 'make test-all' first.$(RESET)"; \
	fi

# Pre-commit
pre-commit: ## Run all pre-commit checks (includes PySpark tests)
	@echo "$(BLUE)Running pre-commit checks...$(RESET)"
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	@echo "$(GREEN)All pre-commit checks passed!$(RESET)"

# Building
clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -rf $(DIST_DIR)/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)Cleanup completed!$(RESET)"

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(RESET)"
	$(UV) build
	@echo "$(GREEN)Build completed! Packages available in $(DIST_DIR)/$(RESET)"
	@ls -la $(DIST_DIR)/

# Publishing
check-version: ## Check if version is set correctly
	@echo "$(BLUE)Checking version...$(RESET)"
	@$(PYTHON) -c "from src.pyforge_cli import __version__; print(f'Current version: {__version__}')"

publish-test: build ## Publish to Test PyPI
	@echo "$(BLUE)Publishing to Test PyPI...$(RESET)"
	@echo "$(YELLOW)Make sure you have set up your Test PyPI credentials!$(RESET)"
	$(UV) publish --repository testpypi $(DIST_DIR)/*
	@echo "$(GREEN)Published to Test PyPI successfully!$(RESET)"
	@echo "$(YELLOW)Test installation with:$(RESET)"
	@echo "  pip install --index-url https://test.pypi.org/simple/ $(PACKAGE_NAME)"

publish: build ## Publish to PyPI (production)
	@echo "$(RED)WARNING: This will publish to production PyPI!$(RESET)"
	@echo "$(YELLOW)Make sure you have:$(RESET)"
	@echo "  1. Tested the package thoroughly"
	@echo "  2. Updated the version number"
	@echo "  3. Set up your PyPI credentials"
	@echo ""
	@read -p "Are you sure you want to continue? (y/N): " confirm && [ "$$confirm" = "y" ]
	@echo "$(BLUE)Publishing to PyPI...$(RESET)"
	$(UV) publish $(DIST_DIR)/*
	@echo "$(GREEN)Published to PyPI successfully!$(RESET)"
	@echo "$(YELLOW)Install with: pip install $(PACKAGE_NAME)$(RESET)"

# Development
dev: install-dev ## Install in development mode and run CLI
	@echo "$(BLUE)Package installed in development mode$(RESET)"
	@echo "$(YELLOW)You can now use: pyforge --help$(RESET)"

run-example: ## Run example conversion (requires sample PDF)
	@echo "$(BLUE)Running example conversion...$(RESET)"
	@if [ -f "example.pdf" ]; then \
		$(UV) run pyforge convert example.pdf --verbose; \
	else \
		echo "$(YELLOW)No example.pdf found. Create one to test the conversion.$(RESET)"; \
	fi

# Documentation
docs-install: ## Install documentation dependencies
	@echo "$(BLUE)Installing documentation dependencies...$(RESET)"
	@if command -v mkdocs >/dev/null 2>&1; then \
		echo "$(GREEN)✓ MkDocs already installed$(RESET)"; \
	else \
		echo "$(YELLOW)Installing MkDocs and dependencies...$(RESET)"; \
		$(PYTHON) -m pip install mkdocs==1.6.1 mkdocs-material==9.6.14 pymdown-extensions==10.15; \
	fi
	@echo "$(GREEN)Documentation dependencies ready!$(RESET)"

docs-serve: docs-install ## Serve documentation locally with live reload
	@echo "$(BLUE)Starting documentation server...$(RESET)"
	@echo "$(YELLOW)📖 Documentation will be available at: http://127.0.0.1:8000$(RESET)"
	@echo "$(YELLOW)📝 Files will auto-reload when you make changes$(RESET)"
	@echo "$(YELLOW)🛑 Press Ctrl+C to stop the server$(RESET)"
	@echo ""
	@if [ -f mkdocs.yml ]; then \
		mkdocs serve; \
	else \
		echo "$(RED)❌ mkdocs.yml not found in current directory$(RESET)"; \
		exit 1; \
	fi

docs-build: docs-install ## Build documentation static site
	@echo "$(BLUE)Building documentation...$(RESET)"
	@if [ -f mkdocs.yml ]; then \
		mkdocs build --clean --strict; \
		echo "$(GREEN)✓ Documentation built in site/ directory$(RESET)"; \
		echo "$(YELLOW)📁 Open site/index.html in your browser to view$(RESET)"; \
	else \
		echo "$(RED)❌ mkdocs.yml not found in current directory$(RESET)"; \
		exit 1; \
	fi

docs-deploy: docs-build ## Deploy documentation to GitHub Pages manually
	@echo "$(BLUE)Deploying documentation to GitHub Pages...$(RESET)"
	@echo "$(YELLOW)Installing ghp-import if needed...$(RESET)"
	@pip install --user ghp-import >/dev/null 2>&1 || echo "ghp-import already installed"
	@echo "$(YELLOW)🚀 Deploying to gh-pages branch...$(RESET)"
	@if command -v ghp-import >/dev/null 2>&1; then \
		ghp-import -n -p -f site; \
	else \
		/Users/sdandey/Library/Python/3.10/bin/ghp-import -n -p -f site; \
	fi
	@echo "$(GREEN)✅ Documentation deployed successfully!$(RESET)"
	@echo "$(GREEN)📖 Live site: https://py-forge-cli.github.io/PyForge-CLI/$(RESET)"
	@echo "$(YELLOW)Note: Automatic deployment also happens on every push to main$(RESET)"

docs-clean: ## Clean documentation build files
	@echo "$(BLUE)Cleaning documentation build files...$(RESET)"
	@rm -rf site/
	@echo "$(GREEN)✓ Documentation build files cleaned$(RESET)"

docs: docs-serve ## Alias for docs-serve (default docs command)

# CI/CD helpers
ci-install: ## Install dependencies for CI
	$(UV) pip install -e ".[dev]"

ci-test: ## Run tests for CI (includes PySpark tests)
	$(UV) run pytest -v --run-pyspark --cov=$(PACKAGE_NAME) --cov-report=xml

ci-lint: ## Run linting for CI
	$(UV) run ruff check $(SRC_DIR) $(TEST_DIR)
	$(UV) run black --check $(SRC_DIR) $(TEST_DIR)
	$(UV) run mypy $(SRC_DIR)

# Utility commands
version: ## Show current version
	@$(PYTHON) -c "from src.pyforge_cli import __version__; print(__version__)"

info: ## Show package info
	@echo "$(BLUE)Package Information:$(RESET)"
	@echo "Name: $(PACKAGE_NAME)"
	@echo "Source: $(SRC_DIR)"
	@echo "Tests: $(TEST_DIR)"
	@$(MAKE) version

all: pre-commit build ## Run all checks and build
	@echo "$(GREEN)All tasks completed successfully!$(RESET)"

# Default target
.DEFAULT_GOAL := help