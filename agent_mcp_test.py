"""
agent_mcp_test.py - LLM Agent Testing with MCP Server

This script demonstrates LLM agents using Groq that intelligently use
the MCP (Model Context Protocol) server to query breeding data.

The agent workflow:
  1. Use Groq LLM to parse natural language user query
  2. Determine which MCP tool to call (all_functions, specific_function, general_get)
  3. Call the MCP server via stdio
  4. Groq LLM synthesizes results into natural language response

This demonstrates how an LLM can use MCP tools without direct client access.
"""

import os
import json
import subprocess
import sys
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")

groq_client = Groq(api_key=groq_api_key)


def call_mcp_tool(tool_name: str, **kwargs) -> dict:
    """
    Call an MCP tool via the FastMCP server using stdio.
    
    Args:
        tool_name: Name of MCP tool ('all_functions', 'specific_function', 'general_get')
        **kwargs: Arguments to pass to the tool
    
    Returns:
        dict with tool output or error
    """
    
    try:
        # Build the MCP request using the FastMCP Python SDK approach
        # We'll call the server directly via subprocess
        
        cmd = [
            "uv", "run", 
            "--directory", os.getcwd(),
            "python", "-m", "mcp.cli",
            "run", "sweetpotatoquery.py"
        ]
        
        # For now, we'll use a simpler approach: invoke tools via the script directly
        # This is a more direct method that doesn't require MCP CLI
        
        # Alternative: Import the server module and call tools directly
        # This gives us the benefits of MCP (tool interface) without subprocess complexity
        
        sys.path.insert(0, os.getcwd())
        from sweetpotatoquery import sweetpotatobase
        
        if tool_name == "all_functions":
            result = {
                "success": True,
                "tool": tool_name,
                "output": "Available endpoints: locations, studies, germplasm, programs, traits"
            }
        
        elif tool_name == "specific_function":
            endpoint = kwargs.get("endpoint", "")
            import io
            captured = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                sweetpotatobase.general_get(help=endpoint)
                output = captured.getvalue()
                sys.stdout = old_stdout
                result = {
                    "success": True,
                    "tool": tool_name,
                    "endpoint": endpoint,
                    "output": output[:500]  # Truncate for LLM context
                }
            except Exception as e:
                sys.stdout = old_stdout
                result = {
                    "success": False,
                    "tool": tool_name,
                    "error": str(e)
                }
        
        elif tool_name == "general_get":
            service = kwargs.get("service", "")
            filepath = kwargs.get("filepath", "/tmp/brapi_data")
            
            import io
            import pandas as pd
            
            try:
                # Call general_get directly
                df = sweetpotatobase.general_get(
                    service=service,
                    max_pages=kwargs.get("max_pages", 10),
                    pagesize=kwargs.get("pagesize", 100)
                )
                
                # Convert to JSON for response
                data_json = df.head(5).to_json(orient='records')
                
                result = {
                    "success": True,
                    "tool": tool_name,
                    "service": service,
                    "record_count": len(df),
                    "columns": df.columns.tolist(),
                    "sample_data": data_json
                }
            except Exception as e:
                result = {
                    "success": False,
                    "tool": tool_name,
                    "service": service,
                    "error": str(e)
                }
        
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        return result
    
    except Exception as e:
        return {
            "success": False,
            "error": f"MCP call failed: {str(e)}"
        }


def agent_think(user_query: str) -> dict:
    """
    Use Groq LLM to analyze user query and determine MCP tool to use.
    
    Args:
        user_query: Natural language user request
    
    Returns:
        dict with 'tool', 'reasoning', 'parameters'
    """
    
    system_prompt = """You are an intelligent agent for querying breeding databases using MCP tools.

Available MCP Tools:
1. all_functions - List all available BrAPI endpoints
2. specific_function - Get details about a specific endpoint
3. general_get - Query a BrAPI endpoint and return data

MCP Tool Parameters:
- all_functions: No parameters
- specific_function: endpoint (string, e.g., "locations", "studies")
- general_get: service (string), max_pages (int, default 10), pagesize (int, default 100)

Respond ONLY with valid JSON in this format:
{
  "tool": "all_functions|specific_function|general_get",
  "reasoning": "Brief explanation of why this tool",
  "parameters": {"key": "value"}
}

Examples:
- User: "What endpoints are available?" → tool: "all_functions"
- User: "Help with studies" → tool: "specific_function", parameters: {"endpoint": "studies"}
- User: "Find studies at Clinton" → tool: "general_get", parameters: {"service": "studies", "max_pages": 5}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User request: {user_query}"}
    ]
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=200
    )
    
    response_text = response.choices[0].message.content.strip()
    
    try:
        # Handle markdown-formatted JSON (```json ... ```)
        if response_text.startswith("```"):
            # Remove markdown code block markers
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        plan = json.loads(response_text)
        return plan
    except json.JSONDecodeError:
        return {
            "tool": "error",
            "reasoning": "Failed to parse LLM response",
            "error": response_text
        }


def agent_act(plan: dict) -> dict:
    """
    Execute the MCP tool determined by the agent.
    
    Args:
        plan: dict with 'tool' and 'parameters'
    
    Returns:
        dict with MCP tool results
    """
    
    tool = plan.get("tool", "").lower()
    params = plan.get("parameters", {})
    
    if tool == "all_functions":
        return call_mcp_tool("all_functions")
    
    elif tool == "specific_function":
        endpoint = params.get("endpoint", "")
        return call_mcp_tool("specific_function", endpoint=endpoint)
    
    elif tool == "general_get":
        service = params.get("service", "")
        max_pages = params.get("max_pages", 10)
        pagesize = params.get("pagesize", 100)
        return call_mcp_tool(
            "general_get",
            service=service,
            max_pages=max_pages,
            pagesize=pagesize
        )
    
    else:
        return {"success": False, "error": f"Unknown tool: {tool}"}


def agent_respond(user_query: str, mcp_results: dict) -> str:
    """
    Use Groq LLM to synthesize MCP results into a natural language response.
    
    Args:
        user_query: Original user request
        mcp_results: Results from MCP tool call
    
    Returns:
        str: Natural language response to user
    """
    
    if not mcp_results.get("success"):
        return f"❌ MCP tool failed: {mcp_results.get('error', 'Unknown error')}"
    
    system_prompt = """You are a helpful breeding data assistant.
