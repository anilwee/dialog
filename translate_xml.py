import xml.etree.ElementTree as ET
import yaml
import argparse
from datetime import datetime
import os
import requests
from urllib.parse import quote
from hashlib import md5
import time
import json

# Configuration
API_URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=si&dt=t&q="
REQUEST_DELAY = 0.5
SKIP_CHANNELS = {"ART Television", "Vasantham TV", "Nethra TV", "Shakthi TV", "Hi TV"}
TRANSLATION_CACHE_FILE = 'translation_cache.json'

def debug_log(message):
    print(f"[DEBUG] {datetime.now().isoformat()} - {message}")
    with open('translation_debug.log', 'a', encoding='utf-8') as log:
        log.write(f"{datetime.now().isoformat()} - {message}\n")

def load_translations(yaml_file):
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        debug_log(f"YAML load error: {str(e)}")
        return {}

def load_translation_cache():
    try:
        with open(TRANSLATION_CACHE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_translation_cache(cache):
    with open(TRANSLATION_CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_string_hash(text):
    return md5(text.strip().lower().encode('utf-8')).hexdigest()

def translate_text(text, translations, cache):
    if not text or not text.strip():
        return text
    
    text_hash = get_string_hash(text)
    
    # Check manual translations first
    if text in translations:
        cache[text_hash] = translations[text]
        return translations[text]
    
    # Check case-insensitive matches
    text_lower = text.lower()
    for key, value in translations.items():
        if key.lower() == text_lower:
            cache[text_hash] = value
            return value
    
    # Check cache
    if text_hash in cache:
        return cache[text_hash]
    
    # API fallback
    try:
        encoded_text = quote(text)
        response = requests.get(API_URL + encoded_text, timeout=5)
        response.raise_for_status()
        translated = response.json()[0][0][0]
        cache[text_hash] = translated
        time.sleep(REQUEST_DELAY)
        return translated
    except Exception as e:
        debug_log(f"API translation failed for '{text}': {str(e)}")
        return text

def process_xml(input_path, output_path, translations, max_api_calls=500):
    cache = load_translation_cache()
    api_calls = 0
    
    try:
        tree = ET.parse(input_path)
        root = tree.getroot()
        stats = {
            'translated': 0,
            'duplicates': 0,
            'skipped_channels': 0,
            'cached': 0
        }

        for programme in root.findall('.//programme'):
            channel_id = programme.get('channel', '')
            
            if channel_id in SKIP_CHANNELS:
                stats['skipped_channels'] += 1
                continue
            
            # Process titles
            si_title = programme.find('title[@lang="si"]')
            if si_title is not None and si_title.text.strip():
                original = si_title.text
                if get_string_hash(original) in cache:
                    si_title.text = cache[get_string_hash(original)]
                    stats['cached'] += 1
                else:
                    si_title.text = translate_text(original, translations, cache)
                    if si_title.text != original:
                        stats['translated'] += 1
                        if 'http' in API_URL:
                            api_calls += 1
                            if api_calls >= max_api_calls:
                                debug_log("Reached max API calls limit")
                                break
            
            # Process descriptions
            si_desc = programme.find('desc[@lang="si"]')
            if si_desc is not None and si_desc.text.strip():
                original = si_desc.text
                if get_string_hash(original) in cache:
                    si_desc.text = cache[get_string_hash(original)]
                    stats['cached'] += 1
                else:
                    si_desc.text = translate_text(original, translations, cache)
                    if si_desc.text != original:
                        stats['translated'] += 1
                        if 'http' in API_URL:
                            api_calls += 1
                            if api_calls >= max_api_calls:
                                debug_log("Reached max API calls limit")
                                break

        save_translation_cache(cache)
        debug_log(
            f"Stats: Translated: {stats['translated']}, "
            f"Cached: {stats['cached']}, "
            f"Skipped channels: {stats['skipped_channels']}, "
            f"API calls made: {api_calls}"
        )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        return True

    except Exception as e:
        debug_log(f"Processing error: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='public/lk.xml', help='Input XML path')
    parser.add_argument('--output', '-o', default='public/si.xml', help='Output XML path')
    parser.add_argument('--mappings', '-m', default='translation_mappings.yml', help='Translation mappings YAML')
    parser.add_argument('--max-api-calls', type=int, default=500, help='Maximum API calls to make')
    args = parser.parse_args()

    translations = load_translations(args.mappings)
    debug_log(f"Loaded {len(translations)} manual translations")

    if not os.path.exists(args.input):
        debug_log("Generating minimal SI XML")
        root = ET.Element('tv')
        ET.SubElement(root, 'channel', {'id': 'default'})
        ET.ElementTree(root).write(args.output, encoding='utf-8', xml_declaration=True)
    else:
        success = process_xml(
            args.input,
            args.output,
            translations,
            args.max_api_calls
        )
        debug_log(f"Process {'completed' if success else 'failed'}")
