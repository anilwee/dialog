import xml.etree.ElementTree as ET
import os
import json
import re
import shutil
from datetime import datetime

def load_lcn_mapping():
    """Load LCN to channel name mapping"""
    mapping_file = "dialog_lcn_map.json"
    
    if not os.path.exists(mapping_file):
        print(f"LCN mapping file '{mapping_file}' not found. Creating empty mapping.")
        # Create empty mapping
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}
    
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error reading {mapping_file}. Using empty mapping.")
        return {}

def load_logos():
    """Load available logos from logo folder and determine their LCN"""
    logo_folder = "logo"
    lcn_to_logo = {}
    
    if not os.path.exists(logo_folder):
        print(f"Logo folder '{logo_folder}' not found. Creating it...")
        os.makedirs(logo_folder)
        return lcn_to_logo
    
    # Scan logo folder for image files
    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    
    for filename in os.listdir(logo_folder):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in valid_extensions:
            # Try to extract LCN from filename (e.g., "53.png" or "53_icon.png")
            match = re.search(r'^(\d+)', filename)
            if match:
                lcn = int(match.group(1))
                lcn_to_logo[lcn] = os.path.join(logo_folder, filename)
                print(f"Found logo for LCN {lcn}: {filename}")
            else:
                print(f"Note: Could not extract LCN from filename (ignoring): {filename}")
    
    return lcn_to_logo

def organize_and_add_logos_to_epg(original_epg_path, output_epg_path, lcn_mapping, lcn_to_logo):
    """Organize EPG channels by LCN and add logo references"""
    
    if not os.path.exists(original_epg_path):
        print(f"Original EPG file not found at {original_epg_path}")
        return False
    
    try:
        # Parse original XML
        tree = ET.parse(original_epg_path)
        root = tree.getroot()
        
        # Find all channel elements
        channels = []
        for channel in root.findall('channel'):
            channel_id = channel.get('id', '')
            display_name_elem = channel.find('display-name')
            display_name = display_name_elem.text if display_name_elem is not None else ''
            
            channels.append({
                'element': channel,
                'id': channel_id,
                'display_name': display_name
            })
        
        # Create a new root with sorted channels
        new_root = ET.Element('tv')
        
        # Copy other elements (programmes, etc.) but we'll re-add sorted channels
        programmes = []
        for elem in root:
            if elem.tag == 'programme':
                programmes.append(elem)
            elif elem.tag != 'channel':
                new_root.append(elem)
        
        # Sort channels by LCN
        channels_with_lcn = []
        channels_without_lcn = []
        
        for channel in channels:
            display_name = channel['display_name']
            normalized_display = display_name.lower().strip()
            
            # Try to match with LCN mapping
            matched_lcn = None
            for lcn, name in lcn_mapping.items():
                # Convert both to strings for comparison
                name_lower = str(name).lower().strip()
                if name_lower in normalized_display or normalized_display in name_lower:
                    matched_lcn = int(lcn)
                    break
            
            if matched_lcn:
                channels_with_lcn.append((matched_lcn, channel))
            else:
                channels_without_lcn.append(channel)
        
        # Sort by LCN
        channels_with_lcn.sort(key=lambda x: x[0])
        
        # Add channels to new root
        logo_count = 0
        for lcn, channel in channels_with_lcn:
            # Add logo if available
            if lcn in lcn_to_logo:
                icon_path = lcn_to_logo[lcn]
                # Convert to relative path
                icon_url = f"logo/{os.path.basename(icon_path)}"
                
                # Check if icon already exists
                existing_icon = channel['element'].find('icon')
                if existing_icon is not None:
                    channel['element'].remove(existing_icon)
                
                icon_elem = ET.SubElement(channel['element'], 'icon')
                icon_elem.set('src', icon_url)
                print(f"Added logo for LCN {lcn}: {channel['display_name']}")
                logo_count += 1
            
            new_root.append(channel['element'])
        
        # Add unmatched channels at the end
        for channel in channels_without_lcn:
            new_root.append(channel['element'])
        
        # Add all programmes back
        for programme in programmes:
            new_root.append(programme)
        
        # Create new tree and save
        new_tree = ET.ElementTree(new_root)
        new_tree.write(output_epg_path, encoding='utf-8', xml_declaration=True)
        
        print(f"\n✅ Success! Processed {len(channels_with_lcn)} numbered channels")
        print(f"Added logos for {logo_count} channels")
        print(f"Unmatched channels: {len(channels_without_lcn)}")
        return True
        
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    original_epg = "open/epg.xml"
    output_epg = "open/epg_organized.xml"
    
    print("=" * 50)
    print("EPG Processor with Channel Logos")
    print("=" * 50)
    
    # Load LCN mapping
    print("\n1. Loading LCN mapping...")
    lcn_mapping = load_lcn_mapping()
    print(f"   Loaded {len(lcn_mapping)} LCN mappings")
    
    # Load available logos
    print("\n2. Scanning for logos...")
    lcn_to_logo = load_logos()
    print(f"   Found {len(lcn_to_logo)} logos")
    
    # Process EPG
    print("\n3. Processing EPG...")
    if organize_and_add_logos_to_epg(original_epg, output_epg, lcn_mapping, lcn_to_logo):
        # Replace original with organized version
        shutil.copy2(output_epg, original_epg)
        print(f"\n✅ Updated {original_epg} with organized channels and logos")
    else:
        print("\n❌ Failed to process EPG")
        return 1
    
    print("\n" + "=" * 50)
    print("Complete!")
    print("=" * 50)
    return 0

if __name__ == "__main__":
    exit(main())
