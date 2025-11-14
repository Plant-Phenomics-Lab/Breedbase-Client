"""
SweetPotatoBase MCP

This MCP (Model Context Protocol) server provides AI agents with tools to query
the SweetPotatoBase BrAPI endpoints and retrieve breeding data.

Version: 0.1.0
Last Updated: 2024-11-3
Author: Jerry Yu

Changelog:
- 0.0.0 (2024-10-29): Initial MCP server implementation
  * Added all_functions() to list available endpoints
  * Added specific_function() to get endpoint details
  * Added general_get() to query and save BrAPI data as CSV
  * Integrated with BrAPIClient for OAuth authentication
"""

#!/usr/bin/env python3
import sys
# import os
from pathlib import Path
import io
import pandas as pd
# import json
# from typing import Optional

# Now import everything (prints won't corrupt MCP)
import os
from dotenv import load_dotenv
from auths import create_sgn_session
from mcp.server.fastmcp import FastMCP
from client_dev import BrAPIClient_dev
import requests

# Load environment variables from .env file
load_dotenv()

# Now Sweetpotatobase
# Auth Session
sweetpotatobase = create_sgn_session(
    base_url="https://sweetpotatobase.org",
    auto_login=True,
    username=os.getenv("SWEETPOTATOBASE_USERNAME"),
    password=os.getenv("SWEETPOTATOBASE_PASSWORD")
)
# Client Session
sweetpotatobase = BrAPIClient_dev(base_url="https://sweetpotatobase.org/brapi/v2",
                         session=sweetpotatobase)

# Initialize client (prints go to stderr)
# sweetpotatobase = BrAPIClient_dev(
#     base_url="https://sweetpotatobase.org/brapi/v2",
#     username=os.getenv("SWEETPOTATOBASE_USERNAME"),
#     password=os.getenv("SWEETPOTATOBASE_PASSWORD")
# )

# Create MCP server
server = FastMCP("sweetpotatobasequery")

@server.tool()
def all_functions() -> dict:
    """
    Use inherent funcitonality of the client to get a list of all possible endpoints
    """
    # Capture print output and return as string
    # captured = io.StringIO()
    # old_stdout = sys.stdout
    # sys.stdout = captured
    # try:
    #     sweetpotatobase.show_services_to_llm()
    #     return captured.getvalue()
    # finally:
    #     sys.stdout = old_stdout
    return sweetpotatobase.show_services_to_llm()

@server.tool()
def specific_function(service:str,
                      DbID:bool = False,
                      Search:bool = False) -> str:
    """
    Get Data on a Specific Service
    Args: DbID: Bolean for DbID, Search: For the search service of the service
    """
    # Capture print output and return as string
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        if DbID:
            if Search:
                return f"Cannot be Both"
            else:
                sweetpotatobase.general_get(help=f"{service}")
                return captured.getvalue()
        if Search:
            sweetpotatobase.general_get(help=f"search/{service}/{{searchResultsDbId}}")
            captured.getvalue()
        else:
            sweetpotatobase.general_get(help=service)
        return captured.getvalue()
    finally:
        sys.stdout = old_stdout

@server.tool()
def general_get(service: str, 
                filepath: str = "",
                max_pages: int = 100,
                pagesize: int = 100,
                DbID = False,
                search=False,
                params:dict = None) -> str:
    """
    Get and Save BrAPI data Endpoints as CSVs
    
    Args:
        service: BrAPI service endpoint name (e.g., 'locations', 'germplasm')
        filepath: Optional directory path to save CSV. If empty, uses default.
    
    Returns:
        Summary string with statistics about the data
    """
    
    # Set default filepath if not provided
    if not filepath:
        raise ValueError("Please Specify a Filepath")
    
    filepath = Path(filepath)
    # Create directory if it doesn't exist
    filepath.mkdir(parents=True,exist_ok=True)
    
    # Get the DataFrame
    df = sweetpotatobase.general_get(service=service,
                                     DbID = DbID,
                                     search=search,
                                     params=params,
                                     max_pages=max_pages,
                                     pagesize=pagesize)
    
    # Data Cleaning
    # Remove columns that are entirely NA
    df = df.dropna(axis=1, how='all')

    if service == 'images':
        for index, row in df.iterrows():
            image_name = str(row['imageName'])
            image_url = row['imageURL']
            image_path = str(filepath) + image_name
            image_url = row['imageURL']
            try:
                response = requests.get(image_url, stream=True)
                response.raise_for_status()

                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            except requests.exceptions.RequestException as e:
                print(f"Error downloading image: {e}")
    
    # # Convert lists and dicts to JSON strings for CSV compatibility
    # for col in df.columns:
    #     if df[col].dtype == 'object':
    #         def safe_convert(x):
    #             if pd.isna(x):
    #                 return x
    #             if isinstance(x, (list, dict)):
    #                 # Convert to JSON string for CSV compatibility
    #                 return json.dumps(x)
    #             return x
            
    #         df[col] = df[col].apply(safe_convert)
    
