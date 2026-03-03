# Makefile for Javis

.PHONY: help install dev test clean lint format

help:
	@echo "Javis - AI Assistant Library"
	@echo ""
	@echo "Available targets:"
	@echo "  install    - Install package"
	@echo "  dev        - Install in editable mode with dev dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting (mypy, flake8)"
	@echo "  format     - Format code with black"
	@echo "  clean      - Clean build artifacts"
	@echo "  example    - Run basic example"

install:
	pip install .

dev:
	pip install -e ".[dev,web,browser,vision,tts]"

test:
	pytest tests/ -v

lint:
	mypy javis/
	flake8 javis/

format:
	black javis/ examples/
	isort javis/ examples/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf javis/__pycache__/
	rm -rf javis/**/*.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

example:
	python -c "from javis import Javis; j=Javis(); print(j.info())"
