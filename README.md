# BrAPI MCP Server

<div align="center">

**The BrAPI MCP Server provides LLMs with tools to search and retrieve data from BrAPI v2 Compatible Servers.**

</div>

# Tools Overview

# Examples

# Getting Started

- The server supports two modes: **STDIO** and **HTTP**.
  - **STDIO:** Best for personal use. The server runs directly on your machine, and files are saved to your local disk. It is easier to configure and more secure for single users.
  - **HTTP:** Under active development. Best for hosting the server for multiple users or on a cloud instance. It exposes a web endpoint that MCP clients can connect to over the network. 

### Configuration

1. Clone the Repository

``` shell
git clone https://github.com/Plant-Phenomics-Lab/Breedbase-Client
```

2. Configure the enviroment variables. You can set these in a `.env` file, pass them via your MCP client config, or use Docker environment variables. You must configure `BASE_URL` for your server to work. 

**Key Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `https://sweetpotatobase.org/brapi/v2` | The BrAPI server URL. You must set a base url. Set it at root of the BRAPI server endpoints (ends in /brapi/v2)  |
| `BRAPI_USERNAME` | `None` | Your login username. |
| `BRAPI_PASSWORD` | `None` | Your login password. |
| `MODE` | `stdio` | `stdio` for local apps, `http` for remote. |

👉 **[See CONFIGURATION.md](Examples/CONFIGURATION.md) for full details and examples.**

**Example with Editing .env.**

``` shell
# Copy the .env example file
cd Breedbase-Client
cp .env.example .env
# Then edit the file with your favorite text editor. 
```

3. Configure the server. 

For STDIO, can can just add this command to your MCP Client Configuration file (ex `claude.json`).

```json
{
  "mcpServers": {
    "brapiserver": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/Breedbase-Client",
        "src/main.py"
      ]
    }
  }
}
```

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
### Dependencies

- [UV](https://github.com/astral-sh/uv) version 0.4.0 or higher for running locally with STDIO. 
- [Docker](https://www.docker.com/) for running HTTP. 


**Features:**
- **Python Client**: A robust Python client for calling Breedbase that handles pagination automatically
- **FastMCP Implementation**: Simple FastMCP implementation with tool uses that can call Breedbase and save data locally as CSV or JSON

## Compatability

- A List of Server the MCP was tested against. 

|Server|Auth Type|Works?| Base Get|Search|Images|
|---|---|---|---|---|---|
|Cassavabase|SGN|✅|✅|✅|✅|
|Solgenomics|SGN|✅|✅|✅|✅|
|Sweetpotatobase|SGN|✅|✅|✅|✅|
|Yambase|SGN|✅|✅|✅|✅|
|Musabase|SGN|✅|✅|✅|No Images|
|CitrusBase|SGN|Not Tested|Not Tested|Not Tested|Not Tested|
|sugarcane.sgn.cornell.edu|SGN|Not Tested|Not Tested|Not Tested|Not Tested|
|BrAPI Test Server|None|✅|✅|✅|✅|
|T3 (Wheat Oat, Barley)|None|✅|✅|✅|✅|
|Gigwa|None|✅|✅|✅|No Images|
|MGIS|None|✅|✅|No Images|✅|
|Musa Acuminata GWAS Panel1 - GBS - genome V1|None|✅|✅|✅|No Images|
|Musa Acuminata GWAS Panel - GBS - genome V2|None|✅|✅|✅|No Images|
|Musa Germplasm Information System v5|None|✅|✅|✅|No Images|
|Crop Ontology|None|❌|❌|❌|❌|
|EU-SOL Tomato collection|None|❌|❌|❌|❌|
|TERRA-REF BrAPI implementation|None|❌|❌|❌|❌|
|URGI GnpIS Information System|None|❌|❌|❌|❌|

## Contributing

This project is under active development. Contributions and feedback are welcome!

## License

[Add your license information here]

