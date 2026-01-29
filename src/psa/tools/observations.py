"""Observation tools for BrAPI Phenotyping endpoints."""

import json
from typing import Optional

from fastmcp import FastMCP

from psa.client import BrAPIClient


def register_observation_tools(server: FastMCP, client: BrAPIClient) -> None:
    """Register observation tools with the MCP server."""

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
