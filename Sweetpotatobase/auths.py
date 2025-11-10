"""
Authentification for Sweetpotatobase
- uses the SGN (Solgenomics) format of psudo authentification with a browser cookie
"""

# Imports
import sys
import os

class sweetpotatobase_client(): 
    """
    Wrap Base BrAPI Client with authentification with sweetpotatobase. 
    
    Authenticate with username and password.

    This method implements SGN's custom array-based token request format.
    The token is automatically saved to file and loaded for future requests.

    Args:
        username: BrAPI username (prompted if None)
        password: BrAPI password (prompted if None, hidden input)

    """
    def __init__(self,
                 base_url:str = "https://sweetpotatobase.org/brapi/v2",
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        pass
    
    def login(self):
        # Prompt for credentials if not provided
        if not username:
            username = input("Enter your BrAPI username: ")
        if not password:
            password = getpass.getpass("Enter your BrAPI password: ")

        # Validate credentials were provided
        if not username or not password:
            raise ValueError("Username and password must be provided")

        # Construct SGN's non-standard format
        # Note: This is NOT standard OAuth2, but required by SGN servers
        payload = {
            "grant_type": "password",
            "password": password,
            "username": username
        }

        # Make authentication request
        response = requests.post(self.token_url, data=payload)

        # Raise exception if authentication failed
        response.raise_for_status()

        # Parse response
        data = response.json()

        # Extract token information
        access_token = data.get('access_token')
        expires_in = data.get('expires_in', 7200)  # Default 2 hours
        user_display_name = data.get('userDisplayName', username)

        if not access_token:
            raise ValueError("Server did not return an access token")



    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """
        Authenticate with username and password (OAuth2 password grant).

        This method implements SGN's custom array-based token request format.
        The token is automatically saved to file and loaded for future requests.

        Args:
            username: BrAPI username (prompted if None)
            password: BrAPI password (prompted if None, hidden input)

        Returns:
            Dictionary containing:
                - access_token: The bearer token
                - expires_at: Unix timestamp when token expires
                - userDisplayName: User's display name from server

        Raises:
            requests.HTTPError: If authentication fails
            ValueError: If credentials are invalid

        Example:
            >>> client = SGNBrAPIOAuth2("https://sweetpotatobase.org")
            >>> client.login("myusername", "mypassword")
            {'access_token': '...', 'expires_at': 1234567890, 'userDisplayName': 'John Doe'}
        """
        # Prompt for credentials if not provided
        if not username:
            username = input("Enter your BrAPI username: ")
        if not password:
            password = getpass.getpass("Enter your BrAPI password: ")

        # Validate credentials were provided
        if not username or not password:
            raise ValueError("Username and password must be provided")

        # Construct SGN's non-standard format
        # Note: This is NOT standard OAuth2, but required by SGN servers
        payload = {
            "grant_type": "password",
            "password": password,
            "username": username
        }

        # Make authentication request
        response = requests.post(self.token_url, data=payload)

        # Raise exception if authentication failed
        response.raise_for_status()

        # Parse response
        data = response.json()

        # Extract token information
        access_token = data.get('access_token')
        expires_in = data.get('expires_in', 7200)  # Default 2 hours
        user_display_name = data.get('userDisplayName', username)

        if not access_token:
            raise ValueError("Server did not return an access token")

        # Convert to standard OAuth2 token format
        token = {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': expires_in,
            'expires_at': int(time.time()) + expires_in,
            'userDisplayName': user_display_name
        }

        # Save token (triggers _save_token callback)
        self.token = OAuth2Token(token)
        self._save_token(token)
        self.login_time = time.time()

        print(f"[OK] Login successful! Authenticated as: {user_display_name}")

        return token

    def logout(self):
        """
        Clear authentication token and delete token file.

        Note: This is a local logout only. The server token remains valid
        until it expires naturally (no server-side revocation endpoint).
        """
        self.token = None

        try:
            Path(self.token_file).unlink()
            print(f"[OK] Token deleted from {self.token_file}")
        except FileNotFoundError:
            pass

        print("[OK] Logged out successfully")

    def _check_time(self):
        """
        Check before requests if token has expired. 
        """
        if time.time() > self.login_time + self.token.get('expires_in', 0):
            print("[WARNING] Token has expired, logging in again.")
            self.logout()
            self.login()