# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BrAPI MCP Server provides LLM access to BrAPI v2-compatible plant breeding databases. It has two MCP server implementations:

1. **Main Server** (`src/main.py`) - Full-featured, dual-mode (STDIO/HTTP) server with 10 tools for searching, downloading, and managing breeding data
2. **PSA Server** (`src/psa/main.py`) - Simplified server for Parental Selection Agent workflows with 12 purpose-built tools

## Commands

```bash
# Install dependencies
uv sync

# Run main server (STDIO mode - default)
uv run src/main.py

# Run PSA server
BRAPI_BASE_URL=https://sweetpotatobase.org/brapi/v2 PYTHONPATH=src uv run python -m psa.main

# Run HTTP server via Docker
docker compose up -d

# Run tests
pytest tests/mcp.py

# Update test snapshots
pytest tests/mcp.py --inline-snapshot=fix,create

# Format code
ruff format .

# Lint code
ruff check .
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BASE_URL` | BrAPI server URL (required for main server) |
| `BRAPI_BASE_URL` | BrAPI server URL (required for PSA server) |
| `MODE` | `stdio` (default) or `http` |
| `PORT` | HTTP port (default: 8000) |
| `NAME` | Server identifier for logs/cache folders |
| `AUTH_TYPE` / `BRAPI_AUTH_TYPE` | `sgn`, `oauth`, or none |
| `BRAPI_USERNAME` / `BRAPI_PASSWORD` | Auth credentials |
| `DOWNLOAD_DIR_OVERRIDE` | Custom path for downloads (STDIO only) |

## Architecture

### Main Server (`src/`)

```
src/
├── main.py                    # Entry point - runs HTTP as daemon thread, MCP on main
├── config/
│   ├── type.py               # BrapiServerConfig dataclass with derived paths
│   └── value.py              # Environment-based config instantiation
├── client/
│   ├── client.py             # BrapiClient with auth handling and auto token refresh
│   ├── helpers.py            # Paginated fetch utilities
│   ├── auth/                 # SGN OAuth2 and basic auth implementations
│   └── capabilities/         # Server introspection and LLM-friendly descriptions
├── mcp_server/
│   ├── mcp_server.py         # FastMCP server factory and tool registration
│   ├── http_server.py        # FastAPI wrapper with download endpoints
│   ├── session/              # SessionManager for result persistence
│   └── tools/                # Tool implementations by category
└── utils/
    └── logger.py             # Rotating file logger
```

### PSA Server (`src/psa/`)

Simplified alternative with cleaner tool set:
- `tools/discovery.py` - list_programs, list_locations, list_seasons, search_trials
- `tools/studies.py` - search_studies, get_study_details
- `tools/observations.py` - get_observations, get_observation_variables, download_study
- `tools/germplasm.py` - search_germplasm, get_germplasm_by_id, get_pedigree

### Key Patterns

**Tool Registration**: Each tool module has a `register_*_tools(server, client, config)` function using `@server.tool()` decorator

**Authentication**: Factory pattern - `create_sgn_session()` for OAuth2, `create_base_session()` for public access. SGN auth auto-refreshes on `InvalidTokenError`

**Session Persistence**: Results cached in `cache/{name}/sessions/` as JSON+CSV with 30-day rotation

**Capability Discovery**: `CapabilitiesBuilder` reads `/serverinfo` + `client/data/metadata.csv` to generate LLM-friendly endpoint descriptions

## Code Style

- Ruff: single quotes, 120 char lines, 2-space indent
- Python 3.11+ with type hints
- Async-first for FastMCP tools

## Testing

Tests use pytest-asyncio with FastMCP's async client transport. Test file: `tests/mcp.py`
