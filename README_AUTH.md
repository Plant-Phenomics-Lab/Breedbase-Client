# BrAPI OAuth2 Authentication Module

## Overview

This module provides OAuth2 authentication for BrAPI clients with automatic token management, storage, and refresh capabilities.

## Files

- **`auths.py`**: OAuth2 authentication module with session management
- **`client-simple-dev.py`**: BrAPI client that uses the auth module
- **`.sgn_brapi_token.json`**: Auto-generated token storage (gitignored)

## Quick Start

### Basic Usage

```python
from client_simple_dev import BrAPIClient

# Create client
client = BrAPIClient("https://sweetpotatobase.org")

# Login (prompts for credentials)
client.login()

# Make authenticated requests
server_info = client.get_serverinfo()
germplasm = client.get_germplasm(germplasm_name="Beauregard")
```

### Auto-Login

```python
# Client will prompt for login if no valid token exists
client = BrAPIClient(
    base_url="https://sweetpotatobase.org",
    auto_login=True
)

# Now you can immediately make requests
programs = client.get_programs()
```

### Programmatic Login

```python
client = BrAPIClient("https://sweetpotatobase.org")
client.login(username="myuser", password="mypassword")
```

## Architecture

### Class Hierarchy

```
OAuth2Session (authlib)
    ↓
BrAPIOAuth2Session (auths.py)
    ↓
SGNBrAPIOAuth2 (auths.py)
    ↓
BrAPIClient (client-simple-dev.py)
```

### Authentication Flow

1. **Initialization**:
   - Client checks for existing token file
   - Loads token if valid and not expired

2. **Login**:
   - Sends credentials to `/brapi/v2/token`
   - Receives `access_token` and `expires_in`
   - Saves token to JSON file

3. **Request**:
   - Checks token expiry before each request
   - Automatically adds `Authorization: Bearer <token>` header
   - Re-prompts for login if token expired

4. **Token Storage**:
   - Tokens saved to `.{domain}_token.json`
   - JSON format for easy debugging
   - Includes expiry timestamp for validation

## Token Management

### Token File Format

```json
{
  "access_token": "abcdef123456...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "expires_at": 1698765432,
  "userDisplayName": "John Doe"
}
```

### Token Expiry

- Default: 7200 seconds (2 hours)
- Automatic checking before requests
- Re-authentication prompt when expired

### Manual Token Management

```python
# Check authentication status
if not client.is_authenticated():
    client.login()

# Force re-authentication
client.logout()
client.login()

# Ensure authenticated (prompts if needed)
client.ensure_authenticated()
```

## Supported Servers

### SGN-Based Servers (Currently Implemented)

- ✅ Sweetpotatobase.org
- ✅ Cassavabase.org
- ✅ Yambase.org
- ✅ Musabase.org
- ✅ Any SGN-based BrAPI server

All use the same authentication endpoint: `/brapi/v2/token`

### Future Support

- 🔲 GIGWA servers (`/gigwa/rest/gigwa/generateToken`)
- 🔲 Standard OAuth2 authorization code flow
- 🔲 OAuth2 implicit flow

## API Methods

### Authentication Methods

```python
client.login(username, password)          # Authenticate
client.logout()                            # Clear token
client.is_authenticated()                  # Check token validity
client.ensure_authenticated()              # Auto re-login if needed
```

### BrAPI Endpoints

```python
client.get_serverinfo()                    # Server information
client.get_germplasm(germplasm_name)       # Germplasm/varieties
client.get_studies(study_name)             # Studies/trials
client.get_observations(study_id)          # Phenotypic observations
client.get_programs()                      # Breeding programs
client.get_trials()                        # Trials
client.get_locations()                     # Locations
```

### Generic Request Methods

```python
# GET request
response = client.get("/endpoint", params={"key": "value"})

# POST request
response = client.post("/endpoint", json_data={"key": "value"})
```

## Error Handling

### Authentication Errors

```python
try:
    client.login("user", "wrongpassword")
except requests.HTTPError as e:
    print(f"Login failed: {e}")
    # Status code 401: Invalid credentials
    # Status code 403: Account disabled
```

### Expired Token

```python
# Automatic handling
client.ensure_authenticated()  # Prompts for re-login

# Manual handling
if not client.is_authenticated():
    client.login()
```

### Network Errors

```python
try:
    data = client.get_germplasm()
except requests.ConnectionError:
    print("Network error: Cannot connect to server")
except requests.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
```

## Security Best Practice

### Password Input

The module uses `getpass.getpass()` for password input:
- Hides password from terminal display
- Prevents shoulder surfing
- No password in command history

```python
# Password is hidden when typing
client.login()  # Prompts: "Enter your BrAPI password: ******"
```

### Token Storage

- Tokens stored in local files (`.json`)
- **Add token files to `.gitignore`**:
  ```
  .sgn_brapi_token.json
  .*_token.json
  ```

### Token Security

- Never commit token files to version control
- Tokens expire after 2 hours (default)
- Use environment-specific token files

## Testing

### Run the example

```bash
cd /home/cabbagecat/Classes/Lab/Breedbase-AI-Agent/client

# Test auth module
python auths.py

# Test full client
python client-simple-dev.py
```

### Expected Output

```
============================================================
BrAPI Client - Example Usage
============================================================
✓ Initialized BrAPI client for https://sweetpotatobase.org
  API Version: v2
  Token file: .sweetpotatobase_org_token.json

🔐 Authentication required
------------------------------------------------------------
Enter your BrAPI username: myuser
Enter your BrAPI password:
✓ Login successful! Authenticated as: John Doe
✓ Token expires in 7200 seconds (2.0 hours)

📡 Testing API endpoints...
------------------------------------------------------------
1. Server Info:
   Server: SweetPotatoBase
   Contact: contact@sweetpotatobase.org

... [more output]
```

## Dependencies

```bash
pip install authlib requests
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'authlib'"

```bash
pip install authlib
```

### "RuntimeError: Not authenticated"

Call `client.login()` before making requests.

### "Token file corrupted"

Delete the token file and re-login:
```bash
rm .sgn_brapi_token.json
python client-simple-dev.py
```

### "Connection refused"

Check server URL is correct and accessible:
```python
import requests
response = requests.get("https://sweetpotatobase.org/brapi/v2/serverinfo")
print(response.status_code)  # Should be 200
```

## Contributing

To add support for new authentication methods:

1. Create new class inheriting from `BrAPIOAuth2Session`
2. Implement `login()` method for specific format
3. Update `BrAPIClient` to support new auth type
4. Add tests and documentation

Example:
```python
class GIGWAOAuth2(BrAPIOAuth2Session):
    def __init__(self, base_url):
        super().__init__(
            base_url=base_url,
            token_endpoint="/gigwa/rest/gigwa/generateToken"
        )

    def login(self, username, password):
        # Implement GIGWA-specific authentication
        pass
```
