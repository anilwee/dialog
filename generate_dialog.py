import xml.etree.ElementTree as ET
import os

# Input and output file paths
INPUT_FILE = "public/lk.xml"
OUTPUT_FILE = "public/dialog.xml"

def generate_tiled_dialog():
    """
    Parse the LK XML file and generate a tiled dialog XML file.
    """
    try:
        # Check if the input file exists
        if not os.path.exists(INPUT_FILE):
            print(f"Error: The file {INPUT_FILE} was not found.")
            return

        # Parse the input XML file
        tree = ET.parse(INPUT_FILE)
        root = tree.getroot()

        # Create a new root for the dialog XML
        dialog_root = ET.Element('dialog')

        # Example transformation: Tiling data into dialog format
        for programme in root.findall('programme'):
            dialog_entry = ET.SubElement(dialog_root, 'entry')
            title = programme.find('title').text if programme.find('title') is not None else "Unknown Title"
            start = programme.attrib.get('start', "Unknown Start")
            channel = programme.attrib.get('channel', "Unknown Channel")

            ET.SubElement(dialog_entry, 'title').text = title
            ET.SubElement(dialog_entry, 'start').text = start
            ET.SubElement(dialog_entry, 'channel').text = channel

        # Write the dialog XML to the output file
        dialog_tree = ET.ElementTree(dialog_root)
        dialog_tree.write(OUTPUT_FILE, encoding='utf-8', xml_declaration=True)
        print(f"Dialog XML file created: {OUTPUT_FILE}")

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    generate_tiled_dialog()