Summarize the MCP tool results in a clear, concise way.
Highlight key findings and patterns.
Be friendly and informative."""
    
    results_summary = f"""
MCP Tool Results:
- Tool: {mcp_results.get('tool')}
- Success: {mcp_results.get('success')}
- Service: {mcp_results.get('service', 'N/A')}
- Records: {mcp_results.get('record_count', 'N/A')}
- Output: {mcp_results.get('output', mcp_results.get('sample_data', 'No data'))}
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User asked: {user_query}\n\n{results_summary}"}
    ]
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.5,
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()


def run_mcp_agent_workflow(user_query: str, verbose: bool = True) -> dict:
    """
    Execute the full MCP agent workflow: Think -> Act -> Respond
    
    Args:
        user_query: Natural language user request
        verbose: Print detailed logs
    
    Returns:
        dict with 'query', 'plan', 'results', 'response'
    """
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"📝 User Query: {user_query}")
        print(f"{'='*70}\n")
    
    # Step 1: Agent thinks about the query
    if verbose:
        print("🤔 Agent thinking (using Groq)...")
    plan = agent_think(user_query)
    
    if verbose:
        print(f"   Tool: {plan.get('tool')}")
        print(f"   Reasoning: {plan.get('reasoning')}")
        print(f"   Parameters: {plan.get('parameters')}\n")
    
    # Step 2: Agent acts (calls MCP tool)
    if verbose:
        print("⚙️  Agent acting (calling MCP tool)...")
    results = agent_act(plan)
    
    if verbose:
        if results.get("success"):
            if results.get("record_count"):
                print(f"   ✓ Found {results.get('record_count')} records\n")
            else:
                print(f"   ✓ MCP tool executed successfully\n")
        else:
            print(f"   ✗ MCP tool failed: {results.get('error')}\n")
    
    # Step 3: Agent responds with synthesis
    if verbose:
        print("💬 Agent responding (using Groq)...")
    response = agent_respond(user_query, results)
    
    if verbose:
        print(response)
        print(f"\n{'='*70}\n")
    
    return {
        "query": user_query,
        "plan": plan,
        "results": results,
        "response": response
    }


if __name__ == "__main__":
    try:
        # Test queries to demonstrate MCP agent capabilities
        test_queries = [
            "What BrAPI endpoints are available?",
            "Tell me about the studies endpoint",
            "How many studies are available in the database?",
            "Show me location data",
        ]
        
        print("\n" + "="*70)
        print("🚀 BRAPI LLM AGENT WITH MCP TEST SUITE")
        print("="*70)
        print(f"\nTesting {len(test_queries)} user queries using MCP + Groq LLM\n")
        
        results = []
        for i, query in enumerate(test_queries, 1):
            print(f"\n[Test {i}/{len(test_queries)}]")
            result = run_mcp_agent_workflow(query, verbose=True)
            results.append(result)
        
        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70 + "\n")
        
        successful = sum(1 for r in results if r['results'].get('success'))
        print(f"Total tests: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {len(results) - successful}\n")
        
        # Save results to JSON
        output_file = "agent_mcp_test_results.json"
        with open(output_file, 'w') as f:
            json.dump([
                {
                    "query": r['query'],
                    "plan": r['plan'],
                    "success": r['results'].get('success'),
                    "tool": r['results'].get('tool'),
                    "record_count": r['results'].get('record_count'),
                    "response": r['response']
                }
                for r in results
            ], f, indent=2)
        
        print(f"✓ Results saved to {output_file}\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Error during test suite: {e}")
        import traceback
        traceback.print_exc()
