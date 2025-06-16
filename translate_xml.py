import xml.etree.ElementTree as ET
import yaml
import os
from datetime import datetime
from hashlib import md5
import json
import sys

# Configuration
SKIP_CHANNELS = {"ART Television", "Vasantham TV", "Nethra TV", "Shakthi TV", "Hi TV"}
CACHE_FILE = '.translation_cache.json'

def debug_log(message):
    timestamp = datetime.now().isoformat()
    log_msg = f"[DEBUG] {timestamp} - {message}"
    print(log_msg)
    with open('translation_debug.log', 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def load_translations():
    try:
        with open('translation_mappings.yml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        debug_log("translation_mappings.yml not found. No translations will be applied.")
        return {}
    except Exception as e:
        debug_log(f"Failed to load translations: {str(e)}")
        return {}

def load_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def process_xml():
    translations = load_translations()
    cache = load_cache()
    stats = {'cached': 0, 'translated': 0, 'skipped': 0}

    try:
        os.makedirs('public', exist_ok=True)

        # Create minimal XML if source doesn't exist
        if not os.path.exists('public/lk.xml'):
            debug_log("Generating minimal si.xml")
            root = ET.Element('tv')
            ET.SubElement(root, 'channel', {'id': 'default'})
            ET.ElementTree(root).write('public/si.xml', encoding='utf-8', xml_declaration=True)
            return True

        tree = ET.parse('public/lk.xml')
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
        debug_log(f"Translation stats: {stats}")

        tree.write('public/si.xml', encoding='utf-8', xml_declaration=True)
        return True

    except Exception as e:
        debug_log(f"Critical error: {str(e)}")
        return False

if __name__ == "__main__":
    success = process_xml()
    debug_log(f"Process {'completed successfully' if success else 'failed'}")
    if not success:
        sys.exit(1)
