import xml.etree.ElementTree as ET
import os

# Define input and output file paths
INPUT_FILE = 'public/epg.xml'
OUTPUT_FILE = 'public/lk.xml'

# List of Sri Lankan channels to include
LK_CHANNELS = {
    "Rupavahini", "ITN", "Sirasa TV", "Siyatha TV", "Swarnavahini", "Hiru TV", "TV Derana",
    "TV Supreme", "Ridee TV", "Citi Hitz", "Channel Eye", "Nethra TV", "ART TV", "TV1 Sri Lanka",
    "Shakthi TV", "Vasantham TV", "ADA DERANA 24", "Rangiri Sri Lanka", "Buddhist TV",
    "Shraddha TV", "The Papare", "Monara TV", "TV Didula", "Hi TV"
}

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found.")
        return

    tree = ET.parse(INPUT_FILE)
    root = tree.getroot()

    new_root = ET.Element('tv')

    # Copy <channel> tags for LK channels
    for channel in root.findall('channel'):
        display_name = channel.find('display-name')
        if display_name is not None and display_name.text in LK_CHANNELS:
            new_root.append(channel)

    # Copy <programme> tags for LK channels
    for programme in root.findall('programme'):
        channel_attr = programme.attrib.get('channel')
        if channel_attr:
            for ch in root.findall('channel'):
                if ch.attrib.get('id') == channel_attr:
                    name = ch.find('display-name')
                    if name is not None and name.text in LK_CHANNELS:
                        new_root.append(programme)
                        break

    # Write to output file
    new_tree = ET.ElementTree(new_root)
    ET.indent(new_tree, space="  ")
    new_tree.write(OUTPUT_FILE, encoding='utf-8', xml_declaration=True)
    print(f"Filtered EPG written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
