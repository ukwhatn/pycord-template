# Pycord Template Development Guidelines

## Build/Test Commands
- `make lint` - Check code with ruff
- `make lint:fix` - Fix linting issues automatically
- `make format` - Format code with ruff format
- `make security:scan` - Run security scans (bandit + semgrep)
- `make up` - Start dev environment
- `make down` - Stop dev environment
- `make logs` - Show container logs
- `make ps` - Show container status
- `make db:migrate` - Run database migrations
- `make db:revision:create NAME="migration name"` - Create new migration

## Code Style
- **Imports**: Group imports (stdlib, third-party, local) with blank lines between groups
- **Formatting**: Uses ruff formatter (similar to black)
- **Types**: Use typing annotations for all function parameters and return values
- **Docstrings**: Use """triple quotes""" for docstrings, describing purpose
- **Naming**:
  - Classes: `PascalCase`
  - Functions/Variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- **Error Handling**: Use specific exceptions, handle appropriately
- **Logging**: Use standard library's logging module, not print statements
- **Architecture**: Follow the cogs pattern for Discord commands

## Environment
- Uses Poetry for dependency management
- Docker-based development environment
- CI runs ruff, security scans, and health checks