#!/usr/bin/env python3
"""
Sri Lanka EPG Filter - Processes XMLTV files to extract Sri Lankan channels
"""

import xml.etree.ElementTree as ET
from defusedxml.ElementTree import parse
import os
import re
import logging
from datetime import datetime
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
        r"(?i)ada\s*derana(?: 24)?", 
        r"(?i)hiru\s*tv", 
        r"(?i)sirasa\s*tv", 
        r"(?i)swarnawahini(?: live)?",
        r"(?i)tv\s*derana", 
        r"(?i)itn", 
        r"(?i)rupavahini", 
        r"(?i)jaya\s*tv",
        
        # Entertainment
        r"(?i)art\s*television", 
        r"(?i)channel\s*c", 
        r"(?i)channel\s*one", 
        r"(?i)hi\s*tv",
        r"(?i)shakthi\s*tv", 
        r"(?i)tv1\s*sri\s*lanka", 
        r"(?i)vasantham\s*tv",
        
        # Religious
        r"(?i)buddhist\s*tv", 
        r"(?i)god\s*tv/swarga\s*tv", 
        r"(?i)shraddha\s*tv",
        
        # Sports
        r"(?i)thepapare\s*\d", 
        r"(?i)citi\s*hitz",
        
        # Regional
        r"(?i)damsathara\s*tv", 
        r"(?i)haritha\s*tv", 
        r"(?i)monara\s*tv", 
        r"(?i)nethra\s*tv",
        r"(?i)pragna\s*tv", 
        r"(?i)rangiri\s*sri\s*lanka", 
        r"(?i)ridee\s*tv", 
        r"(?i)supreme\s*tv",
        r"(?i)siyatha\s*tv", 
        r"(?i)tv\s*didula"
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
            
            # Write sanitized temporary file
            temp_file = f"{self.input_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return temp_file
        
        except Exception as e:
            logging.error(f"XML sanitization failed: {str(e)}")
            raise

    def _match_channel(self, channel_name):
        """Fuzzy match channel names with regex patterns"""
        try:
            if not channel_name:
                return False
            return any(re.search(pattern, channel_name) for pattern in self.CHANNELS)
        except Exception as e:
            logging.warning(f"Channel matching error: {str(e)}")
            return False

    def process(self):
        """Main processing method"""
        temp_file = None
        try:
            # Pre-process XML
            temp_file = self._sanitize_xml()
            
            # Parse XML with security protections
            tree = parse(temp_file)
            root = tree.getroot()
            
            # Prepare new XML structure
            ET.register_namespace('', self.namespace['ns'])
            new_root = ET.Element('tv', self.namespace)
            
            # Process channels
            for channel in root.findall('ns:channel', self.namespace):
                name_elem = channel.find('ns:display-name', self.namespace)
                if name_elem is not None:
                    logging.debug(f"Checking channel: {name_elem.text}")
                    if self._match_channel(name_elem.text):
                        new_root.append(channel)
                        self.channel_map[channel.attrib['id']] = name_elem.text
                        logging.info(f"Added channel: {name_elem.text}")
            
            # Process programs
            for program in root.findall('ns:programme', self.namespace):
                if program.attrib['channel'] in self.channel_map:
                    new_root.append(program)
                    self.program_count += 1
            
            # Write output
            tree = ET.ElementTree(new_root)
            tree.write(
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
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

def main():
    parser = argparse.ArgumentParser(
        description='Filter Sri Lankan channels from XMLTV EPG data'
    )
    parser.add_argument(
        '-i', '--input', 
        default='public/epg.xml',
        help='Input EPG XML file path'
    )
    parser.add_argument(
        '-o', '--output',
        default='public/lk.xml',
        help='Output filtered XML file path'
    )
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        logging.error(f"Input file not found: {args.input}")
        exit(1)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Run the filter
    epg_filter = EPGFilter(args.input, args.output)
    if not epg_filter.process():
        exit(1)

if __name__ == "__main__":
    main()
