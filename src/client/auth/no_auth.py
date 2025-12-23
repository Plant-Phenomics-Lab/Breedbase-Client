import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_base_session() -> requests.Session:
    """
    Create a standard requests session with retry logic but no authentication.
    Useful for public BrAPI endpoints.
    """
    session = requests.Session()
    
    # Configure retries
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Disable SSL verification for this session
    session.verify = False
    
    return session
