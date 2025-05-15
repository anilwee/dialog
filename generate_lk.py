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
        r"ADA DERANA(?: 24)?", r"Hiru TV", r"Sirasa TV", r"Swarnawahini(?: Live)?",
        r"TV Derana", r"ITN", r"Rupavahini", r"Jaya TV",

        # Entertainment
        r"ART Television", r"Channel C", r"Channel One", r"Hi TV",
        r"Shakthi TV", r"TV1 Sri Lanka", r"Vasantham TV",

        # Religious
        r"Buddhist TV", r"God TV/Swarga TV", r"Shraddha TV",

        # Sports
        r"ThePapare \d", r"Citi Hitz",

        # Regional
        r"Damsathara TV", r"Haritha TV", r"Monara TV", r"Nethra TV",
        r"Pragna TV", r"Rangiri Sri Lanka", r"Ridee TV", r"Supreme TV",
        r"Siyatha TV", r"TV Didula"
    ]

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.namespace = {'ns': 'urn:oasis:names:tc:tv:electronic:programming-guide:1.0'}
        self.channel_map = {}
        self.program_count = 0

    def _sanitize_xml(self):
        """Pre-process XML to fix common issues"""
        try:
            with open(self.input_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Fix common XML issues
            content = re.sub(r'&(?!(amp|lt|gt|quot|apos);)', '&amp;', content)
            content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', content)

            temp_file = f"{self.input_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return temp_file

        except Exception as e:
            logging.error(f"XML sanitization failed: {str(e)}")
            raise

    def _match_channel(self, channel_name):
        """Fuzzy match channel names with regex patterns"""
        if not channel_name:
            return False
        return any(re.search(pattern, channel_name, re.IGNORECASE)
                   for pattern in self.CHANNELS)

    def process(self):
        """Main processing method"""
        temp_file = None
        try:
            temp_file = self._sanitize_xml()

            tree = parse(temp_file)
            root = tree.getroot()

            ET.register_namespace('', self.namespace['ns'])
            new_root = ET.Element('tv', self.namespace)

            for channel in root.findall('ns:channel', self.namespace):
                name_elem = channel.find('ns:display-name', self.namespace)
                if name_elem is not None and self._match_channel(name_elem.text):
                    new_root.append(channel)
                    self.channel_map[channel.attrib['id']] = name_elem.text
                    logging.info(f"Added channel: {name_elem.text}")

            for program in root.findall('ns:programme', self.namespace):
                if program.attrib['channel'] in self.channel_map:
                    new_root.append(program)
                    self.program_count += 1

            ET.ElementTree(new_root).write(
                self.output_file,
                encoding='utf-8',
                xml_declaration=True,
                short_empty_elements=False
            )

            logging.info(
                f"Successfully created {self.output_file}\n"
                f"Channels: {len(self.channel_map)}\n"
                f"Programs: {self.program_count}"
            )
            return True

        except ET.ParseError as e:
            logging.error(f"XML parsing error: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}", exc_info=True)
            return False
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

def main():
    parser = argparse.ArgumentParser(description='Filter Sri Lankan channels from XMLTV EPG data')
    parser.add_argument('-i', '--input', default='public/epg.xml', help='Input EPG XML file path')
    parser.add_argument('-o', '--output', default='public/lk.xml', help='Output filtered XML file path')
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    epg_filter = EPGFilter(args.input, args.output)
    if not epg_filter.process():
        exit(1)

if __name__ == "__main__":
    main()
