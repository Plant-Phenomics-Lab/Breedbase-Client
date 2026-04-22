---
name: brapi
description: Query plant breeding databases via a BrAPI MCP server. Use this skill whenever the user wants to retrieve germplasm, study, observation, location, or image data from a BrAPI-compliant database (e.g., SweetPotatoBase). Trigger on any mention of BrAPI, breeding records, germplasm IDs, trial observations, or phenotypic data retrieval — even if the user just asks to "look up a variety" or "pull some yield data". Also use when the user needs to download CSVs of field trial results or filter observations by study, location, or variable.
---

# BrAPI MCP Skills Guide (for LLM Agents)

You have access to a BrAPI MCP server that queries plant breeding databases. Follow this guide to use the tools effectively.

## Core Workflow

Always follow this pattern. Do NOT skip steps.

```
1. describe_server_capabilities()     → What endpoints exist?
2. brapi_get(service)                 → Explore data, discover DbIds
3. get_search_parameters(service)     → What filters can I use?
4. brapi_search(service, params)      → Query with DbId-based filters
5. load_result(session_id, result_id) → Sample data into context
6. quick_download_link(result_id)     → Give user their data
```

## Tools Reference

### Discovery

| Tool | Use When |
|------|----------|
| `describe_server_capabilities()` | First call in any session. Shows available endpoints and whether they support search. |
| `get_search_parameters(service)` | Before any `brapi_search`. Shows valid filter names and types. |
| `get_image_search_parameters()` | Before `download_images`. Shows image-specific filters. |

### Data Retrieval

| Tool | Use When |
|------|----------|
| `brapi_get(service)` | Exploring what data exists. Browsing small datasets. Getting DbIds for search filters. |
| `brapi_get(service, db_id)` | Fetching a single record by ID. |
| `brapi_get(service, db_id, sub)` | Sub-resources (e.g., variantset calls). |
| `brapi_search(service, search_params)` | Targeted queries with filters. Always preferred over GET for complex queries. |
| `download_images(search_params, max_images)` | Downloading images to local storage. |

### Result Access

All GET/search calls return a `session_id` and `result_id`. Use these to access cached results:

| Tool | Use When |
|------|----------|
| `get_result_summary(session_id, result_id)` | Check what's in a result without loading data. |
| `load_result(session_id, result_id, ...)` | Load data into context. Supports `limit`, `offset`, `columns`. |
| `quick_download_link(result_id)` | Get a download URL for the user. |
| `get_download_instructions(result_id)` | Detailed download options. |

## Critical Rules

### 1. Always use DbIds over names in search filters
Names are often case-sensitive and inconsistent. Use GET to discover DbIds first, then filter by DbId.

```
BAD:  brapi_search('studies', {'germplasmNames': ['covington']})     → 0 results
GOOD: brapi_search('studies', {'germplasmNames': ['Covington']})     → 66 results
BEST: brapi_search('observations', {'studyDbIds': ['4427']})         → exact match
```

If the user gives you a name and you don't know the exact casing, try multiple variants: `["Name", "name", "NAME"]`.

### 2. Start small, then expand
- Use `max_results=10` to preview structure
- Use `max_results=9999` only when you need ALL data
- Load results with `limit=10-50` first to understand columns

### 3. Context window management
- **< 500 rows**: Safe to `load_result` fully for analysis
- **500-2000 rows**: Load specific `columns` only, or sample with `limit`
- **2000+ rows**: Do NOT load fully. Sample with `limit=20-50`, then provide `quick_download_link`
- Use `get_result_summary` to check row count before loading

### 4. Check search parameters BEFORE searching
Never guess parameter names. Call `get_search_parameters(service)` first. BrAPI parameter names are specific (e.g., `locationDbIds` not `locations`, `studyTypes` not `type`).

### 5. Session persistence
Results are cached server-side as CSV. The `session_id` persists across calls in the same conversation. Reuse `result_id` values from earlier calls instead of re-querying.

## Common Workflows

### Find studies by location
```
1. brapi_get('locations', max_results=9999)
2. load_result(..., columns=['locationDbId','locationName','countryName'])
3. Identify target locationDbIds
4. brapi_search('studies', {'locationDbIds': ['12','13']})
```

### Get observations for a study
```
1. brapi_search('observations', {'studyDbIds': ['422']}, max_results=9999)
2. load_result(..., columns=['observationVariableName','observationVariableDbId'], limit=50)
3. Identify unique traits measured
4. Optionally filter: brapi_search('observations', {'observationVariableDbIds': ['76552']})
```

### Find studies for a germplasm
```
1. get_search_parameters('studies')  → confirm germplasmNames is valid
2. brapi_search('studies', {'germplasmNames': ['Covington','covington','COVINGTON']}, max_results=50)
3. Load and examine results
```

### Download images with filters
```
1. get_image_search_parameters()
2. download_images(search_params={'imageHeightMin': 300}, max_images=10)
```

## Data Access Patterns

Results from GET/search are saved as CSV and can be accessed two ways:

**In-context** (for analysis):
```
load_result(session_id, result_id, limit=100, columns=['col1','col2'])
```

**For the user** (download):
```
quick_download_link(result_id, session_id)
```

**Local file path** (STDIO mode only):
- Default: `./cache/{server_name}/sessions/{session_id}/{result_id}.csv`
- Custom: `{DOWNLOAD_DIR_OVERRIDE}/data/{session_id}/{result_id}.csv`

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Search without checking parameters first | Call `get_search_parameters()` first |
| Filter by name strings when DbIds are available | GET to discover DbIds, then search by DbId |
| Load 5000+ rows into context | Sample with `limit=50`, provide download link |
| Assume parameter names | They vary by server; always check |
| Skip `describe_server_capabilities()` | Always call it first - not all servers support all endpoints |
| Re-query data you already have | Reuse `session_id`/`result_id` from earlier calls |
