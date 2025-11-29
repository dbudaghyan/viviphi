# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Python Execution
- Use `uv run python ...` to run Python scripts
- Use `uv run pytest ...` to run tests

### Code Quality
- Use `ruff check` for linting and code inspection
- Use `ruff format` for code formatting

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

## Project Overview

This is a Python project called "viviphi" that turns static graphs into beautiful animations.
The project uses Python 3.14+ and is structured as a standard Python package with the core package in the `viviphi/` directory.
