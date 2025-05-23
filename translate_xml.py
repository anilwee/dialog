import xml.etree.ElementTree as ET
import yaml
import os
from datetime import datetime

def debug_log(message):
    print(f"[DEBUG] {datetime.now().isoformat()} - {message}")
    with open('translation_debug.log', 'a', encoding='utf-8') as log:
        log.write(f"{datetime.now().isoformat()} - {message}\n")

def load_translations(yaml_file):
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            translations = yaml.safe_load(f) or {}
            debug_log(f"Loaded {len(translations)} translations from {yaml_file}")
            return translations
    except Exception as e:
        debug_log(f"Error loading {yaml_file}: {str(e)}")
        return {}

def translate_content(text, translations):
    if not text or not text.strip():
        return text
    return translations.get(text, text)

def process_xml(input_path, output_path, translations):
    try:
        debug_log(f"Processing {input_path} → {output_path}")
        
        if not os.path.exists(input_path):
            debug_log(f"Input file not found: {input_path}")
            return False

        tree = ET.parse(input_path)
        root = tree.getroot()
        
        # Counters for debugging
        channels_processed = 0
        programs_translated = 0
        
        for channel in root.findall('.//channel'):
            channel_id = channel.get('id', '')
            
            # Translate channel if ID matches
            if channel_id in translations:
                # Add Sinhala name while preserving original ID
                channel.set('name', translations[channel_id])
                channels_processed += 1
                debug_log(f"Processing channel ID: {channel_id}")
                
                # Translate all programs in this channel
                for program in channel.findall('.//program'):
                    # Translate attributes
                    for attr in program.attrib:
                        if program.attrib[attr] in translations:
                            program.attrib[attr] = translations[program.attrib[attr]]
                            programs_translated += 1
                    
                    # Translate text content
                    for elem in program:
                        if elem.text and elem.text.strip():
                            translated = translate_content(elem.text, translations)
                            if translated != elem.text:
                                elem.text = translated
                                programs_translated += 1
        
        debug_log(f"Translated {channels_processed} channels and {programs_translated} programs")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write output
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        debug_log(f"Successfully wrote to {output_path}")
        return True
        
    except Exception as e:
        debug_log(f"Error processing XML: {str(e)}")
        return False

if __name__ == "__main__":
    config = {
        'input_file': 'public/lk.xml',
        'output_file': 'public/si.xml',
        'mappings_file': 'translation_mappings.yml'
    }
    
    debug_log("Starting translation process")
    translations = load_translations(config['mappings_file'])
    
    success = process_xml(
        config['input_file'],
        config['output_file'],
        translations
    )
    
    debug_log(f"Process {'completed successfully' if success else 'failed'}")
