import yaml
import xml.etree.ElementTree as ET
from pathlib import Path

# Load mappings
mapping = yaml.safe_load(Path('public/translation_mappings.yml').read_text())

# Parse source XML
tree = ET.parse('public/lk.xml')
root = tree.getroot()

for node in root.findall('.//title') + root.findall('.//desc'):
    if node.get('lang') == 'en':
        orig = node.text.strip()
        sinh = mapping.get(orig)
        if sinh:
            new = ET.Element(node.tag, {'lang':'si'})
            new.text = sinh
            node.getparent().append(new)

# Save result
tree.write('public/si.xml', encoding='utf-8', xml_declaration=True)
