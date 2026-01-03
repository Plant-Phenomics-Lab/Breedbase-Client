# Conversational Workflow: Finding Clonal Studies in Uganda

This document demonstrates a realistic conversational workflow for discovering and retrieving phenotypic data from musabase.

---

## User Request

> "Can you find me all clonal studies in Uganda?"

---

## Step 1: Discover Locations in Uganda

**Assistant:** Let me first get all locations and identify which ones are in Uganda.

**BrAPI Server:** musabase

**Tool Call:**

```json
{
  "service": "locations",
  "max_results": 50
}
```

**Response:**

```json
{
  "summary": {
    "total_count": 23,
    "returned_count": 23,
    "columns": [
      "instituteAddress",
      "instituteName",
      "externalReferences",
      "locationName",
      "countryCode",
      "locationType",
      "abbreviation",
      "locationDbId",
      "countryName",
      "coordinates.type",
      "coordinates.geometry.coordinates",
      "coordinates.geometry.type",
      "additionalInfo.breeding_program",
      "additionalInfo.noaa_station_id"
    ],
    "column_count": 14,
    "truncated": false
  }
}
```

**Load Country Information:**

```json
{
  "session_id": "a36fa599-9990-4df8-b731-32b973e63d6e",
  "result_id": "locations_af76c559",
  "columns": ["locationDbId", "locationName", "countryName", "countryCode"]
}
```

**Uganda Locations Found:**

| locationDbId | locationName | countryName | countryCode |
|--------------|--------------|-------------|-------------|
| 12 | Sendusu | Uganda | UGA |
| 13 | Mbarara | Uganda | UGA |
| 16 | kawanda | Uganda | UGA |
| 23 | Hoima | Uganda | UGA |
| 35 | Ikulwe | Uganda | UGA |
| 36 | Ngetta | Uganda | UGA |

**Assistant:** I found 6 locations in Uganda. Now let me search for studies at these locations.

---

## Step 2: Search Studies in Uganda

**Tool Call:**

```json
{
  "service": "studies",
  "search_params": {
    "locationDbIds": ["12", "13", "16", "23", "35", "36"]
  },
  "max_results": 100
}
```

**Response:**

```json
{
  "summary": {
    "total_matches": 232,
    "returned_count": 100,
    "columns": [
      "endDate",
      "trialName",
      "studyName",
      "externalReferences",
      "locationName",
      "seasons",
      "documentationURL",
      "studyDescription",
      "trialDbId",
      "studyType",
      "active",
      "dataLinks",
      "studyDbId",
      "locationDbId",
      "startDate",
      "commonCropName",
      "additionalInfo.programDbId",
      "additionalInfo.programName",
      "experimentalDesign.description",
      "experimentalDesign.PUI"
    ],
    "column_count": 20,
    "truncated": true
  }
}
```

**Sample Study Types Found:**

| studyDbId | studyName | studyType | locationName |
|-----------|-----------|-----------|--------------|
| 882 | 15_05_2023_screening_for_parental_banana_nematode_resistance_batch4_ | health_status_trial | Sendusu |
| 585 | 181 Genotypes_RTB Foods NIRS | Clonal Evaluation | Sendusu |
| 646 | 2001 EET 5 IITA-Sendusu | Clonal Evaluation | Sendusu |
| 645 | 2002 EET 7 IITA-Sendusu | Clonal Evaluation | Sendusu |

**Assistant:** I found 232 studies in Uganda. I see several study types including "Clonal Evaluation", "health_status_trial", "Genomic Selection", and others. When you say "clonal studies", do you mean studies with `studyType = "Clonal Evaluation"`?

---

## User Clarification

> "Yes, exactly! Show me the Clonal Evaluation studies."

---

## Step 3: Filter for Clonal Evaluation Studies

**Tool Call:**

```json
{
  "service": "studies",
  "search_params": {
    "locationDbIds": ["12", "13", "16", "23", "35", "36"],
    "studyTypes": ["Clonal Evaluation"]
  },
  "max_results": 50
}
```

**Response:**

