#!/usr/bin/env python3
"""
Sri Lanka EPG Generator - Filters specific channels from EPG data
"""

import xml.etree.ElementTree as ET
import os
import re
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class EPGFilter:
    # Explicit list of Sri Lankan channels to include
    CHANNELS_TO_FILTER = [
        # News
        'Ada Derana', 'Ada Derana 24', 'Hiru TV', 'Sirasa TV', 'Swarnawahini',
        'TV Derana', 'ITN', 'Rupavahini', 'Jaya TV',
        
        # Entertainment
        'ART Television', 'Channel C', 'Channel One', 'Hi TV',
        'Shakthi TV', 'TV1 Sri Lanka', 'Vasantham TV',
        
        # Religious
        'Buddhist TV', 'God TV/Swarga TV', 'Shraddha TV',
        
        # Sports
        'ThePapare', 'Citi Hitz',
        
        # Regional
        'Damsathara TV', 'Haritha TV', 'Monara TV', 'Nethra TV',
        'Pragna TV', 'Rangiri Sri Lanka', 'Ridee TV', 'TV Supreme',
        'Siyatha TV', 'TV Didula'
    ]

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.matched_channels = set()
        self.program_count = 0

    def _is_wanted_channel(self, channel_name):
        """Check if channel is in our filter list (case-insensitive)"""
        return any(
            filter_channel.lower() in channel_name.lower()
            for filter_channel in self.CHANNELS_TO_FILTER
        )

    def process(self):
        try:
            # Log the channels we're looking for
            logging.info(f"Filtering for {len(self.CHANNELS_TO_FILTER)} Sri Lankan channels")
            
            # Parse the XML
            tree = ET.parse(self.input_file)
            root = tree.getroot()
            
            # Create new EPG structure
            new_root = ET.Element('tv')
            
            # Process channels
            for channel in root.findall('channel'):
                name_elem = channel.find('display-name')
                if name_elem is not None and self._is_wanted_channel(name_elem.text):
                    self.matched_channels.add(name_elem.text)
                    new_root.append(channel)
            
            # Process programmes
            channel_ids = {ch.attrib['id'] for ch in new_root.findall('channel')}
            for program in root.findall('programme'):
                if program.attrib['channel'] in channel_ids:
                    new_root.append(program)
                    self.program_count += 1
            
            # Write output
            ET.ElementTree(new_root).write(
                self.output_file,
                encoding='utf-8',
                xml_declaration=True
            )
            
            # Log results
            logging.info(f"Matched channels:\n- " + "\n- ".join(sorted(self.matched_channels)))
            logging.info(f"Generated {self.output_file} with {len(self.matched_channels)} channels and {self.program_count} programmes")
            return True
            
        except Exception as e:
            logging.error(f"Processing failed: {str(e)}", exc_info=True)
            return False

def main():
    parser = argparse.ArgumentParser(description='Generate Sri Lanka EPG')
    parser.add_argument('-i', '--input', default='public/epg.xml', help='Input EPG file')
    parser.add_argument('-o', '--output', default='public/lk.xml', help='Output file')
    args = parser.parse_args()
    
    # Verify paths
    if not os.path.exists(args.input):
        logging.error(f"Input file not found: {args.input}")
        return 1
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Process EPG
    logging.info(f"Starting EPG generation at {datetime.now()}")
    epg_filter = EPGFilter(args.input, args.output)
    
    if not epg_filter.process():
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
