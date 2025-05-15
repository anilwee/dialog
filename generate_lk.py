#!/usr/bin/env python3
"""
Sri Lanka EPG Filter - Processes XMLTV files to extract Sri Lankan channels
"""

import xml.etree.ElementTree as ET
from defusedxml.ElementTree import parse
import os
import re
import logging
import argparse
import requests  # Added for remote file download

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('epg_filter.log'),
        logging.StreamHandler()
    ]
)

class EPGFilter:
    """Handles filtering of EPG XML data for Sri Lankan channels"""
    
    CHANNELS = [
        # News
        r"(?i)ada\s*derana(?: 24)?", 
        r"(?i)hiru\s*tv", 
        # ... (keep your existing channel patterns)
    ]

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.namespace = {'ns': 'urn:oasis:names:tc:tv:electronic:programming-guide:1.0'}
        self.channel_map = {}
        self.program_count = 0

    # ... (keep all your existing methods)

def download_file(url, local_path):
    """Download file from URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        logging.error(f"Download failed: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Filter Sri Lankan channels from XMLTV EPG data'
    )
    parser.add_argument(
        '-i', '--input', 
        default='https://raw.githubusercontent.com/anilwee/dialog/main/public/epg.xml',
        help='Input EPG XML URL or path'
    )
    parser.add_argument(
        '-o', '--output',
        default='public/lk.xml',
        help='Output filtered XML file path'
    )
    args = parser.parse_args()
    
    # Determine if input is URL or local path
    local_input = 'temp_epg.xml' if args.input.startswith('http') else args.input
    
    # Download if URL
    if args.input.startswith('http'):
        if not download_file(args.input, local_input):
            exit(1)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Run the filter
    epg_filter = EPGFilter(local_input, args.output)
    if not epg_filter.process():
        exit(1)
    
    # Cleanup
    if args.input.startswith('http') and os.path.exists(local_input):
        os.remove(local_input)

if __name__ == "__main__":
    main()
