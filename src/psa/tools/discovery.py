"""Discovery tools for BrAPI Core endpoints."""

import json
from typing import Optional

from fastmcp import FastMCP

from psa.client import BrAPIClient


def register_discovery_tools(server: FastMCP, client: BrAPIClient) -> None:
    """Register discovery tools with the MCP server."""

    @server.tool()
    def list_programs(
        program_name: Optional[str] = None,
        common_crop_name: Optional[str] = None,
        page_size: int = 100,
    ) -> str:
        """
        List available breeding programs.

        Use this to discover breeding programs and get programDbId values
        for filtering trials and studies.

        Args:
            program_name: Filter by program name (partial match)
            common_crop_name: Filter by crop name (e.g., "sweetpotato")
            page_size: Maximum number of results (default 100)

        Returns:
            JSON array of programs with programDbId, programName, etc.
        """
        params = {"pageSize": page_size}
        if program_name:
            params["programName"] = program_name
        if common_crop_name:
            params["commonCropName"] = common_crop_name

        response = client.get("/programs", params=params)
        data = response.get("result", {}).get("data", [])
        return json.dumps(data, indent=2)

    @server.tool()
    def list_locations(
        location_name: Optional[str] = None,
        location_type: Optional[str] = None,
        country_code: Optional[str] = None,
        page_size: int = 100,
    ) -> str:
        """
        List available locations.

        Use this to discover field locations and get locationDbId values
        for filtering trials and studies.

        Args:
            location_name: Filter by location name (partial match)
            location_type: Filter by type (e.g., "Field", "Greenhouse")
            country_code: Filter by ISO 3166-1 alpha-3 country code
            page_size: Maximum number of results (default 100)

        Returns:
            JSON array of locations with locationDbId, locationName, countryCode, etc.
        """
        params = {"pageSize": page_size}
        if location_name:
            params["locationName"] = location_name
        if location_type:
            params["locationType"] = location_type
        if country_code:
            params["countryCode"] = country_code

        response = client.get("/locations", params=params)
        data = response.get("result", {}).get("data", [])
        return json.dumps(data, indent=2)

    @server.tool()
    def list_seasons(
        year: Optional[str] = None,
        season_name: Optional[str] = None,
        page_size: int = 100,
    ) -> str:
        """
        List available seasons.

        IMPORTANT: Use this tool when users ask about years, dates, or time
        periods. In plant breeding, data is organized by growing SEASON
        (typically a year like "2023", "2024"). This tool shows what seasons
        have data available. Use the returned seasonDbId (often equals year)
        with search_studies to find studies from specific seasons.

        Args:
            year: Filter by year (e.g., "2023")
            season_name: Filter by season name (e.g., "Spring", "Fall")
            page_size: Maximum number of results (default 100)

        Returns:
            JSON array of seasons with seasonDbId, season, year, etc.
        """
        params = {"pageSize": page_size}
        if year:
            params["year"] = year
        if season_name:
            params["seasonName"] = season_name

        response = client.get("/seasons", params=params)
        data = response.get("result", {}).get("data", [])
        return json.dumps(data, indent=2)

    @server.tool()
    def search_trials(
        program_db_id: Optional[str] = None,
        location_db_id: Optional[str] = None,
        common_crop_name: Optional[str] = None,
        trial_name: Optional[str] = None,
        active: Optional[bool] = None,
        page_size: int = 100,
    ) -> str:
        """
        Search for trials (experiments).

        Trials are collections of studies testing specific hypotheses.
        Use this to find trials and get trialDbId for querying studies.

        NOTE ON TIME-BASED QUERIES: When users ask for data by year, date, or
        time period, they are asking about growing SEASONS. Use list_seasons
        to find available seasons, then use search_studies with the year
        parameter to find studies from that season. Trial names often include
        the year (e.g., "2024_season") but this endpoint does not support
        year/season filtering directly.

        Args:
            program_db_id: Filter by breeding program ID
            location_db_id: Filter by location ID
            common_crop_name: Filter by crop name
            trial_name: Filter by exact trial name (e.g., "2024_season")
            active: Filter by active status (True/False)
            page_size: Maximum number of results (default 100)

        Returns:
            JSON array of trials with trialDbId, trialName, programDbId, etc.
        """
        params = {"pageSize": page_size}
        if program_db_id:
            params["programDbId"] = program_db_id
        if location_db_id:
            params["locationDbId"] = location_db_id
        if common_crop_name:
            params["commonCropName"] = common_crop_name
        if trial_name:
            params["trialName"] = trial_name
        if active is not None:
            params["active"] = str(active).lower()

        response = client.get("/trials", params=params)
        data = response.get("result", {}).get("data", [])
        return json.dumps(data, indent=2)
