import requests
import json
import re
import os
from bs4 import BeautifulSoup

def generate_lcn_mapping():
    url = "https://www.lyngsat.com/packages/Dialog-TV_lcn.html"
    output_file = "dialog_lcn_map.json"
    
    print("Fetching LCN mapping from LyngSat...")
    
    # Create default empty mapping
    lcn_to_name = {}
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for table rows with LCN
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                first_cell = cells[0].get_text(strip=True)
                if first_cell.isdigit():
                    lcn = int(first_cell)
                    name = cells[1].get_text(strip=True)
                    name = re.sub(r'\s+', ' ', name).strip()
                    # Skip test cards or empty names
                    if name and not name.startswith('[') and name != '':
                        lcn_to_name[lcn] = name
        
        # Save mapping even if empty
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(lcn_to_name, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved {len(lcn_to_name)} LCN mappings to {output_file}")
        
    except Exception as e:
        print(f"Warning: Could not fetch LCN mapping from LyngSat: {e}")
        # Create empty mapping file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"Created empty mapping file: {output_file}")
    
    return lcn_to_name

if __name__ == "__main__":
    generate_lcn_mapping()
