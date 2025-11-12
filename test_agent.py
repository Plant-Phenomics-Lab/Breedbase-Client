import os
import requests
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MCP Server URL
MCP_SERVER_URL = "http://127.0.0.1:8000"

# Initialize Groq Client
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")

groq_client = Groq(
    api_key=groq_api_key,
)

def call_mcp_tool(tool_name: str, params: dict) -> dict:
    """
    Calls a tool on the MCP server.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": tool_name,
        "params": params,
        "id": 1,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(MCP_SERVER_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling MCP tool {tool_name}: {e}")
        return None

def run_agent():
    """
    A simple agent that uses the MCP server to get data and Groq to process it.
    """
    print("Starting the test agent workflow...")

    # 1. Get the list of available tools from the MCP server
    print("Getting available tools from the MCP server...")
    response = call_mcp_tool("mcp.discovery.list_tools", {})
    if not response or "result" not in response:
        print("Could not get tools from MCP server. Exiting.")
        return
    
    tools = response["result"]
    print("Available tools:", [tool['name'] for tool in tools])


    # 2. Call the 'general_get' tool to get some data
    print("\nCalling 'general_get' tool to get attributes...")
    filepath = "Data/Raw/attributes"
    general_get_params = {"service": "attributes", "filepath": filepath}
    response = call_mcp_tool("general_get", general_get_params)

    if not response or "result" not in response:
        print("No data received from 'general_get' tool. Exiting.")
        return
    
    tool_output = response['result']
    print("Tool output:", tool_output)

    # 3. Use Groq to process the data
    print("\nProcessing tool output with Groq...")
    prompt = f"Summarize the following output from the 'general_get' tool:\n\n{tool_output}"

    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )

    summary = chat_completion.choices[0].message.content
    print("\nGroq Summary:\n", summary)

if __name__ == "__main__":
    run_agent()
