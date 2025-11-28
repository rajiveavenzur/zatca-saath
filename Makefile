.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate shell

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies with Poetry
	poetry install

dev:  ## Run development server with hot reload
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests with pytest
	poetry run pytest tests/ -v --cov=app --cov-report=html

lint:  ## Run linting with ruff
	poetry run ruff check app/ tests/

format:  ## Format code with black
	poetry run black app/ tests/

clean:  ## Clean cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true

docker-build:  ## Build Docker image
	docker-compose build

docker-up:  ## Start Docker containers
	docker-compose up -d

docker-down:  ## Stop Docker containers
	docker-compose down

docker-logs:  ## Show Docker logs
	docker-compose logs -f app

migrate:  ## Run database migrations
	poetry run alembic upgrade head

migration:  ## Create a new migration (usage: make migration msg="description")
	poetry run alembic revision --autogenerate -m "$(msg)"

shell:  ## Open Python shell with app context
	poetry run python

db-shell:  ## Connect to PostgreSQL database
	docker-compose exec db psql -U zatca -d zatca_invoice
