from config.type import BrapiServerConfig
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

_CONFIG = {
    'mode': os.getenv("MODE", "stdio"),
    'port': int(os.getenv("PORT", 8000)),
    'name': os.getenv("NAME", "sweetpotatobase"),
    'base_url': os.getenv("BASE_URL", "https://sweetpotatobase.org/brapi/v2"),
    'authtype': os.getenv("AUTH_TYPE"),
    'username': os.getenv("BRAPI_USERNAME"),
    'password': os.getenv("BRAPI_PASSWORD"),
    'session_dir_override': os.getenv("DOWNLOAD_DIR_OVERRIDE"), # As follows: in STDIO mode, the data is downloaded locally. At first, all Data is downloaded to sessions. So in STDIO mode this becomes the de facto downloads directory. 
}

config = BrapiServerConfig(**_CONFIG)