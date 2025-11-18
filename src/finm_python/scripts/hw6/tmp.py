import xml.etree.ElementTree as ET

data_source = ET.parse("external_data_bloomberg.xml")
root = data_source.getroot()
print(root.tag)
print(root.find("symbol").tag)