import os
from lxml import etree

# Replace with your source XML or data generation logic
SOURCE_XML_PATH = 'source.xml'
OUTPUT_XML_PATH = 'public/lk.xml'

def filter_logic(element):
    # Example filter: keep only channels with id starting with "LK"
    # Adjust this filter as needed for your requirements
    return element.get('id', '').startswith('LK')

def generate_filtered_lk():
    if not os.path.exists(SOURCE_XML_PATH):
        print(f"Source XML file {SOURCE_XML_PATH} not found.")
        return

    tree = etree.parse(SOURCE_XML_PATH)
    root = tree.getroot()

    # Create new root for filtered XML
    filtered_root = etree.Element(root.tag, root.attrib)

    # Copy relevant child elements according to filter
    for child in root:
        if filter_logic(child):
            filtered_root.append(child)

    # Save filtered XML
    os.makedirs(os.path.dirname(OUTPUT_XML_PATH), exist_ok=True)
    with open(OUTPUT_XML_PATH, 'wb') as f:
        f.write(etree.tostring(filtered_root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))

    print(f"Filtered lk.xml generated at {OUTPUT_XML_PATH}")

if __name__ == "__main__":
    generate_filtered_lk()
