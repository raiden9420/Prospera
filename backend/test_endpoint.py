import requests
import json

def test_endpoint():
    url = "http://localhost:8000/api/visualize"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "sessionid=9999999999" # Use demo session ID
    }
    
    queries = [
        "Show investment portfolio",
        "Show spending trend last year",
        "Show spending by category last 3 months"
    ]
    
    for q in queries:
        data = {"query": q}
        print(f"\nTesting query: '{q}'...")
        try:
            response = requests.post(url, headers=headers, json=data)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                res_json = response.json()
                if "error" in res_json:
                    print(f"Result: Error - {res_json['error']}")
                else:
                    print(f"Result: Success - Chart Type: {res_json.get('chartType')}, Data Points: {len(res_json.get('data', []))}")
            else:
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint()
