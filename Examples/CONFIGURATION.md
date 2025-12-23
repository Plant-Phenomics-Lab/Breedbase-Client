# Configuration Guide

The BrAPI MCP Server is highly configurable to suit different deployment needs (Local, Docker, Cloud). Configuration is primarily handled via **Environment Variables**.

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BASE_URL` | The URL of the BrAPI endpoint to connect to. | `https://sweetpotatobase.org/brapi/v2` | Yes |
| `MODE` | Operation mode: `stdio` (local) or `http` (server). | `stdio` | No |
| `PORT` | The port for the HTTP server (used in HTTP mode or for health checks). | `8000` | No |
| `NAME` | A friendly name for the server instance (used for logging/folders). | `BrAPI_Server` | No |
| `AUTH_TYPE` | Authentication type: `brapi` (token), `oauth`, or `none`. | `None` | No |
| `BRAPI_USERNAME` | Username for authentication. | `None` | Yes (if auth needed) |
| `BRAPI_PASSWORD` | Password for authentication. | `None` | Yes (if auth needed) |
| `DOWNLOAD_DIR_OVERRIDE` | **STDIO Mode Only**. Absolute path to save downloaded files. | `None` | No |

---

## Configuration Methods

- Each MCP Instance can connect to one BrAPI server at a time, but you can run multiple servers on the same machine if you change the `PORT` variable. 

### 1. Using a `.env` File (Recommended for Local)

Create a `.env` file in the root of the project. See `env.example` for examples. 

```bash
BASE_URL=https://sweetpotatobase.org
MODE=stdio
BRAPI_USERNAME=myuser
BRAPI_PASSWORD=mypassword
DOWNLOAD_DIR_OVERRIDE=C:/Users/Me/Downloads/BrapiData
```

### 2. MCP Client Configuration (VS Code / Claude Desktop)

You can pass environment variables directly in your MCP client configuration file (e.g., `claude_desktop_config.json` or VS Code settings).

**VS Code / Claude Desktop Example:**

```json
{
  "mcpServers": {
    "sweetpotatobase": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/Breedbase-Client",
        "src/main.py"
      ],
      "env": {
        "BASE_URL": "https://sweetpotatobase.org",
        "MODE": "stdio",
        "BRAPI_USERNAME": "your_username",
        "BRAPI_PASSWORD": "your_password"
      }
    }
  }
}
```

### 3. Docker 

For HTTP You need to run the server and then connect your server to the MCP client. Thus: 

```bash
# Run the Sever, assume you're in the Breedbase-Client folder. 
docker compose up -d
```

Then connect the server. Remember to use the port you configured. 

```json
{
  "mcpServers": {
    "brapiserver": {
			"url": "http://127.0.0.1:8000/mcp",
			"type": "http"
		}
  }
}
```

*
## Running Multiple Servers at Once

- It is possible to run two different MCP servers for different BrAPI compatible databases at the same time using different ports. Example here (with STDIO). HTTP + Docker is best suited for this. 

### Docker (HTTP)

1. Use different .env files. 

    ```bash
    # save as env.yambase
    MODE=http
    PORT=8001
    NAME=yambase
    BASE_URL=https://yambase.org/brapi/v2
    AUTH_TYPE=SGN
    BRAPI_USERNAME=myuser
    BRAPI_PASSWORD=mypassword
    ```

2. Start SweetPotatoBase:
    ```bash
    docker compose --env-file .env.sweetpotato -p sweetpotato up -d
    ```

    Start Yambase:
    ```bash
    docker compose --env-file .env.yambase -p yambase up -d
    ```

    *   `--env-file`: Tells Docker which config file to use.
    *   `-p`: Sets a "Project Name" so the containers don't overwrite each other.

3.  Connect MCP Client. 

```json
"sweepotatobase": {
			"url": "http://127.0.0.1:8000.mcp",
			"type": "http"
		},
"yambase": {
			"url": "http://127.0.0.1:8001.mcp",
			"type": "http"
		}
```

### STDIO (Local)

You can use the env option in the json config. 

```json
"sweetpotatobase.stdio": {
			"command": "C:\\Users\\yujer\\.local\\bin\\uv.exe",
			"args": [
    			"run",
   	 			"--directory",
    			"C:\\Users\\yujer\\L_Documents\\Current Classes\\Breedbase-Client-refactor",
    			"src/main.py"
  			],
  			"env": {
    			"MODE": "stdio",
    			"NAME": "sweetpotatobase",
    			"BASE_URL": "https://sweetpotatobase.org/brapi/v2",
    			"PORT": "8002",
    			"AUTH_TYPE": "sgn",
    			"BRAPI_USERNAME": "username",
				"BRAPI_PASSWORD": "password"
  			}},
		
		"yambase.stdio": {
  			"command": "C:\\Users\\yujer\\.local\\bin\\uv.exe",
  			"args": [
    			"run",
    			"--directory",
    			"C:\\Users\\yujer\\L_Documents\\Current Classes\\Breedbase-Client-refactor",
    			"src/main.py"
  			],
  			"env": {
    			"MODE": "stdio",
    			"NAME": "yambase",
    			"BASE_URL": "https://yambase.org/brapi/v2",
    			"PORT": "8001",
    			"AUTH_TYPE": "sgn",
    			"BRAPI_USERNAME": "username2",
				"BRAPI_PASSWORD": "password2"
  			}
		}
```
