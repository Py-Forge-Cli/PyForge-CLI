# CortexPy CLI - Makefile for development and deployment

# Variables
PYTHON := python
UV := uv
PACKAGE_NAME := cortexpy-cli
SRC_DIR := src
TEST_DIR := tests
DIST_DIR := dist

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

.PHONY: help install install-dev clean test lint format type-check build publish publish-test dev setup-dev pre-commit docs all

help: ## Show this help message
	@echo "$(BLUE)CortexPy CLI - Available commands:$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Development Setup
setup-dev: ## Set up development environment with uv
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	$(UV) venv
	$(UV) pip install -e ".[dev]"
	@echo "$(GREEN)Development environment ready!$(RESET)"

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
test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(RESET)"
	$(UV) run pytest -v
	@echo "$(GREEN)Tests completed!$(RESET)"

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(UV) run pytest -v --cov=$(PACKAGE_NAME) --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)Coverage report generated in htmlcov/$(RESET)"

# Pre-commit
pre-commit: ## Run all pre-commit checks
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
	@$(PYTHON) -c "from src.cortexpy_cli import __version__; print(f'Current version: {__version__}')"

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
	@echo "$(YELLOW)You can now use: cortexpy --help$(RESET)"

run-example: ## Run example conversion (requires sample PDF)
	@echo "$(BLUE)Running example conversion...$(RESET)"
	@if [ -f "example.pdf" ]; then \
		$(UV) run cortexpy convert example.pdf --verbose; \
	else \
		echo "$(YELLOW)No example.pdf found. Create one to test the conversion.$(RESET)"; \
	fi

# Documentation
docs: ## Generate documentation
	@echo "$(BLUE)Documentation available in docs/ directory$(RESET)"
	@echo "$(GREEN)✓ docs/USAGE.md - Complete usage guide$(RESET)"
	@echo "$(GREEN)✓ README.md - Project overview$(RESET)"
	@echo "$(YELLOW)Use 'cortexpy COMMAND --help' for detailed command help$(RESET)"

# CI/CD helpers
ci-install: ## Install dependencies for CI
	$(UV) pip install -e ".[dev]"

ci-test: ## Run tests for CI
	$(UV) run pytest -v --cov=$(PACKAGE_NAME) --cov-report=xml

ci-lint: ## Run linting for CI
	$(UV) run ruff check $(SRC_DIR) $(TEST_DIR)
	$(UV) run black --check $(SRC_DIR) $(TEST_DIR)
	$(UV) run mypy $(SRC_DIR)

# Utility commands
version: ## Show current version
	@$(PYTHON) -c "from src.cortexpy_cli import __version__; print(__version__)"

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