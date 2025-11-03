"""
SweetPotatoBase MCP Server

This MCP (Model Context Protocol) server provides AI agents with tools to query
the SweetPotatoBase BrAPI endpoints and retrieve breeding data.

Version: 0.1.0
Last Updated: 2024-11-3
Author: Jerry Yu

Changelog:
- 0.0.0 (2024-10-29): Initial MCP server implementation
  * Added all_functions() to list available endpoints
  * Added specific_function() to get endpoint details
  * Added general_get() to query and save BrAPI data as CSV
  * Integrated with BrAPIClient for OAuth authentication
"""

# Imports
from auths import create_sgn_session
import pydantic
from typing import Optional, Dict, List, Any
import requests
from brapi_v2.manual import ServerInfo
import pandas as pd
import json
import os


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
                # Initialize all attributes first to avoid AttributeError in __del__
                self.base_url = base_url
                self.username = username
                self.password = password
                self.form = form
                self.temp_endpoints_path = None
                self.servicelist = None
                self.session = None
                
                # Now initialize (if these fail, __del__ won't crash)
                self.session = self.get_client()
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
            response.raise_for_status()
            self.last_response = response
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return {}

    def _fetch_all_pages(self, 
                         endpoint: str, 
                         params: Optional[Dict] = None, 
                         max_pages: int = 100,
                         pagesize: int = 100) -> List[Dict]:
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
        params['pageSize'] = pagesize  # Large page size for efficiency

        while page < max_pages:
            params['page'] = page
            response = self._make_request(endpoint, params)

            if not response or 'result' not in response:
                break

            # Check if there are more pages
            metadata = response.get('metadata', {})
            pagination = metadata.get('pagination', {})
            current_page = pagination.get('currentPage', page)
            total_pages = pagination.get('totalPages', 1)
            total_pages = min(total_pages,max_pages)

            if total_pages ==1:
                 data = [response['result']]
                 return data
            else:
                data = response['result'].get('data', [])

            if not data:
                break

            all_data.extend(data)

            if current_page >= total_pages - 1:
                break

            page += 1

        data = all_data
        return data

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

    def general_get(self,
                    help: Optional[bool | str] = None,
                    service: str = None,
                    validate: Optional[bool] = False,
                    dataframe: Optional[bool] = True,
                    DbID: Optional[str] = None,
                    params: Optional[Dict] = None,
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
        # Handle help requests
        if help:
            if help is True:
                self.show_all_services_help()
            else:
                self.format_parameters_help(help)
            return None

        # Validate service exists
        if service not in self.servicelist:
            raise ValueError(
                f"Service '{service}' not available. "
                f"Call client.general_get(help=True) to see available services"
            )

        # Validate parameters if requested
        if validate and params:
            self._validate_params(service, params)

        # Build endpoint URL
        if DbID:
            endpoint = f"/{service}/{DbID}"
        else:
            endpoint = f"/{service}"

        # Make request
        response = self._fetch_all_pages(endpoint, params=params, 
                                         max_pages=max_pages,
                                         pagesize=pagesize)

        # Convert to DataFrame if requested
        if dataframe:
            if len(response) > 0 and len(response[0]) == 1 and 'data' in response[0]:
                return pd.json_normalize(response[0]['data'])
            else:
                return pd.json_normalize(response)

        return response

# Testing if Needed   
# sweetpotatobase = BrAPIClient_dev(
#     base_url="https://sweetpotatobase.org/brapi/v2",
#     username="JerryHYu",
#     password="$B1dX*JC$D!SeYpF"
# )

# sweetpotatobase.general_get(service="locations",pagesize=10,max_pages=1)

