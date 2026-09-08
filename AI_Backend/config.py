## This is the central place to load all API credentials from environment variables. 

import os
from dotenv import load_dotenv
load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_RIVA_SERVER = os.getenv("NVIDIA_RIVA_SERVER" , "grpc.nvcf.nvidia.com:443")
NVIDIA_RIVA_FUNCTION_ID = os.getenv(
    "NVIDIA_RIVA_FUNCTION_ID", "0778f2eb-b64d-45e7-acae-7dd9b9b35b4d"
)


def check_nvidia_config():
    
    if not NVIDIA_API_KEY:
        print(" Missing NVIDIA_API_KEY. Check your .env file.")
    else:
        print(" NVIDIA_API_KEY is set — translate.py is ready to run.")

if __name__ == "__main__":
    check_nvidia_config()