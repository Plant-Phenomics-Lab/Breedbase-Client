"""
Helper Tools for MCP Wofkflows

Version: 0.0.0
Last Updated: 2024-11-3
Author: Jerry Yu
"""

import sys
import os
import io
import shutil
import subprocess
import json
# import pandas as pd

# # Save original stdout for MCP protocol
# _original_stdout = sys.stdout

# # Redirect ALL prints to stderr during imports
# sys.stdout = sys.stderr

# Now import everything (prints won't corrupt MCP)
from mcp.server.fastmcp import FastMCP

# Create MCP server
server = FastMCP("basic_helper")


def create_folder_structure(root:str=None):
    if os.path.exists(root):
        # Create directory structure
        dirs = [
            os.path.join(root, "Data", "Raw"),
            os.path.join(root, "Data", "Processed")
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        # Create scratchpad markdown file (OUTSIDE the loop)
        scratchpad_path = os.path.join(root, "scratchpad.md")
        if not os.path.exists(scratchpad_path):
            with open(scratchpad_path, 'w') as f:
                f.write("# Scratchpad\n\n"
                        "## File Paths\n"
                        "You are a helpful Data Analysis Agent. Your working directories are:\n"
                        f"- Root: {root}\n"
                        f"- Raw Data: {os.path.join(root, 'Data', 'Raw')}\n"
                        f"- Processed Data: {os.path.join(root, 'Data', 'Processed')}\n"
                        f"Write your notes to the scratchpad file here: {os.path.join(root, "scratchpad.md")}")
    else:
        os.mkdir(root)
        create_folder_structure(root)

# def start_jupyter_server(root: str = None, 
#                         env_name: str = "jupytermcp",
#                         port: int = 8888, 
#                         token: str = "MY_TOKEN") -> dict:
#     """
#     Start Jupyter Lab server with conda environment
    
#     Args:
#         root: Root directory to start Jupyter in (optional)
#         env_name: Conda environment name (default: jupytermcp)
#         port: Port number for Jupyter Lab (default: 8888)
#         token: Authentication token (default: MY_TOKEN)
    
#     Returns:
#         Dictionary with server info and PID
#     """
#     # Build command with conda activation
#     if root:
#         # Change to root directory first
#         cmd = f'cd /d "{root}" && conda activate {env_name} && jupyter lab --port {port} --IdentityProvider.token {token} --ip 0.0.0.0'
#     else:
#         cmd = f'conda activate {env_name} && jupyter lab --port {port} --IdentityProvider.token {token} --ip 0.0.0.0'
    
#     try:
#         # Start Jupyter Lab in background (non-blocking)
#         process = subprocess.Popen(
#             cmd,
#             shell=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             creationflags=subprocess.CREATE_NEW_CONSOLE  # Open in new window on Windows
#         )
        
#         return {
#             "status": "started",
#             "pid": process.pid,
#             "port": port,
#             "url": f"http://localhost:{port}/?token={token}",
#             "environment": env_name,
#             "working_directory": root or os.getcwd()
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "error": str(e)
#         }

# @server.tool()
# def initial_workflow(root:str=None,
#                      overwrite:bool = False,
#                      start_jupyter: bool = True,
#                      env_name: str = "jupytermcp",
#                      jupyter_port: int = 8888,
#                      jupyter_token: str = "MY_TOKEN") -> str:
#     """
#     Initialize project workflow: create folder structure and optionally start Jupyter
    
#     Args:
#         root: Root directory for the project
#         overwrite: If True, delete and recreate existing directory
#         start_jupyter: If True, start Jupyter Lab server
#         env_name: Conda environment for Jupyter
#         jupyter_port: Port for Jupyter Lab
#         jupyter_token: Authentication token for Jupyter
#     """
#     if not root:
#         raise ValueError("Root Directory Not Specified")
    
#     if overwrite:
#         shutil.rmtree(root)
#         os.mkdir(root)
    
#     create_folder_structure(root)
    
#     response = f"Folder Structure Set Up at {root}\n"
    
#     if start_jupyter:
#         jupyter_info = start_jupyter_server(root, env_name, jupyter_port, jupyter_token)
#         if jupyter_info["status"] == "started":
#             response += f"\nJupyter Lab started!\n"
#             response += f"URL: {jupyter_info['url']}\n"
#             response += f"Environment: {jupyter_info['environment']}\n"
#             response += f"PID: {jupyter_info['pid']}"
#         else:
#             response += f"\nError starting Jupyter: {jupyter_info.get('error', 'Unknown error')}"
    
#     return response

                    
