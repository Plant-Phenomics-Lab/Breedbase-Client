# Search

## Basic Search

BrAPI Server: musabase

**Tool Call:**

```json
{
  "service": "studies",
  "search_params": {
    "locationDbIds": ["12", "13", "19"]
  },
  "max_results": 50
}
```

**Response:**

```json
{
  "summary": {
    "total_matches": 178,
    "returned_count": 50,
    "columns": [
      "startDate",
      "commonCropName",
      "studyDbId",
      "dataLinks",
      "locationDbId",
      "studyType",
      "active",
      "studyDescription",
      "trialDbId",
      "seasons",
      "locationName",
      "externalReferences",
      "documentationURL",
      "studyName",
      "trialName",
      "experimentalDesign.description",
      "experimentalDesign.PUI",
      "additionalInfo.programName",
      "additionalInfo.programDbId"
    ],
    "column_count": 19,
    "truncated": true
  },
  "access": {
    "resource": "brapi://results/a36fa599-9990-4df8-b731-32b973e63d6e/search_studies_306303e0",
    "tools": {
      "get_summary": "get_result_summary('a36fa599-9990-4df8-b731-32b973e63d6e','search_studies_306303e0')",
      "load_sample": "load_result('a36fa599-9990-4df8-b731-32b973e63d6e','search_studies_306303e0', limit=100)",
      "load_columns": "load_result('a36fa599-9990-4df8-b731-32b973e63d6e','search_studies_306303e0', columns=['col1', 'col2'])"
    }
  },
  "hint": "Data saved to server. Access via resource or load_result('search_studies_306303e0')"
}
```

## Complex Multi-Parameter Search

Perform a more sophisticated search combining multiple parameters: locations, study type, and trial. BrAPI supports AND filtering (so this query would be for clonal evaluations at location 12).

BrAPI Server: musabase

**Tool Call:**

```json
{
  "service": "studies",
  "search_params": {
    "locationDbIds": ["12", "19"],
    "studyTypes": ["Clonal Evaluation"],
    "trialDbIds": ["489"]
  },
  "max_results": 30
}
```

**Response:**

```json
{
  "summary": {
    "total_matches": 41,
    "returned_count": 30,
    "columns": [
      "studyDescription",
      "trialDbId",
      "studyType",
      "active",
      "studyDbId",
      "dataLinks",
      "locationDbId",
      "commonCropName",
      "startDate",
      "trialName",
      "studyName",
      "seasons",
      "locationName",
      "externalReferences",
      "documentationURL",
      "experimentalDesign.PUI",
      "experimentalDesign.description",
      "additionalInfo.programName",
      "additionalInfo.programDbId"
    ],
    "column_count": 19,
    "truncated": true
  },
  "access": {
    "resource": "brapi://results/a36fa599-9990-4df8-b731-32b973e63d6e/search_studies_dd5eb339",
    "tools": {
      "get_summary": "get_result_summary('a36fa599-9990-4df8-b731-32b973e63d6e','search_studies_dd5eb339')",
      "load_sample": "load_result('a36fa599-9990-4df8-b731-32b973e63d6e','search_studies_dd5eb339', limit=100)",
      "load_columns": "load_result('a36fa599-9990-4df8-b731-32b973e63d6e','search_studies_dd5eb339', columns=['col1', 'col2'])"
    }
  },
  "hint": "Data saved to server. Access via resource or load_result('search_studies_dd5eb339')"
}
```

---

## Notes

### Performance Tips

- It's generally good to use GET tools to retreive exploratory information for the model to use for further search parameters, unless you know the exact ontology name. 

- Start with small `max_results` values (10-50) to preview data structure

- Combine multiple filters to narrow results efficiently
- Use `load_result()` with specific columns to reduce data transfer

### Pagination
- The server automatically detects the total number of entries
- To retrieve all entries in one request, set `max_pages` to a high value (e.g., 9999)

### Data Access

Results can be accessed in two ways:

1. **Via API Tools:**
   - Request a download link using `quick_download_link` or `get_download_instructions`
   - The model typically provides the appropriate link automatically

2. **Direct File Access (Local MCP Only):**
   - Default location: `./cache/{server_name}/sessions/{session_id}/{result_id}.csv`
   - Custom location: `{DOWNLOAD_DIR_OVERRIDE}/data/{session_id}/{result_id}.csv`
   
   **Examples:**
   - Default: `Programs/cache/musabase/a36fa599-9990-4df8-b731-32b973e63d6e/search_studies_306303e0.csv`
   - Custom (DOWNLOAD_DIR_OVERRIDE = "Downloads"): `Downloads/data/a36fa599-9990-4df8-b731-32b973e63d6e/search_studies_306303e0.csv`
