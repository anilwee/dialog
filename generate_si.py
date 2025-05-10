import os
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator  # Install via `pip install deep-translator`

# Input and output file paths
INPUT_FILE = "public/lk.xml"
OUTPUT_FILE = "public/si.xml"

def translate_epg():
    """
    Translate the EPG content from English to Sinhala.
    """
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

        # Check if input file exists
        if not os.path.exists(INPUT_FILE):
            raise FileNotFoundError(f"Input file '{INPUT_FILE}' does not exist.")

        # Parse the input XML file
        tree = ET.parse(INPUT_FILE)
        root = tree.getroot()

        # Initialize the translator
        translator = GoogleTranslator(source='en', target='si')

        # Translate titles and descriptions
        for programme in root.findall('programme'):
            title = programme.find('title')
            if title is not None and title.text:
                try:
                    title.text = translator.translate(title.text)
                except Exception as e:
                    print(f"Failed to translate title: {title.text}. Error: {e}")

            description = programme.find('desc')
            if description is not None and description.text:
                try:
                    description.text = translator.translate(description.text)
                except Exception as e:
                    print(f"Failed to translate description: {description.text}. Error: {e}")

        # Write the translated XML to the output file
        tree.write(OUTPUT_FILE, encoding='utf-8', xml_declaration=True)
        print(f"Translated EPG file created: {OUTPUT_FILE}")

    except FileNotFoundError as fnf_error:
        print(f"File Not Found Error: {fnf_error}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    translate_epg()
