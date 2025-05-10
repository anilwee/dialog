import xml.etree.ElementTree as ET
from googletrans import Translator  # Install via `pip install googletrans==4.0.0-rc1`

# Input and output file paths
INPUT_FILE = "public/lk.xml"
OUTPUT_FILE = "public/si.xml"

def translate_epg():
    """
    Translate the EPG content from English to Sinhala.
    """
    try:
        # Parse the input XML file
        tree = ET.parse(INPUT_FILE)
        root = tree.getroot()

        # Initialize the translator
        translator = Translator()

        # Translate titles and descriptions
        for programme in root.findall('programme'):
            title = programme.find('title')
            if title is not None:
                title.text = translator.translate(title.text, src='en', dest='si').text

            description = programme.find('desc')
            if description is not None:
                description.text = translator.translate(description.text, src='en', dest='si').text

        # Write the translated XML to the output file
        tree.write(OUTPUT_FILE, encoding='utf-8', xml_declaration=True)
        print(f"Translated EPG file created: {OUTPUT_FILE}")

    except FileNotFoundError:
        print(f"Error: The file {INPUT_FILE} was not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    translate_epg()