```json
{
  "summary": {
    "total_matches": 102,
    "returned_count": 50,
    "columns": [
      "locationDbId",
      "studyDbId",
      "dataLinks",
      "startDate",
      "commonCropName",
      "trialDbId",
      "studyDescription",
      "active",
      "studyType",
      "studyName",
      "documentationURL",
      "seasons",
      "locationName",
      "externalReferences",
      "trialName",
      "experimentalDesign.PUI",
      "experimentalDesign.description",
      "additionalInfo.programName",
      "additionalInfo.programDbId"
    ],
    "column_count": 19,
    "truncated": true
  }
}
```

**Load Study Details:**

```json
{
  "session_id": "a36fa599-9990-4df8-b731-32b973e63d6e",
  "result_id": "search_studies_a6c5cc5e",
  "columns": ["studyDbId", "studyName", "studyDescription", "locationName", "seasons", "trialName"],
  "limit": 10
}
```

**Clonal Evaluation Studies in Uganda (Sample):**

| studyDbId | studyName | studyDescription | locationName | seasons | trialName |
|-----------|-----------|------------------|--------------|---------|-----------|
| 585 | 181 Genotypes_RTB Foods NIRS | 181 Genotypes for NIRS only | Sendusu | ['2020'] | Quality Evaluation trials |
| 646 | 2001 EET 5 IITA-Sendusu | Hybrids under early evaluation in the field at IITA Sendusu | Sendusu | ['2002'] | Early Evaluation Trials |
| 645 | 2002 EET 7 IITA-Sendusu | Hybrids under early evaluation in the field at IITA Sendusu | Sendusu | ['2002'] | Early Evaluation Trials |
| 644 | 2002 EET 8 IITA-Sendusu | Hybrids under early evaluation in the field at IITA Sendusu | Sendusu | ['2002'] | Early Evaluation Trials |
| 642 | 2003 EET 10 IITA Sendusu | Hybrids under early evaluation in the field at IITA Sendusu | Sendusu | ['2003'] | Early Evaluation Trials |
| 638 | 2003 EET 11 IITA Sendusu | Hybrids under early evaluation in the field at IITA Sendusu | Sendusu | ['2003'] | Early Evaluation Trials |
| 643 | 2003 EET 9 IITA Sendusu | Hybrids under early evaluation in the field at IITA Sendusu | Sendusu | ['2003'] | Early Evaluation Trials |
| 636 | 2004 EET 12 Sendusu | Hybrids under early evaluation in the field at IITA Sendusu | Sendusu | ['2021'] | Early Evaluation Trials |
| 629 | 2005 EET 13 Sendusu | EET hybrids in EET 13 in 2005 at Sendusu | Sendusu | ['2005'] | Early Evaluation Trials |
| 634 | 2006 EET 14 Sendusu | Hybrids under early evaluation in the field at IITA-Sendusu | Sendusu | ['2006'] | Early Evaluation Trials |

**Assistant:** Found 102 Clonal Evaluation studies in Uganda! Most are Early Evaluation Trials (EET) conducted at Sendusu from 2001-2020. Which study would you like to explore further?

---

## User Selection

> "Let me look at study 422 - the 2016 EET 23 IITA-Sendusu. Can you get all the observations for that?"

---

## Step 4: Retrieve All Observations

**Assistant:** I'll retrieve all observations from study 422. Setting max_results very high to get everything in one request.

**Tool Call:**

```json
{
  "service": "observations",
  "search_params": {
    "studyDbIds": ["422"]
  },
  "max_results": 9999
}
```

**Response:**

```json
{
  "summary": {
    "total_matches": 6384,
    "returned_count": 6384,
    "columns": [
      "germplasmDbId",
      "observationUnitDbId",
      "observationUnitName",
      "observationDbId",
      "germplasmName",
      "value",
      "studyDbId",
      "uploadedBy",
      "observationVariableDbId",
      "collector",
      "observationVariableName",
      "season.year",
      "season.seasonDbId",
      "season.season"
    ],
    "column_count": 14,
    "truncated": false
  },
  "access": {
    "resource": "brapi://results/a36fa599-9990-4df8-b731-32b973e63d6e/search_observations_819fd7f3",
    "tools": {
      "get_summary": "get_result_summary('a36fa599-9990-4df8-b731-32b973e63d6e','search_observations_819fd7f3')",
      "load_sample": "load_result('a36fa599-9990-4df8-b731-32b973e63d6e','search_observations_819fd7f3', limit=100)",
      "load_columns": "load_result('a36fa599-9990-4df8-b731-32b973e63d6e','search_observations_819fd7f3', columns=['col1', 'col2'])"
    }
  },
  "hint": "Data saved to server. Access via resource or load_result('search_observations_819fd7f3')"
}
```

