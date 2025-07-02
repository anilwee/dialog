#!/usr/bin/env python3
"""
Sri Lanka EPG Generator - Filters specific channels from EPG data,
with a special exception to skip any <channel> or <programme> related to &flix if it appears in invalid XML form.
"""

import xml.etree.ElementTree as ET
import os
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def remove_andflix(input_file, cleaned_file):
    """Remove lines with unescaped &flix from the raw XML file."""
    with open(input_file, 'r', encoding='utf-8') as infile, open(cleaned_file, 'w', encoding='utf-8') as outfile:
        skip = False
        for line in infile:
            # Check for the start of a channel/programme block with &flix
            if '<channel id="&flix"' in line or '<programme' in line and 'channel="&flix"' in line:
                skip = True
            # Check for the end of the block (for pretty-printed XML)
            if skip and ('</channel>' in line or '</programme>' in line):
                skip = False
                continue  # skip this closing tag too
            if skip:
                continue
            # Otherwise, write the line
            outfile.write(line)

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
            filter_channel.lower() in (channel_name or "").lower()
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

    cleaned_xml = args.input.replace('.xml', '_cleaned.xml')

    # Remove lines containing &flix before processing (so XML parsing doesn't fail)
    remove_andflix(args.input, cleaned_xml)

    # Verify paths
    if not os.path.exists(cleaned_xml):
        logging.error(f"Cleaned input file not found: {cleaned_xml}")
        return 1

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Process EPG
    logging.info(f"Starting EPG generation at {datetime.now()}")
    epg_filter = EPGFilter(cleaned_xml, args.output)

    if not epg_filter.process():
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
