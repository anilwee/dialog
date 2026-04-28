import requests
import os
from datetime import datetime

def download_epg():
    url = "https://api.viulk.xyz/epg/xml"
    filename = "epg.xml"
    
    print(f"[{datetime.now().isoformat()}] Downloading EPG from {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Check if file is not empty
        if os.path.getsize(filename) > 0:
            print(f"[{datetime.now().isoformat()}] Successfully saved to {filename}")
            print(f"File size: {os.path.getsize(filename)} bytes")
        else:
            print(f"[{datetime.now().isoformat()}] WARNING: Downloaded file is empty")
            
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().isoformat()}] ERROR: Failed to download: {e}")
        raise

if __name__ == "__main__":
    download_epg()
