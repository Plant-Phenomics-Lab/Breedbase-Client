# LLM Agent Testing Framework

This directory contains two implementations of LLM-based agents for querying the BrAPI breeding database:

## 1. Direct BrAPI Client Agent (`agent_brapi_test.py`)

**Architecture:**
- Uses Groq LLM to orchestrate queries
- Directly instantiates and calls `BrAPIClient`
- No MCP server required

**Workflow:**
1. **Agent Think** → LLM analyzes user query, determines which endpoint to call
2. **Agent Act** → Direct call to `BrAPIClient.general_get()`
3. **Agent Respond** → LLM synthesizes results into natural language

**Test Results: 4/4 Passed ✅**
- Find studies at Clinton Research Station → 136 locations found
- How many breeding programs? → 31 programs
- Show germplasm for sweet potato → 0 records (not in database)
- What studies in 2024? → 2006 total studies (none in 2024)

**Run:**
```bash
uv run python agent_brapi_test.py
```

**Output:** `agent_brapi_test_results.json`

---

## 2. MCP Server Agent (`agent_mcp_test.py`)

**Architecture:**
- Uses Groq LLM to orchestrate queries
- Calls MCP server functions via Python imports
- Demonstrates MCP tool interface

**Workflow:**
1. **Agent Think** → LLM analyzes user query, determines which MCP tool to call
   - `all_functions` - List available endpoints
   - `specific_function` - Get details about endpoint
   - `general_get` - Query endpoint with parameters
2. **Agent Act** → Call MCP tool via `call_mcp_tool()`
3. **Agent Respond** → LLM synthesizes results into natural language

**Test Results: 4/4 Passed ✅**
- What BrAPI endpoints are available? → locations, studies, germplasm, programs, traits
- Tell me about the studies endpoint → Parameter help: commonCropName filter
- How many studies available? → 1 study (sample)
- Show me location data → 136 location records with details

**Run:**
```bash
uv run python agent_mcp_test.py
```

**Output:** `agent_mcp_test_results.json`

---

## Key Features

### Both Implementations Provide:
- ✅ Natural language query parsing via Groq LLM
- ✅ Intelligent endpoint/tool selection
- ✅ Data fetching from SweetPotatoBase BrAPI
- ✅ Result synthesis into friendly summaries
- ✅ Verbose logging of agent thinking process
- ✅ JSON output with results and metadata

### Differences:

| Feature | `test_agent.py` | `agent_mcp_test.py` |
|---------|-----------------|-------------------|
| **Backend** | Direct `BrAPIClient` | MCP Server Functions |
| **Tool Abstraction** | None | MCP Protocol |
| **Dependency** | Python Client | MCP Server Running |
| **Flexibility** | Direct control | MCP Standard Interface |
| **Use Case** | Direct integration | Remote/standardized tools |

---

## Environment Setup

```bash
# .env file
SWEETPOTATOBASE_USERNAME=<your-username>
SWEETPOTATOBASE_PASSWORD=<your-password>
GROQ_API_KEY=<your-groq-api-key>
```

## Testing Queries

Default test queries demonstrate:
1. **Endpoint Discovery** - What tools/endpoints are available?
2. **Tool/Endpoint Information** - How do I use a specific tool?
3. **Data Aggregation** - Get counts, summaries of data
4. **Data Retrieval** - Fetch actual records with details

---

## Results Format

```json
[
  {
    "query": "User's natural language question",
    "plan": {"tool/action": "...", "reasoning": "...", "parameters": {...}},
    "success": true,
    "tool": "tool_name",
    "record_count": 100,
    "response": "Natural language response from LLM"
  }
]
```


