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
    return sweetpotatobase.show_services_to_llm()

@server.tool()
def specific_function(service:str,
                      DbID:bool = False,
                      Search:bool = False) -> dict:
    """
    Get Data on a Specific Service
    Args: DbID: Bolean for DbID, Search: For the search service of the service
    """
    if DbID:
        if Search:
            return f"Cannot be Both"
        else:
            params = sweetpotatobase.format_parameters_for_llm(f"{service}")
    if Search:
        params = sweetpotatobase.format_parameters_for_llm(f"search/{service}/{{searchResultsDbId}}")
    else:
        params = sweetpotatobase.format_parameters_for_llm(f"{service}")
    return params

@server.tool()
def service(service: str, 
            filepath: str = "",
            max_pages: int = 10,
            pagesize: int = 1) -> str:
    """
    Get and Save BrAPI data from a base endpoint as CSV

    Args:
        service: BrAPI service base endpoint name (e.g., 'locations', 'germplasm')
        filepath: Directory path to save CSV
        max_pages: Maximum number of pages to fetch
        pagesize: Number of results per page
    
    Returns:
        Summary string with statistics about the data
    """
    if not filepath:
        raise ValueError("Please Specify a Filepath")
    
    filepath = Path(filepath)
    filepath.mkdir(parents=True, exist_ok=True)
    
    # Get the DataFrame
    df, metadata = sweetpotatobase.general_get(
        service=service,
        DbID=False,
        search=False,
        max_pages=max_pages,
        pagesize=pagesize
    )
    
    # Data Cleaning
    df = df.dropna(axis=1, how='all')
    # Save cleaned CSV
    csv_path = filepath / f"{service}_{metadata["time"]}.csv"

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        # Write metadata as comments
        f.write(f"# Metadata\n")
        f.write(f"# totalCount: {metadata['totalCount']}\n")
        f.write(f"# timestamp: {metadata['time']}\n")
        f.write(f"# service: {service}\n")
        f.write(f"#\n")
        
        # Write the actual CSV data
        df.to_csv(f, index=False)
    
    summary = f"""Data saved to: {csv_path}

Summary Statistics:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Total Count: {metadata['totalCount']}"""

    return summary


@server.tool()
def service_by_id(service: str,
                  id: str,
                  filepath: str = "",
                  max_pages: int = 10,
                  pagesize: int = 1) -> str:
    """
    Get and Save a specific BrAPI resource by its database ID as CSV

    Args:
        service: BrAPI service base endpoint name (e.g., 'locations', 'germplasm')
        id: Database ID of the specific resource
        filepath: Directory path to save CSV
        max_pages: Maximum number of pages to fetch
        pagesize: Number of results per page
    
    Returns:
        Summary string with statistics about the data
    """
    if not filepath:
        raise ValueError("Please Specify a Filepath")
    
    filepath = Path(filepath)
    filepath.mkdir(parents=True, exist_ok=True)
    
    # Get the DataFrame
    df, metadata = sweetpotatobase.general_get(
        service=service,
        DbID=id,
        search=False,
        max_pages=max_pages,
        pagesize=pagesize
    )
    
    # Data Cleaning
    df = df.dropna(axis=1, how='all')
    
    # Generate timestamp for filename
    csv_path = filepath / f"{service}_{id}.csv"

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        # Write metadata as comments
        f.write(f"# Metadata\n")
        f.write(f"# totalCount: {metadata['totalCount']}\n")
        f.write(f"# timestamp: {metadata['time']}\n")
        f.write(f"# DbID: {id}\n")
        f.write(f"#\n")
        
        # Write the actual CSV data
        df.to_csv(f, index=False)
    
    summary = f"""Data saved to: {csv_path}

Summary Statistics:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Total Count: {metadata['totalCount']}
- Resource ID: {id}"""

    return summary


