# Web Scraper API (FastAPI + PostgreSQL + Docker)

A small, production-style web scraper API built with **FastAPI**, **SQLAlchemy**, **Alembic**, and **PostgreSQL**, containerized with **Docker**.

Users can register/login, trigger a scraper (example: books), and fetch their own items via a REST API.  
Data isolation is enforced: every scraped item is tied to its **owner** (`owner_id`) and a unique constraint prevents duplicates per user.

---

## Features

- **Auth**: Register / Login (OAuth2 Password flow with JWT).
- **Scraper**: Ingests items (e.g., books) and stores them in Postgres.
- **Per-user data**: `owner_id` FK + unique constraint on `(owner_id, url)`.
- **API**:
  - `POST /auth/register`
  - `POST /scrape`
  - `GET /items`
  - `GET /items/{id}`
  - `DELETE /items/{id}`
- **Migrations**: Alembic for schema versioning.
- **Docker**: One command to run web + database.
- **Logging**: Request + scraper logs to console.

---

## Tech Stack

- Python, FastAPI, Uvicorn
- SQLAlchemy + Alembic
- PostgreSQL
- Docker & Docker Compose

---

## Quickstart

```bash
# 1) copy env and fill it
cp .env.example .env

# 2) build & run
docker compose up -d --build

# 3) run DB migrations
docker compose exec web alembic upgrade head

# 4) open docs
open http://localhost:8000/docs
