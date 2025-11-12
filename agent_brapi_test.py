"""
agent_brapi_test.py - LLM Agent Testing Framework

This script demonstrates LLM agents using Groq that intelligently use
the BrAPIClient to answer user queries about breeding data.

The agent can:
  1. Parse user natural language requests
  2. Determine which BrAPI endpoints to query
  3. Execute queries with appropriate filters
  4. Synthesize and present results

Test Cases:
  - Find studies at a specific location
  - Find germplasm by crop name
  - List available breeding programs
  - Search for specific traits
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq
from client import BrAPIClient

# Load environment variables
load_dotenv()

# Initialize clients
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")

groq_client = Groq(api_key=groq_api_key)

brapi_client = BrAPIClient(
    base_url="https://sweetpotatobase.org/brapi/v2",
    username=os.getenv("SWEETPOTATOBASE_USERNAME"),
    password=os.getenv("SWEETPOTATOBASE_PASSWORD")
)


def query_brapi(service: str, params: dict = None) -> dict:
    """
    Execute a BrAPI query and return results as a dict.
    
    Args:
        service: BrAPI service endpoint (e.g., 'locations', 'studies', 'germplasm')
        params: Optional filter parameters
    
    Returns:
        dict with 'success', 'count', 'data', and 'columns'
    """
    try:
        import pandas as pd
        
        df = brapi_client.general_get(
            service=service,
            params=params or {},
            dataframe=True,
            max_pages=100,
            pagesize=100
        )
        
        return {
            "success": True,
            "service": service,
            "count": len(df),
            "columns": df.columns.tolist(),
            "data": df.head(5),  # Return first 5 rows for context
            "data_json": df.head(5).to_json(orient='records')
        }
    except Exception as e:
        return {
            "success": False,
            "service": service,
            "error": str(e)
        }


def agent_think(user_query: str, context: str = "") -> dict:
    """
    Use Groq LLM to analyze user query and determine action plan.
    
    Args:
        user_query: Natural language user request
        context: Optional context about previous interactions
    
    Returns:
        dict with 'action', 'reasoning', 'parameters'
    """
    
    system_prompt = """You are an intelligent agent for querying breeding databases using BrAPI.

Available actions:
1. query_studies - Get breeding studies (can filter by locationDbId, studyType)
2. query_locations - Get available research locations
3. query_germplasm - Get germplasm accessions (can filter by commonCropName)
4. query_programs - Get breeding programs
5. query_traits - Get available trait definitions

Respond ONLY with valid JSON in this format:
{
  "action": "query_studies|query_locations|query_germplasm|query_programs|query_traits",
  "reasoning": "Brief explanation of why this action",
  "parameters": {"key": "value"}
}

For studies at a location, you'll need to:
1. First query locations to find the location ID
2. Then query studies with that location ID

Be concise and direct."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User request: {user_query}\n\nContext: {context or 'None'}"}
    ]
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=200
    )
    
    response_text = response.choices[0].message.content.strip()
    
    try:
        plan = json.loads(response_text)
        return plan
    except json.JSONDecodeError:
        return {
            "action": "error",
            "reasoning": "Failed to parse LLM response",
            "error": response_text
        }


def agent_act(plan: dict) -> dict:
    """
    Execute the action plan determined by the agent.
    
    Args:
        plan: dict with 'action' and 'parameters'
    
    Returns:
        dict with query results
    """
    
    action = plan.get("action", "").lower()
    params = plan.get("parameters", {})
    
    if action == "query_locations":
        return query_brapi("locations", params)
    
    elif action == "query_studies":
        return query_brapi("studies", params)
    
    elif action == "query_germplasm":
        return query_brapi("germplasm", params)
    
    elif action == "query_programs":
        return query_brapi("programs", params)
    
    elif action == "query_traits":
        return query_brapi("traits", params)
    
    else:
        return {"success": False, "error": f"Unknown action: {action}"}


def agent_respond(user_query: str, query_results: dict) -> str:
    """
    Use Groq LLM to synthesize query results into a natural language response.
    
    Args:
        user_query: Original user request
        query_results: Results from query_brapi()
    
    Returns:
        str: Natural language response to user
    """
    
    if not query_results.get("success"):
        return f"❌ Unable to process your request: {query_results.get('error', 'Unknown error')}"
    
    system_prompt = """You are a helpful breeding data assistant. 
Summarize the query results in a clear, concise way.
Highlight key findings and patterns.
Be friendly and informative."""
    
    data_summary = f"""
Query Results:
- Service: {query_results.get('service')}
- Records found: {query_results.get('count')}
- Sample data: {query_results.get('data_json', 'N/A')}
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User asked: {user_query}\n\n{data_summary}"}
    ]
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.5,
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()


def run_agent_workflow(user_query: str, verbose: bool = True) -> dict:
    """
    Execute the full agent workflow: Think -> Act -> Respond
    
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
        print("🤔 Agent thinking...")
    plan = agent_think(user_query)
    
    if verbose:
        print(f"   Action: {plan.get('action')}")
        print(f"   Reasoning: {plan.get('reasoning')}")
        print(f"   Parameters: {plan.get('parameters')}\n")
    
    # Step 2: Agent acts (queries BrAPI)
    if verbose:
        print("⚙️  Agent acting (querying BrAPI)...")
    results = agent_act(plan)
    
    if verbose:
        if results.get("success"):
            print(f"   ✓ Found {results.get('count')} records\n")
        else:
            print(f"   ✗ Query failed: {results.get('error')}\n")
    
    # Step 3: Agent responds with synthesis
    if verbose:
        print("💬 Agent responding...")
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


# Test agent workflows below


if __name__ == "__main__":
    try:
        import pandas as pd
        
        # Test queries to demonstrate agent capabilities
        test_queries = [
            "Find all studies at Clinton Research Station",
            "How many breeding programs are available?",
            "Show me germplasm for sweet potato",
            "What studies were done in 2024?",
        ]
        
        print("\n" + "="*70)
        print("🚀 BRAPI LLM AGENT TEST SUITE")
        print("="*70)
        print(f"\nTesting {len(test_queries)} user queries using Groq LLM\n")
        
        results = []
        for i, query in enumerate(test_queries, 1):
            print(f"\n[Test {i}/{len(test_queries)}]")
            result = run_agent_workflow(query, verbose=True)
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
        output_file = "agent_brapi_test_results.json"
        with open(output_file, 'w') as f:
            json.dump([
                {
                    "query": r['query'],
                    "plan": r['plan'],
                    "success": r['results'].get('success'),
                    "record_count": r['results'].get('count'),
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
