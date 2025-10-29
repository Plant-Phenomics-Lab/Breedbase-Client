# Imports
from client.auths import create_sgn_session
import pydantic
from typing import Optional, Dict, List, Any
import requests
from client.brapi_v2_dev.manual import ServerInfo
import tempfile
import pandas as pd
import json
import traceback


class BrAPIClientDebug:
    """Debug version of BrAPI Client with enhanced error reporting"""

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
                self.temp_endpoints_file = None
                self.servicelist = self._get_valid_endpoints()

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
            traceback.print_exc()
            return {}

    def _fetch_all_pages(self, endpoint: str, params: Optional[Dict] = None, max_pages: int = 100) -> List[Dict]:
        """
        Fetch all pages of paginated results WITH DEBUG OUTPUT

        Args:
            endpoint: API endpoint
            params: Query parameters
            max_pages: Maximum number of pages to fetch

        Returns:
            List of all results across pages
        """
        print(f"\n{'='*60}")
        print(f"DEBUG: Starting _fetch_all_pages for endpoint: {endpoint}")
        print(f"DEBUG: max_pages = {max_pages}")
        print(f"{'='*60}\n")

        all_data = []
        page = 0
        params = params or {}
        params['pageSize'] = 100  # Large page size for efficiency

        while page < max_pages:
            print(f"\n--- DEBUG: Fetching page {page} ---")
            params['page'] = page
            response = self._make_request(endpoint, params)

            if not response or 'result' not in response:
                print(f"DEBUG: No response or 'result' not in response, breaking")
                break

            # Check if there are more pages
            metadata = response.get('metadata', {})
            pagination = metadata.get('pagination', {})
            current_page = pagination.get('currentPage', page)
            total_pages = pagination.get('totalPages', 1)
            total_pages = min(total_pages, max_pages)

            print(f"DEBUG: current_page = {current_page}, total_pages = {total_pages}")

            if total_pages == 1:
                print(f"DEBUG: total_pages == 1, returning early")
                data = [response['result']]
                print(f"DEBUG: Returning data type: {type(data)}, length: {len(data)}")
                print(f"DEBUG: First item type: {type(data[0])}")
                print(f"DEBUG: First item keys: {data[0].keys() if isinstance(data[0], dict) else 'NOT A DICT'}")
                return data
            else:
                data = response['result'].get('data', [])
                print(f"DEBUG: Extracted data from response['result']['data']")
                print(f"DEBUG: data type: {type(data)}, length: {len(data)}")
                if data:
                    print(f"DEBUG: First item in data type: {type(data[0])}")
                    print(f"DEBUG: First item in data: {data[0]}")

            if not data:
                print(f"DEBUG: No data, breaking")
                break

            all_data.extend(data)
            print(f"DEBUG: all_data now has {len(all_data)} items")

            if current_page >= total_pages - 1:
                print(f"DEBUG: Reached last page, breaking")
                break

            page += 1

        print(f"\n{'='*60}")
        print(f"DEBUG: Exited while loop")
        print(f"DEBUG: all_data length: {len(all_data)}")
        print(f"DEBUG: all_data type: {type(all_data)}")
        if all_data:
            print(f"DEBUG: First item in all_data type: {type(all_data[0])}")
            print(f"DEBUG: First item in all_data: {all_data[0]}")
            print(f"DEBUG: Attempting to access all_data[0]['data']...")
        else:
            print(f"DEBUG: all_data is EMPTY!")
        print(f"{'='*60}\n")

        try:
            data = all_data
            print(f"DEBUG: Successfully extracted all_data[0]['data']")
            print(f"DEBUG: Result type: {type(data)}, length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
            return data
        except Exception as e:
            print(f"ERROR: Failed to extract all_data[0]['data']")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {e}")
            traceback.print_exc()
            raise

    def _get_valid_endpoints(self):
        """Get valid endpoints based on server info and save to temp CSV file"""
        serverinfo = self._make_request("/serverinfo")
        servicelist = [serv['service'] for serv in serverinfo['result']['calls']]
        all_endpoints = pd.read_csv('client/brapi_endpoints.csv')
        valid_endpoints = all_endpoints[all_endpoints['service'].isin(servicelist)]

        # Create temporary file - auto-deletes when closed/session ends
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=True)
        valid_endpoints.to_csv(temp_file.name, index=False)
        self.temp_endpoints_file = temp_file
        return servicelist

    def _load_endpoints_df(self) -> pd.DataFrame:
        """Load endpoints from temp CSV file"""
        if not self.temp_endpoints_file:
            raise RuntimeError("Valid endpoints file not initialized")
        return pd.read_csv(self.temp_endpoints_file.name)

    def _load_endpoint_schema(self, service: str) -> Dict[str, Any]:
        """Load valid parameters schema for a service from temp CSV"""
        endpoints_df = self._load_endpoints_df()
        endpoint_row = endpoints_df[endpoints_df['service'] == service]

        if endpoint_row.empty:
            raise KeyError(f"Service '{service}' not found in valid endpoints")

        schema_str = endpoint_row.iloc[0]['dictionary_loc']
        return json.loads(schema_str)

    def _format_parameters_help(self, service: str) -> str:
        """Format parameter information for help display"""
        endpoints_df = self._load_endpoints_df()
        endpoint_row = endpoints_df[endpoints_df['service'] == service]

        if endpoint_row.empty:
            return f"Service '{service}' not found"

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

        return help_text

    def _show_all_services_help(self) -> str:
        """Show all available services with descriptions"""
        endpoints_df = self._load_endpoints_df()
        help_text = "\n" + "="*60 + "\n"
        help_text += "Available BrAPI Services\n"
        help_text += "="*60 + "\n\n"

        for _, row in endpoints_df.iterrows():
            help_text += f"{row['service']}: {row['description']}\n"

        help_text += "\n" + "-"*60 + "\n"
        help_text += "For detailed parameter info, call:\n"
        help_text += "  client.general_get(help='service_name')\n"

        return help_text

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
                    max_pages:Optional[Dict]=100):
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
                return self._show_all_services_help()
            else:
                return self._format_parameters_help(help)

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
        response = self._fetch_all_pages(endpoint, params=params, max_pages=max_pages)

        # Convert to DataFrame if requested
        if dataframe:
            if len(response) > 0 and len(response[0]) == 1 and 'data' in response[0]:
                return pd.json_normalize(response[0]['data'])
            else:
                return pd.json_normalize(response)

        return response

client = BrAPIClientDebug()
client.general_get(service="observations",max_pages=1)