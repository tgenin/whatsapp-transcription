.PHONY: test test-unit lint typecheck format run

test:
	uv run pytest

test-unit:
	uv run pytest tests/unit

lint:
	uv run ruff check .

typecheck:
	uv run mypy app

format:
	uv run ruff format .

run:
	uv run uvicorn app.main:app --reload
