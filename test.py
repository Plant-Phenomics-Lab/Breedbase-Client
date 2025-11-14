import os
from client_dev import BrAPIClient_dev
import requests
import pandas as pd
import json
from dotenv import load_dotenv
from auths import create_sgn_session

# Now Sweetpotatobase
load_dotenv()
swesesh = create_sgn_session(
    base_url="https://sweetpotatobase.org",
    auto_login=True,
    username=os.getenv("SWEETPOTATOBASE_USERNAME"),
    password=os.getenv("SWEETPOTATOBASE_PASSWORD")
)
swesesh = BrAPIClient_dev(base_url="https://sweetpotatobase.org/brapi/v2",
                         session=swesesh)

params={
        "locationTypes": ["Lab"],
        "countryCodes": ["USA"]
    }

swesesh.general_get(service="locations",validate=True,search=True,params=params)

swesesh.show_services_to_llm()
service = "search/studies/{searchResultsDbId}"
swesesh.format_parameters_help(service)
swesesh.format_parameters_help("locations")


result = swesesh.general_get(service="locations",
                    search=True,
                    params = {"countryName":["Ghana"]})

result.columns
result['locationDbId'].unique()



swesesh.format_parameters_help("search/referencesets/{searchResultsDbId}")
swesesh.show_all_services_help()

# Test 1: studyType as array (BrAPI spec says arrays with OR logic)
print("\n=== TEST 1: studyType as array ===")
payload1 = {"studyTypes":["Advanced Yield Trial"]
            }
print(f"Payload: {payload1}")
post_response1 = swesesh.session.post(
  "https://sweetpotatobase.org/brapi/v2/search/studies",
    json=payload1
)
print(f"POST Request Body: {post_response1.request.body}")
post1 = post_response1.json()
post1
search_id1 = post1['result']['searchResultsDbId']
get_response1 = swesesh.session.get(f"https://sweetpotatobase.org/brapi/v2/search/studies/{search_id1}")
get_json1 = get_response1.json()
print(f"Total results: {get_json1['metadata']['pagination']}")
get_json1
if get_json1['result']['data']:
    print(f"First result studyType: {get_json1['result']['data'][0].get('studyType')}")
    get_json1
['totalCount']
# Test 3: Using the CORRECT field name from the schema: studyTypes (plural!)
print("\n=== TEST 3: studyTypes (CORRECT field name) ===")
payload3 = {"locationDbIds": ["66","63","77","78"],
            "studyTypes":["Advanced Yield Trial"]}
print(f"Payload: {payload3}")
post_response3 = swesesh.session.post(
  "https://sweetpotatobase.org/brapi/v2/search/studies",
    json=payload3
)
print(f"POST Request Body: {post_response3.request.body}")
post3 = post_response3.json()
search_id3 = post3['result']['searchResultsDbId']
get_response3 = swesesh.session.get(f"https://sweetpotatobase.org/brapi/v2/search/studies/{search_id3}?pageSize=5")
get_json3 = get_response3.json()
print(f"Total results: {get_json3['metadata']['pagination']['totalCount']}")
if get_json3['result']['data']:
    print(f"First result studyType: {get_json3['result']['data'][0].get('studyType')}")

# Test 4: AND search with both locationDbIds AND studyTypes
print("\n=== TEST 4: AND search (locationDbIds AND studyTypes) ===")
payload4 = {"locationDbIds": ["66","63","77","78"],
            "studyTypes":["Advanced Yield Trial"]}
print(f"Payload: {payload4}")
post_response4 = swesesh.session.post(
  "https://sweetpotatobase.org/brapi/v2/search/studies",
    json=payload4
)
print(f"POST Request Body: {post_response4.request.body}")
post4 = post_response4.json()
search_id4 = post4['result']['searchResultsDbId']
get_response4 = swesesh.session.get(f"https://sweetpotatobase.org/brapi/v2/search/studies/{search_id4}?pageSize=10")
get_json4 = get_response4.json()
print(f"Total results: {get_json4['metadata']['pagination']['totalCount']}")
print(f"Results breakdown:")
for study in get_json4['result']['data']:
    print(f"  - {study['studyName']}: locationDbId={study['locationDbId']}, studyType={study['studyType']}")



swesesh._fetch_all_pages(f"/search/locations/{post['result']['searchResultsDbId']}", 
                                            max_pages=10,
                                            pagesize=10)
post['result']['searchResultsDbId']

swesesh.session.get(f"")
result = post.json()
result['result']['searchResultsDbId']

if result['result']['searchResultsDbId']:
    print("cat")

get = swesesh.general_get(
    
)

swesesh.format_parameters_help("locations")
get.raise_for_status()
get.json()
post.raise_for_status()
post.body
post.json()

# curl -X POST "https://sweetpotatobase.org/brapi/v2/search/studies" \
#      -H "Content-Type: application/json" \
#      -d '{"locationDbIds": ["12"]}'

basesesh = requests.Session()
client = BrAPIClient_dev(base_url="https://test-server.brapi.org/brapi/v2")
# Check Services
client.show_all_services_help()
client.general_get(service="studies")
payload = {"germplasmDbID":"germplasm1"}
post = client.session.post(
  "https://test-server.brapi.org/brapi/v2/search/observations",
    json=payload  
)
post.raise_for_status
post.json()
post.headers
post.request.body
os.getenv("SWEETPOTATOBASE_USERNAME")