**Success!** Retrieved all **6,384 observations** from study 422.

---

## Step 5: Examine Sample Data

**Sample Observations (first 15 rows):**

| germplasmName | observationUnitName | observationVariableName | value | season |
|---------------|---------------------|-------------------------|-------|--------|
| 34244S-2 | 34244S-2_R4C9_Plot60 | Number of functional leaves: count\|cycle 1 main plant\|at flowering\|COMP:0000478 | 8 | 2016 |
| 34244S-2 | 34244S-2_R4C9_Plot60 | Youngest leaf spotted rank\|cycle 1 main plant\|at flowering\|COMP:0000469 | 7 | 2016 |
| 34607S-36 | 34607S-36_R2C16_Plot33 | Bunch orientation 1-5\|cycle 1 main plant\|at harvesting\|COMP:0000466 | 2 | 2016 |
| 34607S-36 | 34607S-36_R2C16_Plot33 | Bunch size 1-3\|cycle 1 main plant\|at harvesting\|COMP:0000470 | 2 | 2016 |
| 34607S-36 | 34607S-36_R2C16_Plot33 | Fruit parthenocarpy\|cycle 1 main plant\|at harvesting\|COMP:0000464 | 0 | 2016 |
| 34607S-36 | 34607S-36_R2C16_Plot33 | Fruitfill 1-2\|cycle 1 main plant\|at harvesting\|COMP:0000465 | 1 | 2016 |
| 34607S-36 | 34607S-36_R2C16_Plot33 | Number of functional leaves: count\|cycle 1 main plant\|at flowering\|COMP:0000478 | 7 | 2016 |
| 34607S-36 | 34607S-36_R2C16_Plot33 | Plant height 1-3\|cycle 1 main plant\|at flowering\|COMP:0000467 | 2 | 2016 |
| 34607S-36 | 34607S-36_R2C16_Plot33 | Suckering behavior 1-3\|cycle 1 main plant\|at flowering\|COMP:0000468 | 2 | 2016 |
| 34607S-36 | 34607S-36_R2C16_Plot33 | Youngest leaf spotted rank\|cycle 1 main plant\|at flowering\|COMP:0000469 | 5 | 2016 |
| 34607S-36 | 34607S-36_R3C15_Plot49 | Number of functional leaves: count\|cycle 1 main plant\|at flowering\|COMP:0000478 | 12 | 2016 |
| 34607S-36 | 34607S-36_R3C15_Plot49 | Youngest leaf spotted rank\|cycle 1 main plant\|at flowering\|COMP:0000469 | 7 | 2016 |
| 34896S-17 | 34896S-17_R3C7_Plot41 | Number of functional leaves: count\|cycle 1 main plant\|at flowering\|COMP:0000478 | 7 | 2016 |
| 34896S-17 | 34896S-17_R3C7_Plot41 | Youngest leaf spotted rank\|cycle 1 main plant\|at flowering\|COMP:0000469 | 2 | 2016 |
| 35066S-166 | 35066S-166_R1C1_Plot1 | Bunch orientation 1-5\|cycle 1 main plant\|at harvesting\|COMP:0000466 | 3 | 2016 |

---

## Step 6: Download Data

**Get Download Link:**

```json
{
  "result_id": "search_observations_819fd7f3",
  "session_id": "a36fa599-9990-4df8-b731-32b973e63d6e"
}
```

**Download URL:**

```
http://localhost:8001/download/a36fa599-9990-4df8-b731-32b973e63d6e/search_observations_819fd7f3
```

**Assistant:** All 6,384 observations are ready for download! The dataset includes:

- **Germplasm**: Multiple banana genotypes (e.g., 34244S-2, 34607S-36, 34896S-17)
- **Traits measured**: 
  - Number of functional leaves
  - Youngest leaf spotted rank
  - Bunch orientation, size, and characteristics
  - Plant height
  - Suckering behavior
  - Fruit parthenocarpy and fill
- **Observation units**: Individual plots (e.g., R4C9_Plot60)
- **Season**: 2016
- **Measurement timing**: At flowering and at harvesting
