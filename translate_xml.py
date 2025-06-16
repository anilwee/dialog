import xml.etree.ElementTree as ET
import requests
import argparse
from datetime import datetime
from urllib.parse import quote
import time
import os

# Configuration
API_URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=si&dt=t&q="
REQUEST_DELAY = 0.5

def debug_log(message):
    print(f"[DEBUG] {datetime.now().isoformat()} - {message}")
    with open('translation_debug.log', 'a', encoding='utf-8') as log:
        log.write(f"{datetime.now().isoformat()} - {message}\n")

def translate_text(text):
    """Translate text to Sinhala while preserving placeholders"""
    if not text or not text.strip():
        return text
    
    try:
        encoded_text = quote(text)
        response = requests.get(API_URL + encoded_text)
        response.raise_for_status()
        translated_text = response.json()[0][0][0]
        debug_log(f"Translated: '{text}' → '{translated_text}'")
        return translated_text
    except Exception as e:
        debug_log(f"Translation error: {str(e)}")
        return text

def process_xml(input_path, output_path, preserve_channels=True):
    try:
        debug_log(f"Processing {input_path} (Preserve Channels: {preserve_channels})")
        tree = ET.parse(input_path)
        root = tree.getroot()
        translated_count = 0

        # Translate only programme content (title/desc with lang="si")
        for programme in root.findall('.//programme'):
            # Title translation
            si_title = programme.find('title[@lang="si"]')
            if si_title is not None and si_title.text:
                original = si_title.text
                si_title.text = translate_text(original)
                if si_title.text != original:
                    translated_count += 1
            
            # Description translation
            si_desc = programme.find('desc[@lang="si"]')
            if si_desc is not None and si_desc.text:
                original = si_desc.text
                si_desc.text = translate_text(original)
                if si_desc.text != original:
                    translated_count += 1
            
            time.sleep(REQUEST_DELAY)

        debug_log(f"Translated {translated_count} programme elements")
        
        # Write output
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        return True

    except Exception as e:
        debug_log(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='public/lk.xml', help='Input XML file path')
    parser.add_argument('--output', '-o', default='public/si.xml', help='Output XML file path')
    parser.add_argument('--preserve-channels', action='store_true', help='Keep channel names untranslated')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        debug_log(f"Source file {args.input} not found, generating minimal SI XML")
        root = ET.Element('tv')
        channel = ET.SubElement(root, 'channel', {'id': 'default'})
        ET.SubElement(channel, 'display-name').text = 'Default Channel'
        ET.SubElement(channel, 'display-name', {'lang': 'si'}).text = 'පෙරනිමි නාලිකාව'
        ET.ElementTree(root).write(args.output, encoding='utf-8', xml_declaration=True)
    else:
        success = process_xml(args.input, args.output, args.preserve_channels)
        debug_log(f"Process {'completed' if success else 'failed'}")
