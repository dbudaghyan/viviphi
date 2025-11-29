# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Python Execution
- Use `uv run python ...` to run Python scripts
- Use `uv run pytest ...` to run tests

### Code Quality
- Use `ruff check` for linting and code inspection
- Use `ruff format` for code formatting

### Package Management
- Use `uv add` to install/add packages
- Use `uv add --dev` for adding dev packages
- Always use `uv sync --no-install-project` instead of `uv sync`

## Code Guidelines

### Design Philosophy
- Beautiful is better than ugly
- Explicit is better than implicit
- Simple is better than complex
- Complex is better than complicated
- Flat is better than nested
- Readability counts

### Code Style
- Always include type annotations
- Write modular, focused functions
- Avoid deeply nested or overly complex functions
- Use Pydantic for all data models
- Always use logger instead of print statements

### Library Preferences
- Use `loguru` for logging
- Use `litellm` for LLM interactions
- Use `jinja2` for creating/rendering prompts for LLMs
- Use `uvicorn`/`fastapi` for creating APIs
- Use `pytest` for testing

### Testing Guidelines
- When writing tests, make sure they are meaningful, i.e. the actual code is being tested and not the mocks
- When writing temporary files for testing, do it in the temp directory
- When writing temporary outputs, put them in a separate folder
- When writing permanent tests, do it in the tests folder

## Project Overview

This is a Python project called "viviphi" that turns static graphs into beautiful animations.
The project uses Python 3.14+ and is structured as a standard Python package with the core package in the `viviphi/` directory.