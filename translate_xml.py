import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
from datetime import datetime
import os
import yaml

# Load translation mappings from YAML
def load_translation_mappings(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file) or {}

# Enhanced text translation with context awareness
def translate_text(text, direct_mappings):
    # Trim whitespace and check for empty string
    text = text.strip()
    if not text:
        return text
    
    # Check for direct mappings first (case insensitive)
    text_lower = text.lower()
    if text_lower in direct_mappings:
        return direct_mappings[text_lower]
    
    # Special handling for XML-specific content we might not want to translate
    if text.startswith(('http://', 'https://', 'www.', '#')):
        return text
    
    # Use Google Translate for general translations
    try:
        translated = GoogleTranslator(source='en', target='si').translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"Translation failed for '{text}': {str(e)}")
        return text

# Process XML file with improved element handling
def translate_xml_file(input_path, output_path, direct_mappings):
    try:
        # Parse with XML declaration preservation
        parser = ET.XMLParser(encoding='utf-8')
        tree = ET.parse(input_path, parser=parser)
        root = tree.getroot()
        
        # Iterate through all elements
        for element in root.iter():
            # Translate element text if it exists and isn't just whitespace
            if element.text and element.text.strip():
                element.text = translate_text(element.text, direct_mappings)
            
            # Translate attribute values
            for attr in element.attrib:
                if element.attrib[attr].strip():
                    element.attrib[attr] = translate_text(element.attrib[attr], direct_mappings)
        
        # Write with proper XML declaration and UTF-8 encoding
        tree.write(output_path, encoding='utf-8', xml_declaration=True, short_empty_elements=False)
        print(f"Successfully translated XML saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error processing XML file: {str(e)}")
        return False

def main():
    # Configuration
    config = {
        'input_file': 'public/lk.xml',  # Source English XML
        'output_file': 'public/si.xml', # Target Sinhalese XML
        'mappings_file': 'translation_mappings.yml',
        'log_file': 'translation_log.txt'
    }
    
    # Ensure public directory exists
    os.makedirs(os.path.dirname(config['output_file']), exist_ok=True)
    
    # Load direct translation mappings
    direct_mappings = load_translation_mappings(config['mappings_file'])
    
    # Process the XML file
    success = translate_xml_file(config['input_file'], config['output_file'], direct_mappings)
    
    # Log completion
    with open(config['log_file'], 'a', encoding='utf-8') as log:
        status = "SUCCESS" if success else "FAILED"
        log.write(f"{datetime.now().isoformat()} - Translation {status}\n")

if __name__ == "__main__":
    main()
