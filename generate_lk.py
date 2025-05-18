from lxml import etree
import os

INPUT_FILE = 'public/epg.xml'
OUTPUT_FILE = 'public/lk.xml'

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

    parser = etree.XMLParser(recover=True)
    tree = etree.parse(INPUT_FILE, parser)
    root = tree.getroot()

    new_root = etree.Element("tv")

    # Copy relevant channels
    valid_channels = set()
    for channel in root.findall("channel"):
        display_name = channel.find("display-name")
        if display_name is not None and display_name.text in LK_CHANNELS:
            new_root.append(channel)
            valid_channels.add(channel.get("id"))

    # Copy relevant programmes
    for programme in root.findall("programme"):
        if programme.get("channel") in valid_channels:
            new_root.append(programme)

    # Save filtered XML
    with open(OUTPUT_FILE, "wb") as f:
        f.write(etree.tostring(new_root, pretty_print=True, encoding='UTF-8', xml_declaration=True))

    print(f"Filtered EPG written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
