import requests
import json
import sys

def test_function_calling(query):
    """
    Test function calling with the given query
    
    Args:
        query: The query to test
    """
    url = "http://localhost:8000/api/v1/debug-function-call"
    
    payload = {
        "query": query
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        print("\n=== TEST RESULTS ===")
        print(f"Query: {result['query']}")
        print(f"\nResponse content: {result['response_content']}")
        print(f"\nHas function calls: {result['has_function_calls']}")
        
        if result['has_function_calls']:
            print("\nFunction calls:")
            for i, call in enumerate(result['function_calls']):
                print(f"  {i+1}. {call['name']}({json.dumps(call['arguments'])})")
            
            print("\nFunction results:")
            for i, res in enumerate(result['function_results']):
                if 'error' in res:
                    print(f"  {i+1}. ERROR: {res['error']}")
                else:
                    print(f"  {i+1}. RESULT: {json.dumps(res['result'])}")
        
        print("\nRaw response additional kwargs:")
        print(json.dumps(result['raw_response']['additional_kwargs'], indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_function_calling.py 'your query here'")
        sys.exit(1)
    
    query = sys.argv[1]
    test_function_calling(query) 