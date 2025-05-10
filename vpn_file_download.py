import os
import subprocess
import base64
import requests

# Configuration
OVPN_BASE64 = os.getenv("OVPN_FILE")  # OVPN file in base64 format
VPN_USERNAME = os.getenv("VPN_USERNAME")
VPN_PASSWORD = os.getenv("VPN_PASSWORD")
OUTPUT_DIR = "public"
EPG_URL = "https://watch.livecricketsl.xyz/epg/epg.xml.gz"

def decode_ovpn_config():
    """Decode the base64-encoded OVPN configuration and save it."""
    if not OVPN_BASE64:
        raise ValueError("OVPN_FILE environment variable is not set.")
    
    raw_config = base64.b64decode(OVPN_BASE64).decode("utf-8")
    with open("config.ovpn", "w") as f:
        f.write(raw_config)
    print("OVPN configuration decoded and saved to config.ovpn.")

def create_auth_file():
    """Create an auth.txt file with VPN credentials."""
    if not VPN_USERNAME or not VPN_PASSWORD:
        raise ValueError("VPN_USERNAME or VPN_PASSWORD environment variable is not set.")
    
    with open("auth.txt", "w") as f:
        f.write(f"{VPN_USERNAME}\n{VPN_PASSWORD}\n")
    os.chmod("auth.txt", 0o600)  # Secure the file
    print("Auth file created and secured.")

def run_openvpn():
    """Run OpenVPN to establish a VPN connection."""
    subprocess.run(["sudo", "openvpn", "--config", "config.ovpn", "--auth-user-pass", "auth.txt", "--daemon"])
    print("OpenVPN started. Waiting for connection...")
    subprocess.run(["sleep", "10"])  # Wait for the VPN connection to establish

def verify_vpn_connection():
    """Verify that the VPN connection is established."""
    result = subprocess.run(["curl", "--max-time", "10", "https://ipinfo.io"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to verify VPN connection.")
    print("VPN connection verified. External IP info:")
    print(result.stdout)

def download_epg_file():
    """Download the EPG file in GZIP format."""
    response = requests.get(EPG_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to download EPG file. HTTP Status Code: {response.status_code}")
    
    with open("epg.xml.gz", "wb") as f:
        f.write(response.content)
    print("EPG file downloaded as epg.xml.gz.")

def decompress_epg_file():
    """Decompress the EPG file."""
    subprocess.run(["gunzip", "-c", "epg.xml.gz"], stdout=open("epg.xml", "w"))
    print("EPG file decompressed to epg.xml.")

def move_files_to_public():
    """Move the EPG files to the public directory."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.rename("epg.xml.gz", os.path.join(OUTPUT_DIR, "epg.xml.gz"))
    os.rename("epg.xml", os.path.join(OUTPUT_DIR, "epg.xml"))
    print(f"Files moved to {OUTPUT_DIR} directory.")

def main():
    try:
        decode_ovpn_config()
        create_auth_file()
        run_openvpn()
        verify_vpn_connection()
        download_epg_file()
        decompress_epg_file()
        move_files_to_public()
        print("Workflow completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
