"""Germplasm tools for BrAPI Germplasm endpoints."""

import json
from typing import Optional

from fastmcp import FastMCP

from psa.client import BrAPIClient


def register_germplasm_tools(server: FastMCP, client: BrAPIClient) -> None:
    """Register germplasm tools with the MCP server."""

    @server.tool()
    def search_germplasm(
        germplasm_name: Optional[str] = None,
        accession_number: Optional[str] = None,
        common_crop_name: Optional[str] = None,
        genus: Optional[str] = None,
        species: Optional[str] = None,
        page_size: int = 100,
    ) -> str:
        """
        Search for germplasm (plant genetic resources).

        Use this to find plant varieties, accessions, or breeding lines
        and get germplasmDbId for detailed information or pedigree queries.

        Args:
            germplasm_name: Filter by name (partial match)
            accession_number: Filter by accession number
            common_crop_name: Filter by crop name (e.g., "sweetpotato")
            genus: Filter by genus (e.g., "Ipomoea")
            species: Filter by species (e.g., "batatas")
            page_size: Maximum number of results (default 100)

        Returns:
            JSON array of germplasm with:
            - germplasmDbId, germplasmName
            - accessionNumber, defaultDisplayName
            - genus, species, commonCropName
            - instituteCode, instituteName
        """
        params = {"pageSize": page_size}
        if germplasm_name:
            params["germplasmName"] = germplasm_name
        if accession_number:
            params["accessionNumber"] = accession_number
        if common_crop_name:
            params["commonCropName"] = common_crop_name
        if genus:
            params["genus"] = genus
        if species:
            params["species"] = species

        response = client.get("/germplasm", params=params)
        data = response.get("result", {}).get("data", [])
        return json.dumps(data, indent=2)

    @server.tool()
    def get_germplasm_by_id(germplasm_db_id: str) -> str:
        """
        Get detailed information about a specific germplasm.

        Retrieves comprehensive germplasm data including taxonomy,
        origin, donors, attributes, and external references.

        Args:
            germplasm_db_id: The unique germplasm identifier (required)

        Returns:
            JSON object with full germplasm details including:
            - germplasmDbId, germplasmName, defaultDisplayName
            - accessionNumber, germplasmPUI
            - genus, species, subtaxa, commonCropName
            - biologicalStatusOfAccessionCode
            - countryOfOriginCode, instituteCode
            - donors, germplasmOrigin
            - synonyms, additionalInfo
        """
        response = client.get(f"/germplasm/{germplasm_db_id}")
        data = response.get("result", {})
        return json.dumps(data, indent=2)

    @server.tool()
    def get_pedigree(
        germplasm_db_id: Optional[str] = None,
        germplasm_name: Optional[str] = None,
        include_parents: bool = True,
        include_progeny: bool = False,
        pedigree_depth: int = 1,
        page_size: int = 100,
    ) -> str:
        """
        Get pedigree information for germplasm.

        Retrieves parent-child relationships and crossing history.
        Essential for understanding genetic background and planning crosses.

        Args:
            germplasm_db_id: Filter by germplasm ID
            germplasm_name: Filter by germplasm name
            include_parents: Include parent information (default True)
            include_progeny: Include progeny/offspring information (default False)
            pedigree_depth: Number of generations to include (default 1)
            page_size: Maximum number of results (default 100)

        Returns:
            JSON array of pedigree nodes with:
            - germplasmDbId, germplasmName
            - parents (list of parent germplasm with type: MALE/FEMALE)
            - progeny (list of offspring if include_progeny=True)
            - pedigreeString (text representation)
        """
        params = {
            "pageSize": page_size,
            "includeParents": str(include_parents).lower(),
            "includeProgeny": str(include_progeny).lower(),
            "pedigreeDepth": pedigree_depth,
        }
        if germplasm_db_id:
            params["germplasmDbId"] = germplasm_db_id
        if germplasm_name:
            params["germplasmName"] = germplasm_name

        response = client.get("/pedigree", params=params)
        data = response.get("result", {}).get("data", [])
        return json.dumps(data, indent=2)