@server.tool()
def search_service(service: str,
                   params: dict,
                   filepath: str = "",
                   max_pages: int = 1,
                   pagesize: int = 10,
                   validate: bool = True) -> str:
    """
    Search and filter BrAPI data using search parameters, save as CSV

    Args:
        service: BrAPI service base endpoint name (e.g., 'locations', 'studies')
        params: Dictionary of search parameters (e.g., {"locationTypes": ["Lab"], "countryCodes": ["USA"]})
        filepath: Directory path to save CSV
        max_pages: Maximum number of pages to fetch
        pagesize: Number of results per page
        validate: Validate parameters against endpoint schema
    
    Returns:
        Summary string with statistics about the data
    """
    if not filepath:
        raise ValueError("Please Specify a Filepath")
    
    if not params:
        raise ValueError("Search requires parameters. Provide a params dictionary.")
    
    filepath = Path(filepath)
    filepath.mkdir(parents=True, exist_ok=True)
    
    # Get the DataFrame
    df, metadata = sweetpotatobase.general_get(
        service=service,
        search=True,
        params=params,
        validate=validate,
        max_pages=max_pages,
        pagesize=pagesize
    )
    
    # Data Cleaning
    df = df.dropna(axis=1, how='all')
    
    # Generate timestamp and param hash for filename
    timestamp = metadata['time']
    # Create readable filename from key params
    csv_path = filepath / f"{service}_search_{timestamp}.csv"

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        # Write metadata as comments
        f.write(f"# Metadata\n")
        f.write(f"# totalCount: {metadata['totalCount']}\n")
        f.write(f"# timestamp: {metadata['time']}\n")
        f.write(f"# search: True\n")
        f.write(f"# params: {params}\n")
        f.write(f"#\n")
        
        # Write the actual CSV data
        df.to_csv(f, index=False)
    
    summary = f"""Data saved to: {csv_path}

Summary Statistics:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Total Count: {metadata['totalCount']}"""

    return summary


