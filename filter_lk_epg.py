import xml.etree.ElementTree as ET
import sys

def filter_epg(input_file, output_file, filtered_channels):
    """
    Filters the EPG XML file to include only specific channels.

    Args:
        input_file (str): Path to the input EPG XML file.
        output_file (str): Path to the output filtered XML file.
        filtered_channels (list): List of channel display names to include.
    """
    try:
        # Parse the input XML file
        tree = ET.parse(input_file)
    except ET.ParseError as e:
        # Log the error and exit
        print(f"Error parsing XML file: {e}")
        sys.exit(1)

    root = tree.getroot()

    # Create a new root for the filtered XML
    filtered_root = ET.Element('tv')

    # Map display-name to channel ID
    channel_id_map = {}
    for channel in root.findall('channel'):
        display_name = channel.find('display-name').text
        if display_name in filtered_channels:
            filtered_root.append(channel)
            channel_id_map[channel.attrib['id']] = display_name

    # Copy only programs belonging to the filtered channels
    for programme in root.findall('programme'):
        if programme.attrib['channel'] in channel_id_map:
            filtered_root.append(programme)

    # Write the filtered XML to the output file
    filtered_tree = ET.ElementTree(filtered_root)
    filtered_tree.write(output_file, encoding='utf-8', xml_declaration=True)

# Main execution
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python filter_lk_epg.py <input_epg.xml> <output_lk.xml>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Define the list of channels to filter
    filtered_channels = [
        "ADA DERANA 24", "ART Television", "Buddhist TV", "Channel C", "Channel One",
        "Citi Hitz", "Damsathara TV", "God TV/Swarga TV", "Haritha TV", "Hi TV",
        "Hiru TV", "ITN", "Jaya TV", "Monara TV", "Nethra TV", "Pragna TV",
        "Rangiri Sri Lanka", "Ridee TV", "Rupavahini", "Shakthi TV", "Shraddha TV",
        "Sirasa TV", "Siyatha TV", "Supreme TV", "Swarnawahini Live", "Swarnawahini",
        "TV Derana", "TV Didula", "TV1 Sri Lanka", "Vasantham TV"
    ]

    filter_epg(input_file, output_file, filtered_channels)
    print(f"Filtered EPG file created: {output_file}")
