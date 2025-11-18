import xml.etree.ElementTree as ET

# 1. Parsing XML from a string
xml_string = """
<root>
    <item id="1">First Item</item>
    <item id="2">Second Item</item>
</root>
"""
root = ET.fromstring(xml_string)
print(root)

# 2. Accessing elements and attributes
print(f"Root tag: {root.tag}")
for item in root.findall('item'):
    print(f"Item ID: {item.get('id')}, Text: {item.text}")

# 3. Modifying an element
new_item = ET.SubElement(root, 'item', id="3")
new_item.text = "Third Item"

# 4. Writing the modified XML to a file
tree = ET.ElementTree(root)
tree.write("output.xml", encoding="utf-8", xml_declaration=True)