import os
import requests
import gzip
import xml.etree.ElementTree as ET

# URL of the source XML GZ file
SOURCE_URL = "https://github.com/anilwee/dialog/raw/refs/heads/main/public/epg.xml.gz"

# Path to save the generated lk.xml file
OUTPUT_FILE = "public/lk.xml"

def fetch_and_extract_xml(url):
    """
    Fetch gzipped XML data from the given URL and extract it.
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with gzip.GzipFile(fileobj=response.raw) as gz:
        xml_data = gz.read()
    return xml_data.decode('utf-8')

def customize_xml(xml_content):
    """
    Customize the XML content as needed.
    """
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        # Save the problematic XML to a file for debugging
        with open("debug_invalid_xml.xml", "w", encoding="utf-8") as debug_file:
            debug_file.write(xml_content)
        raise

    # Example modification: Add a custom attribute to the root
    root.set("source", "customized")

    # Convert the modified XML tree back to a string
    return ET.tostring(root, encoding="unicode")

def save_xml_to_file(xml_content, file_path):
    """
    Save the XML content to the specified file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(xml_content)

def main():
    print("Fetching and extracting XML...")
    original_xml = fetch_and_extract_xml(SOURCE_URL)
    
    print("Customizing XML...")
    try:
        customized_xml = customize_xml(original_xml)
    except ET.ParseError:
        print("Failed to process the XML due to parsing errors.")
        return

    print(f"Saving XML to {OUTPUT_FILE}...")
    save_xml_to_file(customized_xml, OUTPUT_FILE)
    print("Done!")

if __name__ == "__main__":
    main()
