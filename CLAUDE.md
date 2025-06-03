# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Discord bot template built with py-cord that provides a production-ready foundation for Discord bots. The project uses a modular architecture with automatic cog loading, database integration via SQLAlchemy, Redis support, and comprehensive Docker deployment.

## Development Commands

### Environment Setup
- `make dev:setup` - Install all dependencies using uv (discord, db, dev groups)
- `make envs:setup` - Copy environment file templates from envs/ directory

### Code Quality
- `make lint` - Run Ruff linter to check code quality
- `make lint:fix` - Run Ruff with automatic fixes
- `make format` - Format code using Ruff formatter

### Docker Operations
- `make up` - Build and start all containers in detached mode
- `make down` - Stop all containers
- `make reload` - Rebuild and restart containers
- `make logs` - Follow container logs
- `make ps` - Show running containers

### Database Management
- `make db:revision:create NAME="description"` - Create new Alembic migration
- `make db:migrate` - Apply migrations to database
- `make db:current` - Show current migration revision
- `make db:history` - Show migration history

### Security Scanning
- `make security:scan` - Run all security scans (Bandit + Semgrep)
- `make security:scan:code` - Run Bandit static analysis
- `make security:scan:sast` - Run Semgrep security analysis

## Architecture

### Core Components
- **main.py**: Bot entry point with automatic cog loading from `/app/cogs/` (excludes `template.py`)
- **core/config.py**: Centralized settings using Pydantic with environment-based configuration
- **cogs/**: Discord command modules loaded automatically at startup
- **db/**: Database layer with SQLAlchemy models, schemas, and CRUD operations

### Configuration System
The bot uses a Pydantic-based configuration system (`core/config.py`) that supports:
- Environment-specific settings (development/production/test via `ENV_MODE`)
- Database connection management (PostgreSQL)
- Redis integration
- Sentry error tracking
- Security headers and CSP policies

### Database Architecture
- **models/base.py**: Provides `BaseModel` with auto-incrementing ID and `TimeStampMixin` for created_at/updated_at
- **models/**: SQLAlchemy model definitions inheriting from `BaseModel`
- **schemas/**: Pydantic schemas for data validation
- **crud/**: Database operation layer with base CRUD operations

### Cog System
- Cogs are automatically discovered and loaded from `/app/cogs/` except `template.py`
- **cog_manager.py**: Provides runtime cog management with `/reload`, `/load`, `/unload` commands
- **health_monitor.py**: System monitoring functionality
- **admin.py**: Administrative commands

### Docker Configuration
The project uses multi-profile Docker Compose setup:
- **app**: Main Discord bot service
- **db**: PostgreSQL database with health checks
- **redis**: Redis cache/session store
- **db-migrator**: Alembic migration runner
- **adminer**: Database management interface (dev only)
- **db-dumper**: Database backup utilities

Environment variables control which services are included via `INCLUDE_DB` and `INCLUDE_REDIS` flags.

## Development Workflow

1. Use `make envs:setup` to create environment files from templates
2. Configure database and Discord bot tokens in respective env files
3. Use `make dev:setup` to install dependencies
4. Run `make up INCLUDE_DB=true` to start with database
5. Apply database migrations with `make db:migrate`
6. Use `make lint` and `make format` before committing

## Key Files

- `app/main.py:26-40` - Automatic cog loading logic
- `app/core/config.py:78-83` - Settings factory with caching
- `app/db/models/base.py:23-31` - Base model with timestamp mixin
- `Makefile:55-82` - Docker service management
- `compose.yml:46-65` - Database service configuration

## Testing

The project includes security scanning but no explicit test framework is configured. When adding tests, check the project structure and add appropriate test dependencies to the `dev` group in `pyproject.toml`.