# Breedbase Client

## Introduction

This is a GitHub repository for Breedbase client tools. Currently supports **SweetPotatoBase**, with the goal of supporting all BrAPI-compliant databases.

**Features:**
- **Python Client**: A robust Python client for calling Breedbase that handles pagination automatically
- **FastMCP Implementation**: Simple FastMCP implementation with tool uses that can call Breedbase and save data locally as CSV or JSON

## Setup

### Development Setup with UV

This project uses [UV](https://github.com/astral-sh/uv) for simple setup and dependency management:

```bash
# Install dependencies
uv sync

# Test the Server
!uv run mcp dev sweetpotatoquery.py
```

### Production Setup

Docker implementation is planned for production deployments (see To-Do list below).

## Project Structure

### Important Files

- [client.py](client.py) - Main client implementation
- [client dev.py](client%20dev.py) - Development version of the client
- [auths.py](auths.py) - Authentication handling for Breedbase endpoints
- [Helper.py](Helper.py) - Helper utilities
- [sweetpotatoquery.py](sweetpotatoquery.py) - SweetPotatoBase-specific queries
- [pyproject.toml](pyproject.toml) - Project dependencies and configuration
- [requirements.txt](requirements.txt) - Python package requirements
- [brapi_endpoints.csv](brapi_endpoints.csv) - BrAPI endpoint definitions

### Important Folders

- [brapi_v2/](brapi_v2/) - BrAPI v2 implementation
  - [model.py](brapi_v2/model.py) - Data models
  - [manual.py](brapi_v2/manual.py) - Manual endpoint implementations
  - [brapi_generated.json](brapi_v2/brapi_generated.json) - Generated BrAPI schema
- [Data/](Data/) - Local data storage directory
- [.brapi_temp/](.brapi_temp/) - Temporary BrAPI cache

### Configuration Files

- [README_AUTH.md](README_AUTH.md) - Authentication documentation
- [.gitignore](.gitignore) - Git ignore rules

## To-Do List

### Completed ✅

- [x] Build basic Python clients
- [x] Authentication for SOL Genomics endpoints
- [x] Basic GET endpoints
- [x] GET endpoints with DBID
- [x] Get information for agent about specific endpoints
- [x] Get information for all endpoints

### In Progress / Not Done ⏳

- [ ] Debate General vs. Specific Tools Calls
- [ ] Implement tracking/logging with ctx
- [ ] GET endpoints for filtering/searching
- [ ] Database-specific resources
- [ ] Allow user input for client auth
- [ ] Authentication for other selected endpoints
- [ ] Write validation script
- [ ] Docker implementation
- [ ] MCP registry
- [ ] Write and publish arXiv whitepaper


## Contributing

This project is under active development. Contributions and feedback are welcome!

## License

[Add your license information here]
