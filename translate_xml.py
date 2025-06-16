import xml.etree.ElementTree as ET
import yaml
import os
from datetime import datetime
from hashlib import md5
import json

# Configuration
SKIP_CHANNELS = {"ART Television", "Vasantham TV", "Nethra TV", "Shakthi TV", "Hi TV"}
CACHE_FILE = '.translation_cache.json'

def debug_log(message):
    print(f"[DEBUG] {datetime.now().isoformat()} - {message}")
    with open('translation_debug.log', 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")

def load_cache():
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def process_xml(input_path, output_path, translations):
    cache = load_cache()
    stats = {'cached': 0, 'translated': 0, 'skipped': 0}
    
    try:
        tree = ET.parse(input_path)
        root = tree.getroot()
        
        for programme in root.findall('.//programme'):
            channel = programme.get('channel', '')
            if channel in SKIP_CHANNELS:
                stats['skipped'] += 1
                continue
            
            # Process titles
            if (title := programme.find('title[@lang="si"]')) is not None and title.text:
                text_hash = md5(title.text.strip().encode()).hexdigest()
                if text_hash in cache:
                    title.text = cache[text_hash]
                    stats['cached'] += 1
                elif title.text in translations:
                    cache[text_hash] = translations[title.text]
                    title.text = translations[title.text]
                    stats['translated'] += 1
            
            # Process descriptions
            if (desc := programme.find('desc[@lang="si"]')) is not None and desc.text:
                text_hash = md5(desc.text.strip().encode()).hexdigest()
                if text_hash in cache:
                    desc.text = cache[text_hash]
                    stats['cached'] += 1
                elif desc.text in translations:
                    cache[text_hash] = translations[desc.text]
                    desc.text = translations[desc.text]
                    stats['translated'] += 1

        save_cache(cache)
        debug_log(f"Stats: {stats}")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        return True

    except Exception as e:
        debug_log(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        translations = yaml.safe_load(open('translation_mappings.yml')) or {}
    except Exception as e:
        debug_log(f"Failed to load translations: {str(e)}")
        translations = {}

    input_path = 'public/lk.xml'
    output_path = 'public/si.xml'
    
    if not os.path.exists(input_path):
        debug_log("Creating minimal si.xml")
        root = ET.Element('tv')
        ET.SubElement(root, 'channel', {'id': 'default'})
        ET.ElementTree(root).write(output_path, encoding='utf-8', xml_declaration=True)
    else:
        success = process_xml(input_path, output_path, translations)
        debug_log(f"Process {'succeeded' if success else 'failed'}")