#     # Remove columns with only empty lists and dicts
#     cols_to_drop = []
#     for col in df.columns:
#         if df[col].dtype == 'object':
#             def is_empty(x):
#                 if pd.isna(x):
#                     return True
#                 if isinstance(x, str):
#                     return x in ['[]', '{}', '']
#                 return False
            
#             # Remove if all values are empty
#             if df[col].apply(is_empty).all():
#                 cols_to_drop.append(col)
    
#     if cols_to_drop:
#         df = df.drop(columns=cols_to_drop)
    
    # Save cleaned CSV
    csv_path = filepath / f"{service}.csv"
    df.to_csv(csv_path, index=False)
    
#     # Generate summary
#     null_columns = df.columns[df.isnull().any()].tolist()
    
    summary = f"""
Data saved to: {csv_path}

Summary Statistics:
- Rows: {len(df)}
- Columns: {len(df.columns)}

Data types:
"""
    
    return summary

@server.prompt()
def tutorial() -> str:
    """
    Best Practices for Using BrAPI
    """
    return f"Use `all_functions` first in every chat to check which endpoints are avalible. \n - Use `specific_function` when you first try to call an endpoint always."

@server.prompt()
def get_endpoints() -> str: 
    """
    how to find the right endpoint
    """
    return """Given the user's prompt, translate it into a valid endpoint structure.

Service Structure:
- service: The base endpoint name (e.g., 'locations', 'germplasm', 'studies')

Modifications:
- DbID: Use {service}/{serviceDbID} to get a specific item by ID
- search: Use search/{service}/{searchResultsDbId} with params dict to filter data

Examples:
- User: "Can you map all the locations for me?"
  Agent workflow:
    1. Call `all_functions` to see available endpoints
    2. Call `specific_function` for 'locations' to understand the endpoint
    3. Call `general_get` with service='locations' to retrieve data

- User: "Get location with ID LOC123"
  Endpoint: locations/LOC123

- User: "Search for studies in 2023"
  Endpoint: search/studies/{searchResultsDbId} with params={'year': 2023}
"""

@server.resource("instruction://find_right_endpoints")
def get_right_endpoints() -> dict: 
    """
    Given the user's prompt, translate it into a valid endpoint structure.
    
    Service Structure:
    - service: The base endpoint name (e.g., 'locations', 'germplasm', 'studies')
    
    Modifications:
    - DbID: Use {service}/{serviceDbID} to get a specific item by ID
    - search: Use search/{service}/{searchResultsDbId} with params dict to filter data
    
    Examples:
    - User: "Can you map all the locations for me?"
      Agent workflow:
        1. Call `all_functions` to see available endpoints
        2. Call `specific_function` for 'locations' to understand the endpoint
        3. Call `general_get` with service='locations' to retrieve data
    
    - User: "Get location with ID LOC123"
      Endpoint: locations/LOC123
    
    - User: "Search for studies in 2023"
      Endpoint: search/studies/{searchResultsDbId} with params={'year': 2023}
    """
    return {
        "service": "",  # Base service name (e.g., 'locations', 'germplasm')
        "modifications": {
            "dbId": {
                "pattern": "{service}/{serviceDbID}",
                "description": "Find a specific item by database ID",
                "example": "locations/LOC123"
            },
            "search": {
                "pattern": "search/{service}/{searchResultsDbId}",
                "description": "Filter data using params dictionary",
                "example": "search/studies/SEARCH456",
                "params": {}  # Dictionary of search parameters
            }
        },
        "workflow": [
            "1. Call `all_functions` to check available endpoints",
            "2. Call `specific_function` to understand the endpoint structure",
            "3. Call `general_get` to retrieve the data"
        ]
    }

# filepath = "C:\\Users\\yujer\\L_Documents\\Current Classes\\BreedbaseCsvs"
# service = "locations"
# import pandas as pd
# csv = sweetpotatobase.general_get(service="locations")
# csv.isna().all(axis=0)
# csv.to_csv(f"{filepath}\\{service}.csv",index=False)
# csv.describe
# null_columns = csv.columns[csv.isnull().any()].tolist()
# print(null_columns)
# tempfile = pd.read_csv(sweetpotatobase.temp_endpoints_file.name)
# tempfile.columns
# tempfile[["service","category"]]

# Restore stdout for MCP JSON protocol
# sys.stdout = _original_stdout
if __name__ == "__main__":
    server.run()
