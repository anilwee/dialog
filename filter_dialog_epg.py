import gzip
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

# File paths
INPUT_FILE = "repo_folder/epg.xml.gz"  # Update this to the correct relative path of the XML file in your repo.
OUTPUT_FILE = "dialog.xml"

# List of allowed channels
ALLOWED_CHANNELS = [
    "ADA DERANA 24", "ART Television", "Buddhist TV", "Channel C", 
    "Channel One", "Citi Hitz", "Damsathara TV", "God TV/Swarga TV", 
    "Haritha TV", "Hi TV", "Hiru TV", "ITN", "Jaya TV", "Monara TV", 
    "Nethra TV", "Pragna TV", "Rangiri Sri Lanka", "Ridee TV", 
    "Rupavahini", "Shakthi TV", "Shraddha TV", "Sirasa TV", 
    "Siyatha TV", "Supreme TV", "Swarnawahini Live", 
    "Swarnawahini", "TV Derana", "TV Didula", "TV1 Sri Lanka", 
    "Vasantham TV"
]

# Time limit for filtering (48 hours from now)
TIME_LIMIT = datetime.now(timezone.utc) + timedelta(hours=48)

def parse_and_filter():
    # Open the gzipped XML file
    try:
        with gzip.open(INPUT_FILE, 'rt', encoding='utf-8') as f:
            tree = ET.parse(f)
            root = tree.getroot()

            # Filter channels
            for channel in root.findall("channel"):
                channel_id = channel.get("id")
                if channel_id not in ALLOWED_CHANNELS:
                    root.remove(channel)

            # Filter programmes
            for programme in root.findall("programme"):
                channel_id = programme.get("channel")
                start_time = datetime.strptime(programme.get("start")[:12], "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
                if channel_id not in ALLOWED_CHANNELS or start_time > TIME_LIMIT:
                    root.remove(programme)

            # Write the filtered XML to a new file
            tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    except FileNotFoundError:
        print(f"Error: The file {INPUT_FILE} was not found.")
        raise

if __name__ == "__main__":
    parse_and_filter()
