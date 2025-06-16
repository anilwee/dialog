import xml.etree.ElementTree as ET
import yaml
import argparse
from datetime import datetime
import os
import requests
from urllib.parse import quote
from hashlib import md5

# Configuration
API_URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=si&dt=t&q="
REQUEST_DELAY = 0.5
SKIP_CHANNELS = {"ART Television", "Vasantham TV", "Nethra TV", "Shakthi TV", "Hi TV"}

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

def get_string_hash(text):
    return md5(text.strip().lower().encode('utf-8')).hexdigest()

def process_xml(input_path, output_path, translations):
    try:
        tree = ET.parse(input_path)
        root = tree.getroot()
        
        # Track processed strings and their translations
        processed_hashes = {}
        translated_count = 0
        duplicate_skips = 0
        skipped_channels = set()

        for programme in root.findall('.//programme'):
            channel_id = programme.get('channel', '')
            
            # Skip specified channels
            if channel_id in SKIP_CHANNELS:
                if channel_id not in skipped_channels:
                    debug_log(f"Skipping channel: {channel_id}")
                    skipped_channels.add(channel_id)
                continue
            
            # Process titles
            si_title = programme.find('title[@lang="si"]')
            if si_title is not None and si_title.text and si_title.text.strip():
                text_hash = get_string_hash(si_title.text)
                if text_hash in processed_hashes:
                    si_title.text = processed_hashes[text_hash]
                    duplicate_skips += 1
                else:
                    original = si_title.text
                    # First try manual translations
                    if original in translations:
                        si_title.text = translations[original]
                    else:
                        # Try case-insensitive match
                        original_lower = original.lower()
                        matched = False
                        for key, value in translations.items():
                            if key.lower() == original_lower:
                                si_title.text = value
                                matched = True
                                break
                        if not matched:
                            # Fall back to API
                            try:
                                encoded_text = quote(original)
                                response = requests.get(API_URL + encoded_text)
                                response.raise_for_status()
                                si_title.text = response.json()[0][0][0]
                                time.sleep(REQUEST_DELAY)
                            except Exception as e:
                                debug_log(f"API translation failed: {str(e)}")
                                si_title.text = original
                    
                    if si_title.text != original:
                        processed_hashes[text_hash] = si_title.text
                        translated_count += 1
            
            # Process descriptions (same logic as titles)
            si_desc = programme.find('desc[@lang="si"]')
            if si_desc is not None and si_desc.text and si_desc.text.strip():
                text_hash = get_string_hash(si_desc.text)
                if text_hash in processed_hashes:
                    si_desc.text = processed_hashes[text_hash]
                    duplicate_skips += 1
                else:
                    original = si_desc.text
                    if original in translations:
                        si_desc.text = translations[original]
                    else:
                        original_lower = original.lower()
                        matched = False
                        for key, value in translations.items():
                            if key.lower() == original_lower:
                                si_desc.text = value
                                matched = True
                                break
                        if not matched:
                            try:
                                encoded_text = quote(original)
                                response = requests.get(API_URL + encoded_text)
                                response.raise_for_status()
                                si_desc.text = response.json()[0][0][0]
                                time.sleep(REQUEST_DELAY)
                            except Exception as e:
                                debug_log(f"API translation failed: {str(e)}")
                                si_desc.text = original
                    
                    if si_desc.text != original:
                        processed_hashes[text_hash] = si_desc.text
                        translated_count += 1

        debug_log(f"Translated: {translated_count}, Skipped duplicates: {duplicate_skips}, Skipped channels: {len(skipped_channels)}")
        
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
    args = parser.parse_args()

    translations = load_translations(args.mappings)
    debug_log(f"Loaded {len(translations)} manual translations")

    if not os.path.exists(args.input):
        debug_log("Source file missing, generating minimal SI XML")
        root = ET.Element('tv')
        ET.SubElement(root, 'channel', {'id': 'default'})
        ET.ElementTree(root).write(args.output, encoding='utf-8', xml_declaration=True)
    else:
        success = process_xml(args.input, args.output, translations)
        debug_log(f"Process {'succeeded' if success else 'failed'}")
