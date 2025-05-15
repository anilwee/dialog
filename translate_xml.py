import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
from datetime import datetime
import os
import yaml

def debug_log(message):
    print(f"[DEBUG] {datetime.now().isoformat()} - {message}")
    with open('translation_debug.log', 'a', encoding='utf-8') as log:
        log.write(f"{datetime.now().isoformat()} - {message}\n")

def load_translation_mappings(yaml_file):
    try:
        with open(yaml_file, 'r', encoding='utf-8') as file:
            debug_log(f"Loaded mappings from {yaml_file}")
            return yaml.safe_load(file) or {}
    except Exception as e:
        debug_log(f"Error loading {yaml_file}: {str(e)}")
        return {}

def should_translate(channel_name):
    channels_to_translate = {'Rupavahini', 'Sirasa TV', 'Siyatha TV'}
    debug_log(f"Checking channel: {channel_name}")
    return channel_name in channels_to_translate

def translate_xml_file(input_path, output_path, direct_mappings):
    try:
        debug_log(f"Starting translation: {input_path} → {output_path}")
        
        # Verify input file exists
        if not os.path.exists(input_path):
            debug_log(f"Input file not found: {input_path}")
            return False
            
        parser = ET.XMLParser(encoding='utf-8')
        tree = ET.parse(input_path, parser=parser)
        root = tree.getroot()
        
        debug_log(f"Found {len(root.findall('.//channel'))} channels in XML")
        
        for channel in root.findall('.//channel'):
            channel_name = channel.get('name', '')
            if should_translate(channel_name):
                debug_log(f"Translating channel: {channel_name}")
                
                # Channel name translation
                if 'name' in channel.attrib:
                    channel.attrib['name'] = direct_mappings.get(channel_name, channel_name)
                
                # Program translation
                for program in channel.findall('.//program'):
                    for attr in program.attrib:
                        program.attrib[attr] = direct_mappings.get(program.attrib[attr], program.attrib[attr])
                    
                    for elem in program:
                        if elem.text and elem.text.strip():
                            elem.text = direct_mappings.get(elem.text, elem.text)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write output file
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        debug_log(f"Successfully wrote output to {output_path}")
        
        # Verify output file was created
        if os.path.exists(output_path):
            debug_log("Output file verification: SUCCESS")
            return True
        else:
            debug_log("Output file verification: FAILED")
            return False
            
    except Exception as e:
        debug_log(f"Error in translate_xml_file: {str(e)}")
        return False

def main():
    config = {
        'input_file': 'public/lk.xml',
        'output_file': 'public/si.xml',
        'mappings_file': 'translation_mappings.yml',
        'debug_log': 'translation_debug.log'
    }
    
    debug_log("Starting translation process")
    debug_log(f"Config: {config}")
    
    direct_mappings = load_translation_mappings(config['mappings_file'])
    debug_log(f"Loaded {len(direct_mappings)} direct mappings")
    
    success = translate_xml_file(
        config['input_file'],
        config['output_file'],
        direct_mappings
    )
    
    debug_log(f"Process completed: {'SUCCESS' if success else 'FAILED'}")

if __name__ == "__main__":
    main()
