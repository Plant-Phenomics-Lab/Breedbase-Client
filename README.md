<div align="center">

# BrAPI MCP Server

</div>

<div align="center">

**The BrAPI MCP Server provides LLMs with tools to search and retrieve data from BrAPI v2 Compatible Servers.**

</div>

<div align="center">

[![Version](https://img.shields.io/badge/Version-0.1.0-blue.svg)](./pyproject.toml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?&logo=python&logoColor=white)](https://www.python.org/)
[![MCP SDK](https://img.shields.io/badge/MCP-1.19.0-green.svg?style=flat-square)](https://modelcontextprotocol.io/)
![fastmcp](https://img.shields.io/badge/fastmcp-2.13.1-orange)
![UV](https://img.shields.io/badge/UV-^0.4.0-magenta)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker&logoColor=white)

</div>

Jerry Yu, Akarsh Eathamukkala, Jay Shah, Benjamin Maza, Jerome Maleski

# 🛠️ Tools Overview

This server provides 9 powerful tools for accessing and analyzing plant breeding data from BrAPI-compatible servers:

| Tool Name | Description |
| :--- | :--- |
| **Core BrAPI Access** | |
| `describe_server_capabilities` | Returns a list of accesible endpoints and searchable filters for the BrAPI compliant server you are connected to. |
| `brapi_get` | Fetches data from any BrAPI GET endpoint. Supports filtering by Database ID (DbID) and pagination. |
| `brapi_search` | Performs advanced searches using BrAPI POST search endpoints. |
| `get_image_search_parameters` | Retrieves valid filters for the image search endpoint. |
| `download_images` | Downloads images from the BrAPI server to the local directory based on search criteria. |
| **Data Processing & Management** (Mostly for the Model) | |
| `get_result_summary` | Provides a summary of a saved result (columns, row count, size) without loading the full data. |
| `load_result` | Loads a saved result (or a specific subset) into the conversation context for analysis. Supports pagination and column selection. |
| `get_download_instructions` | Generates URLs and instructions for downloading a csv of saved results via HTTP. |
| `quick_download_link` | Returns a direct download URL for a saved result, ideal for quick access. |

You can access some example workflows in the [Examples](./Examples) folder. [Conversational_Workflow.md](./Examples/Conversational_Workflow.md) and [Covington_MetaAnalysis_EDA.md](./Examples/Covington_MetaAnalysis_EDA.md) show some workflows that incorporate some complex interactive filtering. VS Code Copilot with Claude Sonnet/Haiku 4.5 were used to for the workflows. 

## Examples

### `brapi_get`

Download data from most BrAPI compatible servers. Generally use it to fetch data for subsequent searches. 

**Example Use Cases:**
- "Where are all the locations that sweetpotatoes have been trialed on?" 
- "For the variantset with the dbID =5, what were the possible genotype calls?" 

More examples [here](./Examples/Get.md). 

### `brapi_search`
Search and discover breeding data using advanced filters. Supports all search terms compatible with BrAPI. 

**Example Use Cases:**
- "Find all studies in 'Mozambique' with 'Advanced Yield Trial' type."
- "Please download all data For the Advanced Yield Trial run at NCSU research station 1 during spring 2018."

More examples [here](./Examples/Search.md). 

# Getting Started

- The server supports two modes: **STDIO** and **HTTP**.
  - **STDIO:** Best for personal use. The server runs directly on your machine, and files are saved to your local disk. It is easier to configure and more secure for single users.
  - **HTTP:** Under active development. Best for hosting the server for multiple users or on a cloud instance. It exposes a web endpoint that MCP clients can connect to over the network. 

### Configuration

1. Clone the Repository

``` shell
git clone https://github.com/Plant-Phenomics-Lab/Breedbase-Client

```
2. Create UV Environment
```shell
cd Breedbase-Client
uv venv
.venv\Scripts\activate
uv sync
```

3. Configure the enviroment variables. You can set these in a `.env` file, pass them via your MCP client config, or use Docker environment variables. You must configure `BASE_URL` for your server to work. 

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

4. Configure the server. 

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