@server.tool()
def get_images(params: dict = None,
               filepath: str = "",
               max_pages: int = 10,
               pagesize: int = 10,
               download_images: bool = True) -> str:
    """
    Get image metadata and optionally download the actual image files

    Args:
        params: Optional search parameters for filtering images
        filepath: Directory path to save CSV and images
        max_pages: Maximum number of pages to fetch
        pagesize: Number of results per page
        download_images: If True, downloads actual image files; if False, only saves metadata CSV
    
    Returns:
        Summary string with statistics about the images
    """
    if not filepath:
        raise ValueError("Please Specify a Filepath")
    
    filepath = Path(filepath)
    filepath.mkdir(parents=True, exist_ok=True)
    
    # Get the DataFrame
    if params:
        df, metadata = sweetpotatobase.general_get(
            service='images',
            search=True,
            params=params,
            max_pages=max_pages,
            pagesize=pagesize
        )
    else:
        df, metadata = sweetpotatobase.general_get(
            service='images',
            search=False,
            max_pages=max_pages,
            pagesize=pagesize
        )
    
    # Data Cleaning
    df = df.dropna(axis=1, how='all')

    # Download actual image files if requested
    downloaded_count = 0
    if download_images and 'imageURL' in df.columns:
        images_dir = filepath / "downloaded_images"
        images_dir.mkdir(exist_ok=True)
        
        for index, row in df.iterrows():
            if pd.notna(row.get('imageURL')):
                image_url = row['imageURL']
                # Extract filename from URL and get extension
                url_filename = image_url.split('/')[-1]  # e.g., "medium.jpg"
                file_extension = Path(url_filename).suffix  # e.g., ".jpg"
                
                # Use imageFileName from data, add extension
                base_filename = str(row.get('imageFileName', f"image_{index}"))
                image_filename = f"{base_filename}{file_extension}"
                image_path = images_dir / image_filename
                
                try:
                    response = requests.get(image_url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    with open(image_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    downloaded_count += 1
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {image_filename}: {e}")

    # Save metadata CSV
    csv_path = filepath / f"images_{metadata['time']}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        # Write metadata as comments
        f.write(f"# Metadata\n")
        f.write(f"# totalCount: {metadata['totalCount']}\n")
        f.write(f"# timestamp: {str(metadata['time'])}\n")
        f.write(f"# service: images\n")
        if params:
            f.write(f"# search_params: {params}\n")
        if download_images:
            f.write(f"# images_downloaded: {downloaded_count}\n")
        f.write(f"#\n")
        
        # Write the actual CSV data
        df.to_csv(f, index=False)
    
    summary = f"""Data saved to: {csv_path}

Summary Statistics:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Total Count: {metadata['totalCount']}"""
    
    if download_images:
        summary += f"\n- Images Downloaded: {downloaded_count} / {len(df)}"
        summary += f"\n- Images saved to: {images_dir}"

    return summary

# @server.tool()
# def general_get(service: str, 
#                 filepath: str = "",
#                 max_pages: int = 100,
#                 pagesize: int = 100,
#                 DbID = False,
#                 search=False,
#                 params:dict = None) -> str:
#     """
#     Get and Save BrAPI data Endpoints as CSVs
    
#     Args:
#         service: BrAPI service endpoint name (e.g., 'locations', 'germplasm')
#         filepath: Optional directory path to save CSV. If empty, uses default.
    
#     Returns:
#         Summary string with statistics about the data
#     """
    
#     # Set default filepath if not provided
#     if not filepath:
#         raise ValueError("Please Specify a Filepath")
    
#     filepath = Path(filepath)
#     # Create directory if it doesn't exist
#     filepath.mkdir(parents=True,exist_ok=True)
    
#     # Get the DataFrame
#     df = sweetpotatobase.general_get(service=service,
#                                      DbID = DbID,
#                                      search=search,
#                                      params=params,
#                                      max_pages=max_pages,
#                                      pagesize=pagesize)
    
#     # Data Cleaning
#     # Remove columns that are entirely NA
#     df = df.dropna(axis=1, how='all')

#     if service == 'images':
#         for index, row in df.iterrows():
#             image_name = str(row['imageName'])
#             image_url = row['imageURL']
#             image_path = str(filepath) + image_name
#             image_url = row['imageURL']
#             try:
#                 response = requests.get(image_url, stream=True)
#                 response.raise_for_status()

#                 with open(image_path, 'wb') as f:
#                     for chunk in response.iter_content(chunk_size=8192):
#                         f.write(chunk)

#             except requests.exceptions.RequestException as e:
#                 print(f"Error downloading image: {e}")
    
#     # # Convert lists and dicts to JSON strings for CSV compatibility
#     # for col in df.columns:
#     #     if df[col].dtype == 'object':
#     #         def safe_convert(x):
#     #             if pd.isna(x):
#     #                 return x
#     #             if isinstance(x, (list, dict)):
#     #                 # Convert to JSON string for CSV compatibility
#     #                 return json.dumps(x)
#     #             return x
            
#     #         df[col] = df[col].apply(safe_convert)
    
# #     # Remove columns with only empty lists and dicts
# #     cols_to_drop = []
# #     for col in df.columns:
# #         if df[col].dtype == 'object':
# #             def is_empty(x):
# #                 if pd.isna(x):
# #                     return True
# #                 if isinstance(x, str):
# #                     return x in ['[]', '{}', '']
# #                 return False
            
# #             # Remove if all values are empty
# #             if df[col].apply(is_empty).all():
# #                 cols_to_drop.append(col)
    
# #     if cols_to_drop:
# #         df = df.drop(columns=cols_to_drop)
    
#     # Save cleaned CSV
#     csv_path = filepath / f"{service}.csv"
#     df.to_csv(csv_path, index=False)
    
# #     # Generate summary
# #     null_columns = df.columns[df.isnull().any()].tolist()
    
#     summary = f"""
# Data saved to: {csv_path}

# Summary Statistics:
# - Rows: {len(df)}
# - Columns: {len(df.columns)}

# Data types:
# """
    
    return summary

@server.prompt()
def tutorial() -> str:
    """
    Best Practices for Using BrAPI
    """
    return f"Use `all_functions` first in every chat to check which endpoints are avalible. \n - Use `specific_function` when you first try to call an endpoint always. Use`service` to get unfiltered data, `service_by_id` for service by a single database ID, `search_service` for services to search, and `get_images` for getting images" 

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
