import yaml
import xml.etree.ElementTree as ET
from pathlib import Path

# Load mappings from root folder
mapping = yaml.safe_load(Path('translation_mappings.yml').read_text(encoding='utf-8'))

# Parse source XML
tree = ET.parse('public/lk.xml')
root = tree.getroot()

# We need to find the parent for each node to append a sibling.
# xml.etree.ElementTree does not have getparent(), so we find parents manually.

def find_parent(root, child):
    for parent in root.iter():
        for c in parent:
            if c is child:
                return parent
    return None

for node in root.findall('.//title') + root.findall('.//desc'):
    if node.get('lang') == 'en':
        orig = node.text.strip()
        sinh = mapping.get(orig)
        if sinh:
            new_node = ET.Element(node.tag, {'lang': 'si'})
            new_node.text = sinh
            parent = find_parent(root, node)
            if parent is not None:
                # Insert new_node after the current node
                index = list(parent).index(node)
                parent.insert(index + 1, new_node)

# Save result
tree.write('public/si.xml', encoding='utf-8', xml_declaration=True)
