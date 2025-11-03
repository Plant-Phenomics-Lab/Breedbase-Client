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
import os
import io
import pandas as pd
# import json
# from typing import Optional

# # Save original stdout for MCP protocol
# _original_stdout = sys.stdout

# # Redirect ALL prints to stderr during imports
# sys.stdout = sys.stderr

# Now import everything (prints won't corrupt MCP)
from mcp.server.fastmcp import FastMCP
from client import BrAPIClient

# Initialize client (prints go to stderr)
sweetpotatobase = BrAPIClient(
    base_url="https://sweetpotatobase.org/brapi/v2",
    username="JerryHYu",
    password="$B1dX*JC$D!SeYpF"
)

# Create MCP server
server = FastMCP("sweetpotatobasequery")

@server.tool()
def all_functions() -> str:
    """
    Use inherent funcitonality of the client to get a list of all possible endpoints
    """
    # Capture print output and return as string
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        sweetpotatobase.general_get(help=True)
        return captured.getvalue()
    finally:
        sys.stdout = old_stdout

@server.tool()
def specific_function(endpoint:str) -> str:
    """
    Get Data on a Specific Endpoint
    """
    # Capture print output and return as string
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        sweetpotatobase.general_get(help=endpoint)
        return captured.getvalue()
    finally:
        sys.stdout = old_stdout

@server.tool()
def general_get(service: str, 
                filepath: str = "",
                max_pages: int = 100,
                pagesize: int = 100) -> str:
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
        filepath = os.path.join(os.getcwd(),"Downloads")
    
    # Create directory if it doesn't exist
    os.makedirs(filepath, exist_ok=True)
    
    # Get the DataFrame
    df = sweetpotatobase.general_get(service=service,
                                     max_pages=max_pages,
                                     pagesize=pagesize)
    
    # Data Cleaning
    # Remove columns that are entirely NA
    df = df.dropna(axis=1, how='all')
    
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
    csv_path = os.path.join(filepath, f"{service}.csv")
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
