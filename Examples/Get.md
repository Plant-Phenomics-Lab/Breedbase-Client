# BrAPI GET Operations Examples

## Basic Get

**BrAPI Server:** yambase

**Tool Call:**

```json
{
  "service": "locations"
}
```

**Response:**

```json
{
  "summary": {
    "total_count": 122,
    "returned_count": 100,
    "columns": [
      "locationDbId",
      "countryName",
      "abbreviation",
      "externalReferences",
      "locationName",
      "instituteAddress",
      "countryCode",
      "locationType",
      "instituteName",
      "coordinates.type",
      "coordinates.geometry.type",
      "coordinates.geometry.coordinates",
      "additionalInfo.breeding_program",
      "additionalInfo.noaa_station_id"
    ],
    "column_count": 14,
    "truncated": true
  },
  "access": {
    "resource": "brapi://results/e7e70983-0565-4780-ab3b-ccc0ac889286/locations_af76c559",
    "tools": {
      "get_summary": "get_result_summary('e7e70983-0565-4780-ab3b-ccc0ac889286','locations_af76c559'**)",
      "load_result": "load_result('e7e70983-0565-4780-ab3b-ccc0ac889286','locations_af76c559', limit=100)"
    }
  },
  "hint": "Data saved to server. Use resource brapi://results/e7e70983-0565-4780-ab3b-ccc0ac889286/locations_af76c559 or load_result('e7e70983-0565-4780-ab3b-ccc0ac889286','locations_af76c559') to access."
}
```

## Get by Database ID

Retrieves a single record by its database identifier.

**BrAPI Server:** yambase

**Tool Call:**
```json
{
  "service": "locations",
  "db_id": "31"
}
```

**Response:**

```json
{
  "summary": {
    "total_count": 1,
    "returned_count": 1,
    "columns": [
      "instituteName",
      "locationType",
      "instituteAddress",
      "locationName",
      "countryCode",
      "externalReferences",
      "abbreviation",
      "countryName",
      "locationDbId",
      "coordinates.type",
      "coordinates.geometry.coordinates",
      "coordinates.geometry.type"
    ],
    "column_count": 12,
    "truncated": false
  },
  "access": {
    "resource": "brapi://results/e7e70983-0565-4780-ab3b-ccc0ac889286/locations_b491b38e",
    "tools": {
      "get_summary": "get_result_summary('e7e70983-0565-4780-ab3b-ccc0ac889286','locations_b491b38e')",
      "load_result": "load_result('e7e70983-0565-4780-ab3b-ccc0ac889286','locations_b491b38e', limit=100)"
    }
  },
  "hint": "Data saved to server. Use resource brapi://results/e7e70983-0565-4780-ab3b-ccc0ac889286/locations_b491b38e or load_result('e7e70983-0565-4780-ab3b-ccc0ac889286','locations_b491b38e') to access."
}
`# Get Sub-resources

Retrieves sub-resources associated with a parent resource (e.g., calls for a specific variant set).

**BrAPI Server:** testserver

**
  "db_id": "variantset1", 
  "service": "variantsets", 
  "sub": "calls" 
}
```

**Response:**
*
```json
{ "db_id": "variantset1", "service": "variantsets", "sub": "calls" }
```
**Response**
```json
{
  "summary": {
    "total_count": 260,
    "returned_count": 100,
    "columns": [
      "callSetDbId",
      "callSetName",
      "genotypeValue",
      "genotypeMetadata",
      "genotype_likelihood",
      "phaseSet",
      "variantDbId",
      "variantName",
      "variantSetDbId",
      "variantSetName",
      "genotype.values"
    ],
    "column_count": 11,
    "truncated": true
  },
  "access": {
    "resource": "brapi://results/3d19eff5-c624-46a4-8979-7e279e93ab4a/variantsets_5e7de10d",
    "tools": {
```
---
## Notes

### Use Cases
- The GET function is ideal for exploring BrAPI servers and understanding available data.
- For complex queries, use the search function instead.
- in agentic workflows, models may use this function to get values to filter/search programmatically. 

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
   - Default: `Programs/cache/yambase/e7e70983-0565-4780-ab3b-ccc0ac889286/locations_af76c559.csv`
   - Custom (DOWNLOAD_DIR_OVERRIDE = "Downloads"): `Downloads/data/e7e70983-0565-4780-ab3b-ccc0ac889286/locations_af76c559.csv`

# Notes

- Practically, this function is good for understanding what is on you BrAPI server if it is relativley small, most complex quesries should be routed to the search function. 

- The server detects how many entries there are, so if you want all entires on your first try tell the model to set max_pages very high (some arbitasry number like 9999)

- Data access is provided one of two ways. you can ask for the data (the model usually understnads to provide you wiht a download linkw itht eh  `quick_download_link` or `get_download_instructions`) or if the MCP is runnign locally yuou can access it by going to ./cache/name/sessions or your_custom DOWNLOAD_DIR_OVERRIDE/sessions. So for example if your BrAPI MCP was located in Programs, then the first get tool call example would be store in (e7e70983-0565-4780-ab3b-ccc0ac889286/locations_af76c559) Programs/cache/yambase/e7e70983-0565-4780-ab3b-ccc0ac889286/locations_af76c559.csv (wordy, I know). Or if you manuall set DOWNLOAD_DIR_OVERRIDE to say Donwloads, then the file would be in Donwnloads/data/e7e70983-0565-4780-ab3b-ccc0ac889286/locations_af76c559.csv. 