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
            debug_log(f"Loaded {len(translations)} translations")
            return translations
    except Exception as e:
        debug_log(f"YAML load error: {str(e)}")
        return {}

def translate_content(text, translations):
    if not text or not text.strip():
        return text
    return translations.get(text, text)

def process_xml(input_path, output_path, translations):
    try:
        debug_log(f"Starting processing {input_path}")
        
        tree = ET.parse(input_path)
        root = tree.getroot()
        
        target_channels = ["Rupavahini", "Sirasa TV", "Siyatha TV"]
        processed_channels = 0
        translated_programs = 0
        
        for channel in root.findall('.//channel'):
            channel_id = channel.get('id', '')
            
            if channel_id in target_channels:
                debug_log(f"Processing channel: {channel_id}")
                processed_channels += 1
                
                # Update Sinhala display name
                for display_name in channel.findall('display-name'):
                    if display_name.get('lang') == 'si':
                        display_name.text = translations.get(channel_id, channel_id)
                        debug_log(f"Updated display-name to {display_name.text}")
                
                # Translate all program elements
                for program in channel.findall('.//program'):
                    translated_programs += 1
                    
                    # Translate program title
                    title = program.find('title')
                    if title is not None and title.text:
                        title.text = translate_content(title.text, translations)
                    
                    # Translate program description
                    desc = program.find('desc')
                    if desc is not None and desc.text:
                        desc.text = translate_content(desc.text, translations)
                    
                    # Translate program category
                    category = program.find('category')
                    if category is not None and category.text:
                        category.text = translate_content(category.text, translations)
        
        debug_log(f"Processed {processed_channels} channels and {translated_programs} programs")
        
        # Write output file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        debug_log(f"Successfully wrote {output_path}")
        return True
        
    except Exception as e:
        debug_log(f"XML processing error: {str(e)}")
        return False

if __name__ == "__main__":
    CONFIG = {
        'input': 'public/lk.xml',
        'output': 'public/si.xml',
        'mappings': 'translation_mappings.yml'
    }
    
    translations = load_translations(CONFIG['mappings'])
    if not translations:
        debug_log("No translations loaded - check YAML file")
    
    success = process_xml(CONFIG['input'], CONFIG['output'], translations)
    debug_log(f"Process {'succeeded' if success else 'failed'}")
