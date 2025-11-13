import os
from client_dev import BrAPIClient_dev
import requests
import pandas as pd
import json
from dotenv import load_dotenv
from auths import create_sgn_session

basesesh = requests.Session()
client = BrAPIClient_dev(base_url="https://test-server.brapi.org/brapi/v2",
                         session=basesesh)
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

# Now Sweetpotatobase
load_dotenv()
swesesh = create_sgn_session(
    base_url="https://sweetpotatobase.org",
    auto_login=True,
    username=os.getenv("SWEETPOTATOBASE_USERNAME"),
    password=os.getenv("SWEETPOTATOBASE_PASSWORD")
)

payload = {
            "grant_type": "password",
            "password": f"JgWY3gMv%*GC8FfL",
            "username": os.getenv("SWEETPOTATOBASE_USERNAME")
        }

# Make authentication request
response = requests.post("https://sweetpotatobase.org/brapi/v2/token", data=payload)
response.json()
# curl -X POST "https://test-server.brapi.org/brapi/v2/search/observations" \
#      -H "Content-Type: application/json" \
#      -d '{"germplasmDbID":["germplasm1"]}'