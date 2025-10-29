# Use Modify Romil's and Barebones brAPI to with an authentification function and parsing function. 

# Imports
from client.auths import create_sgn_session
import pydantic
from typing import Optional, Dict, List, Any
import requests
from client.brapi_v2.manual import ServerInfo


class BrAPIClient:
    """Client for interacting with SweetPotatoBase BrAPI endpoints"""
    
    def __init__(self, base_url: str = "https://sweetpotatobase.org/brapi/v2",
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 form: str = "SGN"
                 ):
                """
                Initialize BrAPI client
                
                Args:
                    base_url: Base URL for BrAPI endpoints
                    """
                self.base_url = base_url
                self.username = username
                self.password = password
                self.form = form
                self.session = self.get_client()
    def get_client(self):
        if self.form == "SGN":
            return create_sgn_session(
                base_url=self.base_url.replace("/brapi/v2",""),
                auto_login=True,
                username=self.username,
                password=self.password
            )
        else:
            raise NotImplementedError(f"Form {self.form} not implemented yet.")
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a GET request to BrAPI endpoint
        
        Args:
            endpoint: API endpoint (e.g., '/germplasm')
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            self.last_response = response
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return {}
    
    def _fetch_all_pages(self, endpoint: str, params: Optional[Dict] = None, max_pages: int = 100) -> List[Dict]:
        """
        Fetch all pages of paginated results
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of all results across pages
        """
        all_data = []
        page = 0
        params = params or {}
        params['pageSize'] = 1000  # Large page size for efficiency
        
        while page < max_pages:
            params['page'] = page
            response = self._make_request(endpoint, params)
            print(response)
            if not response or 'result' not in response:
                break

            # Check if there are more pages
            metadata = response.get('metadata', {})
            pagination = metadata.get('pagination', {})
            current_page = pagination.get('currentPage', page)
            total_pages = pagination.get('totalPages', 1)

            if total_pages ==1:   
                 data = response['result']
            else:
                data = response['result'].get('data', [])
            if not data:
                break
                
            all_data.extend(data)
            
            if current_page >= total_pages - 1:
                break
                
            page += 1
            
        return all_data

brapi_client = BrAPIClient()

programs = brapi_client._fetch_all_pages('/programs/1288')
programs

studies = brapi_client._fetch_all_pages('/studies')
pd.DataFrame(studies)['studyDbId']

study_id = "4494"
obs =  brapi_client._fetch_all_pages('/studies/{study_id}/observations')

from client.brapi_v2.model import Program,ProgramType
programs = [Program.model_validate(p) for p in programs]
import pandas as pd
pd.DataFrame(programs)

programs

germ = client._make_request('/germplasm')
if1 = germ['result']
if1
pd.json_normalize(if1["data"])

import json
with open('serverinfo.json') as f:
     data =json.load(f)
len(data['result']['calls'])

for call in data['result']['calls']:
    print(call['service'])


pydantic.__version__
client = create_sgn_session(
        base_url="https://sweetpotatobase.org",
        auto_login=True,
        username="JerryHYu",
        password="$B1dX*JC$D!SeYpF"
    )
response = client.get(f"{client.base_url}/brapi/v2/serverinfo")

data = response.json()
result = data['result']
server_info = ServerInfo.model_validate(result)
server_info.calls[1].service

type(server_info)

germplasm


from client.brapi_v2.manual import ServerInfo





import json
with open(filename,"w") as j_file:
      json.dump(server_info,j_file,indent=4)