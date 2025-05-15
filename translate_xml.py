import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
from datetime import datetime
import os
import yaml

def load_translation_mappings(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file) or {}

def should_translate(channel_name):
    # Exact channel names to translate (case sensitive)
    channels_to_translate = {
        'Rupavahini', 
        'Sirasa TV', 
        'Siyatha TV'
    }
    return channel_name in channels_to_translate

def translate_text(text, direct_mappings, channel_name=None):
    text = text.strip()
    if not text:
        return text
    
    # First check direct mappings
    if text in direct_mappings:
        return direct_mappings[text]
    
    # Skip URLs and special values
    if text.startswith(('http://', 'https://', 'www.', '#')):
        return text
    
    # Only translate if it's from our target channels
    if channel_name and should_translate(channel_name):
        try:
            translated = GoogleTranslator(source='en', target='si').translate(text)
            return translated if translated else text
        except Exception as e:
            print(f"Translation failed for '{text}': {str(e)}")
    
    return text

def translate_xml_file(input_path, output_path, direct_mappings):
    try:
        parser = ET.XMLParser(encoding='utf-8')
        tree = ET.parse(input_path, parser=parser)
        root = tree.getroot()
        
        for channel in root.findall('.//channel'):
            channel_name = channel.get('name', '')
            translate_channel = should_translate(channel_name)
            
            # Translate channel name if in our list
            if translate_channel and 'name' in channel.attrib:
                channel.attrib['name'] = translate_text(
                    channel.attrib['name'], 
                    direct_mappings
                )
            
            # Translate program elements
            for program in channel.findall('.//program'):
                # Translate attributes
                for attr in program.attrib:
                    program.attrib[attr] = translate_text(
                        program.attrib[attr], 
                        direct_mappings,
                        channel_name
                    )
                
                # Translate child elements
                for elem in program:
                    if elem.text and elem.text.strip():
                        elem.text = translate_text(
                            elem.text, 
                            direct_mappings,
                            channel_name
                        )
        
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"Successfully created channel-specific translation at {output_path}")
        return True
    except Exception as e:
        print(f"Error processing XML file: {str(e)}")
        return False

def main():
    config = {
        'input_file': 'public/lk.xml',
        'output_file': 'public/si.xml',
        'mappings_file': 'translation_mappings.yml',
        'log_file': 'translation_log.txt'
    }
    
    os.makedirs(os.path.dirname(config['output_file']), exist_ok=True)
    direct_mappings = load_translation_mappings(config['mappings_file'])
    
    success = translate_xml_file(config['input_file'], config['output_file'], direct_mappings)
    
    with open(config['log_file'], 'a', encoding='utf-8') as log:
        status = "SUCCESS" if success else "FAILED"
        log.write(f"{datetime.now().isoformat()} - Channel-specific translation {status}\n")

if __name__ == "__main__":
    main()
