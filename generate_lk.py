import xml.etree.ElementTree as ET

# Input and output file paths
INPUT_FILE = "public/epg.xml"
OUTPUT_FILE = "public/lk.xml"

# List of channels to filter
FILTERED_CHANNELS = [
    "ADA DERANA 24", "ART Television", "Buddhist TV", "Channel C", "Channel One",
    "Citi Hitz", "Damsathara TV", "God TV/Swarga TV", "Haritha TV", "Hi TV",
    "Hiru TV", "ITN", "Jaya TV", "Monara TV", "Nethra TV", "Pragna TV",
    "Rangiri Sri Lanka", "Ridee TV", "Rupavahini", "Shakthi TV", "Shraddha TV",
    "Sirasa TV", "Siyatha TV", "Supreme TV", "Swarnawahini Live", "Swarnawahini",
    "TV Derana", "TV Didula", "TV1 Sri Lanka", "Vasantham TV", "ThePapare 1""
]

def parse_and_filter():
    """
    Parse the EPG XML file, filter for specific channels, and generate a new XML file.
    """
    try:
        tree = ET.parse(INPUT_FILE)
        root = tree.getroot()

        filtered_root = ET.Element('tv')
        channel_id_map = {}

        for channel in root.findall('channel'):
            display_name = channel.find('display-name').text
            if display_name in FILTERED_CHANNELS:
                filtered_root.append(channel)
                channel_id_map[channel.attrib['id']] = display_name

        for programme in root.findall('programme'):
            if programme.attrib['channel'] in channel_id_map:
                filtered_root.append(programme)

        filtered_tree = ET.ElementTree(filtered_root)
        filtered_tree.write(OUTPUT_FILE, encoding='utf-8', xml_declaration=True)
        print(f"Filtered LK file created: {OUTPUT_FILE}")

    except FileNotFoundError:
        print(f"Error: The file {INPUT_FILE} was not found.")
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")

if __name__ == "__main__":
    parse_and_filter()
