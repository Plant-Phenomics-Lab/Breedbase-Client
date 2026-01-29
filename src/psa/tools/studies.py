"""Study tools for BrAPI Study endpoints."""

import json
from typing import Optional

from fastmcp import FastMCP

from psa.client import BrAPIClient


def register_study_tools(server: FastMCP, client: BrAPIClient) -> None:
    """Register study tools with the MCP server."""

    @server.tool()
    def search_studies(
        trial_db_id: Optional[str] = None,
        program_db_id: Optional[str] = None,
        location_db_id: Optional[str] = None,
        common_crop_name: Optional[str] = None,
        study_name: Optional[str] = None,
        season_db_id: Optional[str] = None,
        active: Optional[bool] = None,
        page_size: int = 100,
    ) -> str:
        """
        Search for studies.

        Studies are specific field experiments within trials where observations
        are recorded. Use this to find studies and get studyDbId for
        retrieving observations.

        Args:
            trial_db_id: Filter by trial ID (get from search_trials)
            program_db_id: Filter by breeding program ID
            location_db_id: Filter by location ID
            common_crop_name: Filter by crop name
            study_name: Filter by study name (partial match)
            season_db_id: Filter by season ID
            active: Filter by active status (True/False)
            page_size: Maximum number of results (default 100)

        Returns:
            JSON array of studies with studyDbId, studyName, trialDbId, locationDbId, etc.
        """
        params = {"pageSize": page_size}
        if trial_db_id:
            params["trialDbId"] = trial_db_id
        if program_db_id:
            params["programDbId"] = program_db_id
        if location_db_id:
            params["locationDbId"] = location_db_id
        if common_crop_name:
            params["commonCropName"] = common_crop_name
        if study_name:
            params["studyName"] = study_name
        if season_db_id:
            params["seasonDbId"] = season_db_id
        if active is not None:
            params["active"] = str(active).lower()

        response = client.get("/studies", params=params)
        data = response.get("result", {}).get("data", [])
        return json.dumps(data, indent=2)

    @server.tool()
    def get_study_details(study_db_id: str) -> str:
        """
        Get detailed information about a specific study.

        Retrieves comprehensive study metadata including location details,
        seasons, contacts, experimental design, and more.

        Args:
            study_db_id: The unique study identifier (required)

        Returns:
            JSON object with full study details including:
            - studyDbId, studyName, studyDescription
            - trialDbId, programDbId
            - locationDbId, locationName
            - startDate, endDate
            - contacts, dataLinks
            - experimentalDesign, observationLevels
        """
        response = client.get(f"/studies/{study_db_id}")
        data = response.get("result", {})
        return json.dumps(data, indent=2)
