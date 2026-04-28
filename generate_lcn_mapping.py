import requests
import json
import re
from bs4 import BeautifulSoup

def generate_lcn_mapping():
    url = "https://www.lyngsat.com/packages/Dialog-TV_lcn.html"
    output_file = "dialog_lcn_map.json"
    
    print("Fetching LCN mapping from LyngSat...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main table - look for tables with LCN in first column
        lcn_to_name = {}
        
        # Method 1: Look for standard table rows
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                # First cell might be LCN
                first_cell = cells[0].get_text(strip=True)
                if first_cell.isdigit():
                    lcn = int(first_cell)
                    # Second cell is channel name
                    name = cells[1].get_text(strip=True)
                    # Clean up name - remove extra info
                    name = re.sub(r'\s+', ' ', name).strip()
                    if name and not name.startswith('['):
                        lcn_to_name[lcn] = name
        
        # Save mapping
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(lcn_to_name, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved {len(lcn_to_name)} LCN mappings to {output_file}")
        return lcn_to_name
        
    except Exception as e:
        print(f"Error fetching LCN mapping: {e}")
        # Return empty dict if fails
        return {}

if __name__ == "__main__":
    generate_lcn_mapping()
