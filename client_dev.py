# Imports
from auths import create_sgn_session
import pydantic
from typing import Optional, Dict, List, Any, Literal
import requests
from brapi_v2.manual import ServerInfo
import pandas as pd
import json
import os
from datetime import datetime
from urllib.parse import urlparse

class BrAPIClient_dev:
    """Client for interacting with SweetPotatoBase BrAPI endpoints"""

    def __init__(self, 
                 base_url: str = "https://sweetpotatobase.org/brapi/v2",
                 session: requests.Session = requests.Session(),
                #  username: Optional[str] = None,
                #  password: Optional[str] = None,
                #  form: str = "SGN"
                 ):
                """
                Initialize BrAPI client

                Args:
                    base_url: Base URL for BrAPI endpoints
                    """
                # Initialize all attributes first to avoid AttributeError in __del__
                self.base_url = base_url
                # self.username = username
                # self.password = password
                self.form = urlparse(base_url).hostname.split('.')[0] 
                # self.temp_endpoints_path = None
                self.servicelist = None
                self.session = None
                
                # Now initialize (if these fail, __del__ won't crash)
                self.session = session
                self.servicelist = self._get_valid_endpoints()
    
    # def __del__(self):
    #     """Cleanup temp file when object is destroyed"""
    #     if hasattr(self, 'temp_endpoints_file') and self.temp_endpoints_file:
    #         try:
    #             os.unlink(self.temp_endpoints_file.name)
    #         except:
    #             pass
    
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
            print(f"DEBUG _make_request: Final URL = {response.url}")
            print(f"DEBUG _make_request: Status = {response.status_code}")
            response.raise_for_status()
            self.last_response = response
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error {e.response.status_code}: {e.response.reason}")
            print(f"URL: {e.response.url}")
            print(f"Response: {e.response.text}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return {}

    def _fetch_all_pages(self, 
                         endpoint: str, 
                         params: Optional[Dict] = None, 
                         max_pages: int = 100,
                         pagesize: int = 100,
                         is_search_result: bool = False) -> List[Dict]:
        """
        Fetch all pages of paginated results

        Args:
            endpoint: API endpoint
            params: Query parameters
            max_pages: Maximum number of pages to fetch
            is_search_result: If True, only use page/pageSize params (don't add filter params)

        Returns:
            List of all results across pages
        """
        all_data = []
        page = 0
        
        # For search results, DON'T add any params - the filter is in the URL already
        if is_search_result:
            params = {}
        else:
            params = params or {}
        
        params['pageSize'] = pagesize  # Large page size for efficiency

        while page < max_pages:
            params['page'] = page
            url = f"{self.base_url}{endpoint}"
            print(f"DEBUG: Fetching {url} with params: {params}")
            response = self._make_request(endpoint, params)

            if not response or 'result' not in response:
                break

            # Check if there are more pages
            metadata = response.get('metadata', {})
            pagination = metadata.get('pagination', {})
            current_page = pagination.get('currentPage', page)
            total_pages = pagination.get('totalPages', 1)
            total_pages = min(total_pages,max_pages)

            # Normalize result to a flat list of row dicts for consistent return shape.
            # Possible shapes returned by BrAPI 'result':
            #  - {'data': [...], ...}             -> use the 'data' list
            #  - [...]                             -> already a list of rows
            #  - { ... } (single resource object) -> wrap as single-item list
            result_obj = response['result']
            if isinstance(result_obj, dict) and 'data' in result_obj:
                data = result_obj.get('data', [])
            elif isinstance(result_obj, list):
                data = result_obj
            elif isinstance(result_obj, dict):
                # Single resource object — return as single-item list
                data = [result_obj]
            else:
                data = []

            if not data:
                break

            all_data.extend(data)

            if current_page >= total_pages - 1:
                break

            page += 1

        data = all_data

        # Get Metadta
        totalCount = pagination.get('totalCount', 0)
        saved_metadata = {
            "totalCount":totalCount,
            "time":datetime.now().strftime("%Y%m%d%H%M%S")
        }
        return data, saved_metadata

    def _get_valid_endpoints(self,clean=True):
        """Get valid endpoints based on server info and save to temp CSV file"""

        # Check if File Exists, and delete if needed
        # Create temp directory in current working directory
        temp_dir = os.path.join(os.getcwd(), ".brapi_temp")
        os.makedirs(temp_dir, exist_ok=True)
        self.temp_endpoints_path = f"{temp_dir}/{self.form}.csv"
        if os.path.exists(self.temp_endpoints_path) and clean:
            try:
                os.remove(self.temp_endpoints_path)
            except FileNotFoundError:
                pass
        
        serverinfo = self._make_request("/serverinfo")
        servicelist = [serv['service'] for serv in serverinfo['result']['calls']]
        all_endpoints = pd.read_csv('brapi_endpoints.csv')
        # all_endpoints = all_endpoints["status" != 0]
        valid_endpoints = all_endpoints[all_endpoints['service'].isin(servicelist)]
        
        # save csv
        valid_endpoints.to_csv(f"{temp_dir}/{self.form}.csv",index=False)
        return servicelist

    def _load_endpoints_df(self) -> pd.DataFrame:
        """Load endpoints from temp CSV file"""
        if not self.temp_endpoints_path:
            raise RuntimeError("Valid endpoints file not initialized")
        return pd.read_csv(self.temp_endpoints_path)

    def _load_endpoint_schema(self, service: str) -> Dict[str, Any]:
        """Load valid parameters schema for a service from temp CSV"""
        endpoints_df = self._load_endpoints_df()
        endpoint_row = endpoints_df[endpoints_df['service'] == service]

        if endpoint_row.empty:
            raise KeyError(f"Service '{service}' not found in valid endpoints")

        schema_str = endpoint_row.iloc[0]['dictionary_loc']
        return json.loads(schema_str)

    def format_parameters_help(self, service: str) -> None:
        """Format parameter information for help display"""
        endpoints_df = self._load_endpoints_df()
        endpoint_row = endpoints_df[endpoints_df['service'] == service]

        if endpoint_row.empty:
            print(f"Service '{service}' not found")
            return

        description = endpoint_row.iloc[0]['description']
        schema = json.loads(endpoint_row.iloc[0]['dictionary_loc'])

        help_text = f"\n{'='*60}\n"
        help_text += f"Service: {service}\n"
        help_text += f"Description: {description}\n"
        help_text += f"{'='*60}\n\n"
        help_text += "Available Parameters:\n"
        help_text += "-" * 60 + "\n"

        for param_name, param_info in schema.items():
            param_type = param_info.get('type', 'unknown')
            required = param_info.get('required', False)
            param_desc = param_info.get('description', 'No description')
            required_str = "REQUIRED" if required else "optional"

            help_text += f"\n{param_name} ({param_type}) [{required_str}]\n"
            help_text += f"  {param_desc}\n"

        print(help_text)
    
    def format_parameters_for_llm(self, service: str) -> None:
        """Format parameter information for help display"""
        endpoints_df = self._load_endpoints_df()
        endpoint_row = endpoints_df[endpoints_df['service'] == service]

        if endpoint_row.empty:
            print(f"Service '{service}' not found")
            return

        description = endpoint_row.iloc[0]['description']
        schema = json.loads(endpoint_row.iloc[0]['dictionary_loc'])
        return schema

    def show_all_services_help(self) -> None:
        """Show all available services with descriptions in a formatted table"""
        endpoints_df = self._load_endpoints_df()

        help_text = "\n" + "="*100 + "\n"
        help_text += " " * 35 + "AVAILABLE BrAPI SERVICES\n"
        help_text += "="*100 + "\n"

        # Group by category
        categories = endpoints_df['category'].unique()
        # Sort categories in a logical order
        category_order = ['Core', 'Germplasm', 'Phenotyping', 'Genotyping', 'Other']
        categories = [c for c in category_order if c in categories]

        for category in categories:
            cat_df = endpoints_df[endpoints_df['category'] == category].sort_values('service')

            if len(cat_df) == 0:
                continue

            help_text += f"\n┌─ {category} " + "─" * (97 - len(category)) + "┐\n"

            # Table header
            help_text += "│ " + "SERVICE".ljust(40) + " │ " + "DESCRIPTION".ljust(54) + " │\n"
            help_text += "├─" + "─" * 40 + "─┼─" + "─" * 54 + "─┤\n"

            # Table rows
            for _, row in cat_df.iterrows():
                service = row['service']
                desc = row['description']

                # Truncate long descriptions
                if len(desc) > 54:
                    desc = desc[:51] + "..."

                help_text += f"│ {service.ljust(40)} │ {desc.ljust(54)} │\n"

            help_text += "└─" + "─" * 40 + "─┴─" + "─" * 54 + "─┘\n"

        help_text += "\n" + "="*100 + "\n"
        help_text += "For detailed parameter info:\n"
        help_text += "  client.general_get(help='service_name')\n"
        help_text += "\nExample:\n"
        help_text += "  client.general_get(help='germplasm')\n"
        help_text += "="*100 + "\n"

        print(help_text)
    
    def show_services_to_llm(self) -> Dict[str, Any]:
        """Show all available services in dictionary for LLM
        
        Returns:
            Dictionary with services grouped by category, flagging DbID and Search support
        """
        endpoints_df = self._load_endpoints_df()
        # Group by category
        categories = endpoints_df['category'].unique()
        # Sort categories in a logical order
        category_order = ['Core', 'Germplasm', 'Phenotyping', 'Genotyping', 'Other']
        categories = [c for c in category_order if c in categories]

        result = {}
        
        for category in categories:
            cat_df = endpoints_df[endpoints_df['category'] == category].sort_values('service')
            if len(cat_df) == 0:
                continue
            
            # Group services by base name (without DbID or search prefix)
            services_dict = {}
            
            for _, row in cat_df.iterrows():
                service = row['service']
                
                # Determine base service name and flags
                has_dbid = '/{' in service and 'DbId}' in service
                has_search = service.startswith('search/')
                
                # Extract base service name
                if has_search:
                    # e.g., "search/germplasm/{searchResultsDbId}" -> "germplasm"
                    base_service = service.split('/')[1].split('/{')[0]
                elif has_dbid:
                    # e.g., "germplasm/{germplasmDbId}" -> "germplasm"
                    base_service = service.split('/{')[0]
                else:
                    # e.g., "germplasm" -> "germplasm"
                    base_service = service
                
                # Initialize service entry if not exists
                if base_service not in services_dict:
                    services_dict[base_service] = {
                        "service": base_service,
                        "DbID": False,
                        "Search": False,
                        "description": row['description']
                    }
                
                # Update flags
                if has_dbid:
                    services_dict[base_service]["DbID"] = True
                if has_search:
                    services_dict[base_service]["Search"] = True
                
                # If this is the base endpoint (no DbID, no search), keep its description
                if not has_dbid and not has_search:
                    services_dict[base_service]["description"] = row['description']
            
            result[category] = services_dict
        
        return result

    def _validate_params(self, service: str, params: Dict[str, Any]) -> None:
        """Validate params against endpoint schema"""
        if not params:
            return

        schema = self._load_endpoint_schema(service)

        for param_name, param_value in params.items():
            if param_name not in schema:
                valid_params = list(schema.keys())
                raise KeyError(
                    f"Parameter '{param_name}' not valid for service '{service}'.\n"
                    f"Valid parameters: {valid_params}"
                )

            # Check type
            expected_type = schema[param_name].get('type')
            if expected_type == 'string' and not isinstance(param_value, str):
                raise TypeError(
                    f"Parameter '{param_name}' expects type 'string', "
                    f"got {type(param_value).__name__}"
                )
            
    def _search_request(self, 
                         endpoint: str, 
                         params: Dict = None, 
                         max_pages: int = 100,
                         pagesize: int = 100,
                         validate:bool = True) -> List[Dict]:
        """
        Use BrAPI's POST > Search workflow to search using params
        """
        if params:
            # Validate parameters if requested
            if validate and params:
                # Extract service name from endpoint (e.g., "search/germplasm" -> "germplasm")
                service = f"{endpoint}/{{searchResultsDbId}}"
                self._validate_params(service, params)
            # Post
            response = self.session.post(f"{self.base_url}/{endpoint}",
                                     json=params  
                                    )
            response.raise_for_status()
            print("-"*97)
            print(f"URL: {response.url}")
            print(f"Request body: {response.request.body}")
            print(f"Response: {response.json()}")
            post = response.json()

            # Get
            if post['result']['searchResultsDbId']:
                return self._fetch_all_pages(f"/{endpoint}/{post['result']['searchResultsDbId']}", 
                                            max_pages=max_pages,
                                            pagesize=pagesize,
                                            is_search_result=True)
            else: 
                raise ValueError("Search POST did not return searchResultsDbId")
        else:
            raise ValueError(
                "You specified a search request with no fields. A search request is not appropriate."
                " If you did nopt intend to search with anything, please set search = False in general_get"
            )

    def general_get(self,
                    # Endpoint Construction
                    service: str = None,
                    DbID: Optional[str] = None,
                    search: Optional[bool] = False,
                    sub: Optional[str] = None,
                    params: Optional[Dict] = None,
                    # Checking
                    validate: Optional[bool] = False,
                    # Output Options
                    dataframe: Optional[bool] = True,
                    # Pagination
                    max_pages:Optional[int]=100,
                    pagesize:Optional[int]=100
                    ):
        """
        General Helper Function for BrAPI Output.

        Args:
            help: Show help. Set to True for all services, or service name for specific service
            service: BrAPI service endpoint name (e.g., 'germplasm', 'attributes')
            validate: Validate params against endpoint schema
            dataframe: Convert response to pandas DataFrame
            DbID: Optional ID to append to endpoint path
            params: Dictionary of query parameters matching the endpoint schema

        Returns:
            Help text if help=True, otherwise the API response (as DataFrame or dict)
        """

        # Validate service exists
        if service not in self.servicelist:
            raise ValueError(
                f"Service '{service}' not available. "
                f"Call client.general_get(help=True) to see available services"
            )

        # Build endpoint URL
        if search: 
            response, metadata = self._search_request(f"search/{service}",
                                            params=params,
                                            max_pages=max_pages,
                                            pagesize=pagesize,
                                            validate=validate)
        else:
            # NOT NEEDED RN; the three things that work are hard coded. 
            # # Validate parameters if requested
            # if validate and params:
            #     self._validate_params(service, params)
            if sub: 
                if sub not in ["calls","callsets","variants"]:
                    raise ValueError(
                        f"The subservice you requested is not avalible."
                    )
                elif not DbID:
                    raise ValueError(
                        f"sub calls require DbID. DbID was not provided."
                    )
                else: 
                    endpoint = f"{service}/{DbID}/{sub}"
            elif DbID: 
                endpoint = f"/{service}/{DbID}"
            else:
                endpoint = f"/{service}"
            # Make request
            response, metadata = self._fetch_all_pages(endpoint, params=params, 
                                                max_pages=max_pages,
                                                pagesize=pagesize)

        # Convert to DataFrame if requested
        if dataframe:
            return pd.json_normalize(response), metadata

        return response, metadata

    # def _update_endpoint(service: str = None):


# Testing if Needed   
# sweetpotatobase = BrAPIClient_dev(
#     base_url="https://sweetpotatobase.org/brapi/v2",
#     username="JerryHYu",
#     password="$B1dX*JC$D!SeYpF"
# )

# sweetpotatobase.general_get(service="locations",pagesize=10,max_pages=1)