import xml.etree.ElementTree as ET
import os
import json
import re
from datetime import datetime

def load_lcn_mapping():
    """Load LCN to channel name mapping"""
    try:
        with open("dialog_lcn_map.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("LCN mapping file not found. Run generate_lcn_mapping.py first.")
        return {}
    except json.JSONDecodeError:
        print("Error reading LCN mapping file.")
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
                print(f"Warning: Could not extract LCN from filename: {filename}")
    
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
        
        # Match channels to LCN using display_name
        # Create reverse mapping from channel name to LCN
        name_to_lcn = {}
        for lcn, name in lcn_mapping.items():
            # Normalize names for matching
            normalized_name = name.lower().strip()
            name_to_lcn[normalized_name] = lcn
        
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
                if name.lower() in normalized_display or normalized_display in name.lower():
                    matched_lcn = lcn
                    break
            
            if matched_lcn:
                channels_with_lcn.append((matched_lcn, channel))
            else:
                channels_without_lcn.append(channel)
        
        # Sort by LCN
        channels_with_lcn.sort(key=lambda x: x[0])
        
        # Add channels to new root
        for lcn, channel in channels_with_lcn:
            # Add logo if available
            if lcn in lcn_to_logo:
                icon_path = lcn_to_logo[lcn]
                # Convert to relative path or URL
                icon_url = f"logo/{os.path.basename(icon_path)}"
                icon_elem = ET.SubElement(channel['element'], 'icon')
                icon_elem.set('src', icon_url)
                print(f"Added logo for LCN {lcn}: {channel['display_name']}")
            
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
        
        print(f"Successfully organized EPG with {len(channels_with_lcn)} numbered channels")
        print(f"Added logos for {len([l for l in channels_with_lcn if l[0] in lcn_to_logo])} channels")
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
    
    # Load LCN mapping
    print("Loading LCN mapping...")
    lcn_mapping = load_lcn_mapping()
    print(f"Loaded {len(lcn_mapping)} LCN mappings")
    
    # Load available logos
    print("\nScanning for logos...")
    lcn_to_logo = load_logos()
    print(f"Found {len(lcn_to_logo)} logos")
    
    # Process EPG
    print("\nProcessing EPG...")
    if organize_and_add_logos_to_epg(original_epg, output_epg, lcn_mapping, lcn_to_logo):
        print(f"\n✅ Success! Organized EPG saved to: {output_epg}")
        
        # Replace original with organized version
        import shutil
        shutil.copy2(output_epg, original_epg)
        print("Updated original epg.xml with organized version")
    else:
        print("Failed to process EPG")

if __name__ == "__main__":
    main()
