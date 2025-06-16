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
    # Try exact match first
    if text in translations:
        return translations[text]
    # Try case-insensitive match
    text_lower = text.lower()
    for key, value in translations.items():
        if key.lower() == text_lower:
            return value
    return text

def process_xml(input_path, output_path, translations):
    try:
        debug_log(f"Starting processing {input_path}")
        
        tree = ET.parse(input_path)
        root = tree.getroot()
        
        target_channels = ["Rupavahini", "Sirasa TV", "Siyatha TV"]
        processed_channels = set()
        translated_programs = 0
        
        # First pass: Update channel display names
        for channel in root.findall('.//channel'):
            channel_id = channel.get('id', '')
            if channel_id in target_channels:
                for display_name in channel.findall('display-name'):
                    if display_name.get('lang') == 'si':
                        display_name.text = translations.get(channel_id, channel_id)
                        debug_log(f"Updated {channel_id} display-name to {display_name.text}")
                        processed_channels.add(channel_id)
        
        # Second pass: Translate programs
        for programme in root.findall('.//programme'):
            channel_id = programme.get('channel', '')
            if channel_id in processed_channels:
                translated_programs += 1
                
                # Translate title
                title = programme.find('title[@lang="si"]')
                if title is not None and title.text:
                    original = title.text
                    title.text = translate_content(original, translations)
                    if title.text != original:
                        debug_log(f"Translated title: {original} → {title.text}")
                
                # Translate description
                desc = programme.find('desc[@lang="si"]')
                if desc is not None and desc.text:
                    original = desc.text
                    desc.text = translate_content(original, translations)
                    if desc.text != original:
                        debug_log(f"Translated desc: {original} → {desc.text}")
        
        debug_log(f"Processed {len(processed_channels)} channels and {translated_programs} programmes")
        
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
