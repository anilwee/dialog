import gzip
import xml.etree.ElementTree as ET
import os

# Input and output file paths
INPUT_FILE = "epg.xml.gz"  # Update this path if the file is in a different location
OUTPUT_FILE = "dialog.xml"

# List of channels to filter
FILTERED_CHANNELS = [
    "ADA DERANA 24", "ART Television", "Buddhist TV", "Channel C", "Channel One",
    "Citi Hitz", "Damsathara TV", "God TV/Swarga TV", "Haritha TV", "Hi TV",
    "Hiru TV", "ITN", "Jaya TV", "Monara TV", "Nethra TV", "Pragna TV",
    "Rangiri Sri Lanka", "Ridee TV", "Rupavahini", "Shakthi TV", "Shraddha TV",
    "Sirasa TV", "Siyatha TV", "Supreme TV", "Swarnawahini Live", "Swarnawahini",
    "TV Derana", "TV Didula", "TV1 Sri Lanka", "Vasantham TV"
]

def parse_and_filter():
    """
    Parse the compressed EPG XML file, filter for specific channels, and generate a new XML file.
    """
    if not os.path.exists(INPUT_FILE):
        print(f"Error: The file {INPUT_FILE} was not found.")
        return

    try:
        # Open the compressed XML file
        print(f"Opening file: {INPUT_FILE}")
        with gzip.open(INPUT_FILE, 'rt', encoding='utf-8') as f:
            tree = ET.parse(f)
            root = tree.getroot()
        print(f"File opened successfully: {INPUT_FILE}")

        # Create a new root for the filtered XML
        filtered_root = ET.Element('tv')

        # Map display-name to channel ID
        channel_id_map = {}
        for channel in root.findall('channel'):
            display_name = channel.find('display-name').text
            if display_name in FILTERED_CHANNELS:
                filtered_root.append(channel)
                channel_id_map[channel.attrib['id']] = display_name

        # Copy only programs belonging to the filtered channels
        for programme in root.findall('programme'):
            if programme.attrib['channel'] in channel_id_map:
                filtered_root.append(programme)

        # Write the filtered XML to the output file
        filtered_tree = ET.ElementTree(filtered_root)
        filtered_tree.write(OUTPUT_FILE, encoding='utf-8', xml_declaration=True)
        print(f"Filtered EPG file created: {OUTPUT_FILE}")

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")

if __name__ == "__main__":
    parse_and_filter()
