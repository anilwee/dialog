import xml.etree.ElementTree as ET
import requests
import os
from datetime import datetime
from urllib.parse import quote
import time

API_URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=si&dt=t&q="
REQUEST_DELAY = 0.5

def debug_log(message):
    print(f"[DEBUG] {datetime.now().isoformat()} - {message}")
    with open('translation_debug.log', 'a', encoding='utf-8') as log:
        log.write(f"{datetime.now().isoformat()} - {message}\n")

def translate_text(text):
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
        debug_log(f"Translation error for '{text}': {str(e)}")
        return text

def process_xml(input_path, output_path):
    try:
        debug_log(f"Starting processing {input_path}")
        tree = ET.parse(input_path)
        root = tree.getroot()
        translated_elements = 0
        
        # EXACT MATCHING OF TARGET ELEMENTS
        for element in root.findall('.//*[(self::title or self::desc) and @lang="si"]'):
            if element.text and element.text.strip():
                original = element.text
                element.text = translate_text(original)
                if element.text != original:
                    translated_elements += 1
                time.sleep(REQUEST_DELAY)
        
        debug_log(f"Translated {translated_elements} elements")
        
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
        'output': 'public/si.xml'
    }
    success = process_xml(CONFIG['input'], CONFIG['output'])
    debug_log(f"Process {'succeeded' if success else 'failed'}")
