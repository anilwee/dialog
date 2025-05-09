import os
import requests
import xml.etree.ElementTree as ET

# URL to fetch the lk.xml file
SOURCE_URL = "https://raw.githubusercontent.com/anilwee/dialog/main/public/lk.xml"

# Path to save the generated dialog.xml file
OUTPUT_FILE = "public/dialog.xml"

def fetch_lk_xml(url):
    """
    Fetch lk.xml from the given URL.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def generate_tiled_xml(lk_xml_content):
    """
    Generate tiled XML (dialog.xml) from lk.xml content.
    """
    # Parse the original lk.xml
    root = ET.fromstring(lk_xml_content)

    # Create a new root element for dialog.xml
    tiled_root = ET.Element("TiledEPG")

    # Example logic: Convert each program into a tiled format
    for program in root.findall(".//programme"):
        tile = ET.SubElement(tiled_root, "Tile")
        tile.set("channel", program.get("channel"))
        tile.set("start", program.get("start"))
        tile.set("stop", program.get("stop"))

        title = program.find("title")
        if title is not None:
            ET.SubElement(tile, "Title").text = title.text

        desc = program.find("desc")
        if desc is not None:
            ET.SubElement(tile, "Description").text = desc.text

    # Convert the tiled XML tree to a string
    return ET.tostring(tiled_root, encoding="unicode")

def save_xml_to_file(xml_content, file_path):
    """
    Save the XML content to the specified file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(xml_content)

def main():
    print("Fetching lk.xml...")
    lk_xml_content = fetch_lk_xml(SOURCE_URL)

    print("Generating tiled XML (dialog.xml)...")
    dialog_xml_content = generate_tiled_xml(lk_xml_content)

    print(f"Saving dialog.xml to {OUTPUT_FILE}...")
    save_xml_to_file(dialog_xml_content, OUTPUT_FILE)
    print("Done!")

if __name__ == "__main__":
    main()
