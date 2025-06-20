import xml.etree.ElementTree as ET
import yaml
import os
from datetime import datetime
from hashlib import md5
import json
import sys
import re

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

def apply_partial_translations(text, translations):
    """Replace all substrings found in translations keys with their corresponding value."""
    # Build regex alternation for all translation keys (longer keys first)
    sorted_keys = sorted(translations.keys(), key=len, reverse=True)
    pattern = re.compile('|'.join(map(re.escape, sorted_keys)))
    def replacer(match):
        return translations[match.group(0)]
    return pattern.sub(replacer, text)

def process_xml():
    translations = load_translations()
    cache = load_cache()
    stats = {'cached': 0, 'translated': 0, 'skipped': 0}

    try:
        os.makedirs('public', exist_ok=True)

        if not os.path.exists('public/lk.xml'):
            debug_log("Generating minimal si.xml")
            root = ET.Element('tv')
            ET.SubElement(root, 'channel', {'id': 'default'})
            ET.ElementTree(root).write('public/si.xml', encoding='utf-8', xml_declaration=True)
            return True

        tree = ET.parse('public/lk.xml')
        root = tree.getroot()

        for programme in root.findall('.//programme'):
            # No skipping any channels

            # Process titles
            title = programme.find('title[@lang="si"]')
            if title is not None and title.text:
                orig_text = title.text.strip()
                text_hash = md5(orig_text.encode()).hexdigest()
                if text_hash in cache:
                    title.text = cache[text_hash]
                    stats['cached'] += 1
                else:
                    new_text = apply_partial_translations(orig_text, translations)
                    if new_text != orig_text:
                        cache[text_hash] = new_text
                        title.text = new_text
                        stats['translated'] += 1

            # Process descriptions
            desc = programme.find('desc[@lang="si"]')
            if desc is not None and desc.text:
                orig_text = desc.text.strip()
                text_hash = md5(orig_text.encode()).hexdigest()
                if text_hash in cache:
                    desc.text = cache[text_hash]
                    stats['cached'] += 1
                else:
                    new_text = apply_partial_translations(orig_text, translations)
                    if new_text != orig_text:
                        cache[text_hash] = new_text
                        desc.text = new_text
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
