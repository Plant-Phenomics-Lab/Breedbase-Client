"""Observation tools for BrAPI Phenotyping endpoints."""

import csv
import json
import os
import re
from datetime import datetime, timezone
from typing import Optional

from fastmcp import FastMCP

from psa.client import BrAPIClient
from psa.config import PSAConfig

# CSV columns for observation export (matches reference format)
CSV_COLUMNS = [
    "observationVariableDbId",
    "observationUnitName",
    "value",
    "observationDbId",
    "studyDbId",
    "observationUnitDbId",
    "germplasmDbId",
    "observationVariableName",
    "germplasmName",
    "uploadedBy",
    "collector",
    "season.season",
    "season.year",
    "season.seasonDbId",
]


def flatten_observation(obs: dict) -> dict:
    """Flatten nested season data for CSV export.

    Args:
        obs: A BrAPI observation object with potentially nested season data.

    Returns:
        A flat dictionary with season fields extracted to dot-notation keys.
    """
    flat = {}
    # Copy top-level fields
    for col in CSV_COLUMNS[:11]:  # All non-season columns
        flat[col] = obs.get(col, "")

    # Flatten nested season data
    season = obs.get("season", {}) or {}
    flat["season.season"] = season.get("season", "")
    flat["season.year"] = season.get("year", "")
    flat["season.seasonDbId"] = season.get("seasonDbId", "")

    return flat


def register_observation_tools(server: FastMCP, client: BrAPIClient, config: Optional[PSAConfig] = None) -> None:
    """Register observation tools with the MCP server."""

    # Default data directory if config not provided
    data_dir = config.data_dir if config else "./data"

    @server.tool()
    def get_observations(
        study_db_id: Optional[str] = None,
        germplasm_db_id: Optional[str] = None,
        observation_variable_db_id: Optional[str] = None,
        observation_unit_db_id: Optional[str] = None,
        observation_level: Optional[str] = None,
        page_size: int = 100,
    ) -> str:
        """
        Get phenotypic observations.

        Retrieves measured trait values from field experiments. At least one
        filter parameter should be provided to avoid retrieving too much data.

        Args:
            study_db_id: Filter by study ID (recommended - get from search_studies)
            germplasm_db_id: Filter by germplasm ID
            observation_variable_db_id: Filter by trait/variable ID
            observation_unit_db_id: Filter by observation unit (plot/plant) ID
            observation_level: Filter by level (e.g., "plot", "plant", "subplot")
            page_size: Maximum number of results (default 100)

        Returns:
            JSON array of observations with:
            - observationDbId, observationUnitDbId
            - germplasmDbId, germplasmName
            - observationVariableDbId, observationVariableName
            - value, observationTimeStamp
            - studyDbId
        """
        params = {"pageSize": page_size}
        if study_db_id:
            params["studyDbId"] = study_db_id
        if germplasm_db_id:
            params["germplasmDbId"] = germplasm_db_id
        if observation_variable_db_id:
            params["observationVariableDbId"] = observation_variable_db_id
        if observation_unit_db_id:
            params["observationUnitDbId"] = observation_unit_db_id
        if observation_level:
            params["observationLevel"] = observation_level

        response = client.get("/observations", params=params)
        data = response.get("result", {}).get("data", [])
        return json.dumps(data, indent=2)

    @server.tool()
    def get_observation_variables(
        study_db_id: Optional[str] = None,
        common_crop_name: Optional[str] = None,
        observation_variable_name: Optional[str] = None,
        trait_class: Optional[str] = None,
        page_size: int = 100,
    ) -> str:
        """
        Get observation variables (traits).

        Lists the phenotypic traits that can be measured, including their
        definitions, measurement scales, and methods.

        Args:
            study_db_id: Filter to variables used in a specific study
            common_crop_name: Filter by crop name
            observation_variable_name: Filter by variable name (partial match)
            trait_class: Filter by trait class (e.g., "Morphological", "Agronomic")
            page_size: Maximum number of results (default 100)

        Returns:
            JSON array of observation variables with:
            - observationVariableDbId, observationVariableName
            - trait (name, description, traitClass)
            - method (description, formula)
            - scale (dataType, validValues)
            - ontologyReference
        """
        params = {"pageSize": page_size}
        if study_db_id:
            params["studyDbId"] = study_db_id
        if common_crop_name:
            params["commonCropName"] = common_crop_name
        if observation_variable_name:
            params["observationVariableName"] = observation_variable_name
        if trait_class:
            params["traitClass"] = trait_class

        response = client.get("/variables", params=params)
        data = response.get("result", {}).get("data", [])
        return json.dumps(data, indent=2)

    @server.tool()
    def download_study(
        study_db_id: str,
        output_format: str = "json",
        include_metadata: bool = True,
    ) -> str:
        """
        Download all observations from a study and save to a local file.

        Fetches all observation data (with pagination) and saves it to the
        data directory with a descriptive filename. Use this when the user
        wants to save or export study data locally.

        Args:
            study_db_id: The study ID to download (required)
            output_format: Output format - "json" (default) or "csv"
            include_metadata: Include study metadata in JSON output (default True, ignored for CSV)

        Returns:
            JSON with download status including:
            - file_path: Path to the saved file
            - study_name: Name of the study
            - observation_count: Number of observations downloaded
            - file_size_kb: Size of the saved file in KB
        """
        # Validate output format
        output_format = output_format.lower()
        if output_format not in ("json", "csv"):
            return json.dumps({
                "status": "error",
                "message": f"Invalid output_format '{output_format}'. Use 'json' or 'csv'."
            }, indent=2)
        # Get study details for metadata and naming
        study_response = client.get(f"/studies/{study_db_id}")
        study = study_response.get("result", {})

        study_name = study.get("studyName", f"study_{study_db_id}")
        program_name = study.get("additionalInfo", {}).get("programName", "unknown")
        seasons = study.get("seasons", [])
        year = seasons[0] if seasons else "unknown"

        # Fetch all observations with pagination
        all_observations = []
        page = 0
        while True:
            response = client.get(
                "/observations",
                params={"studyDbId": study_db_id, "pageSize": 1000, "page": page}
            )
            data = response.get("result", {}).get("data", [])
            if not data:
                break
            all_observations.extend(data)
            page += 1
            if len(data) < 1000:
                break

        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        # Sanitize filename components (remove special characters)
        safe_study_name = re.sub(r'[^\w\-]', '_', study_name)
        safe_program = re.sub(r'[^\w\-]', '_', program_name)

        if output_format == "csv":
            # Create filename: {program}_{year}_{study_name}.csv
            filename = f"{safe_program}_{year}_{safe_study_name}.csv"
            file_path = os.path.join(data_dir, filename)

            # Write CSV file
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
                writer.writeheader()
                for obs in all_observations:
                    writer.writerow(flatten_observation(obs))
        else:
            # Create filename: {program}_{year}_{study_name}.json
            filename = f"{safe_program}_{year}_{safe_study_name}.json"
            file_path = os.path.join(data_dir, filename)

            # Prepare output data
            output = {
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "study_db_id": study_db_id,
                "observation_count": len(all_observations),
                "observations": all_observations,
            }

            if include_metadata:
                output["study_metadata"] = study

            # Write JSON file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)

        file_size_kb = os.path.getsize(file_path) / 1024

        return json.dumps({
            "status": "success",
            "file_path": os.path.abspath(file_path),
            "format": output_format,
            "study_name": study_name,
            "program": program_name,
            "year": year,
            "observation_count": len(all_observations),
            "file_size_kb": round(file_size_kb, 2),
        }, indent=2)
