#!/usr/bin/env python
"""
Generate XML test files with various edge cases for comprehensive testing.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import gzip
import bz2
import json
from pathlib import Path
import random
import string


class XMLTestGenerator:
    """Generate various XML test files."""
    
    @staticmethod
    def prettify_xml(elem):
        """Return a pretty-printed XML string."""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    @staticmethod
    def generate_simple_xml():
        """Generate a simple, well-formed XML."""
        root = ET.Element('catalog')
        
        for i in range(1, 4):
            book = ET.SubElement(root, 'book', id=str(i))
            ET.SubElement(book, 'title').text = f'Book Title {i}'
            ET.SubElement(book, 'author').text = f'Author {i}'
            ET.SubElement(book, 'price').text = str(10.99 + i)
            ET.SubElement(book, 'publish_date').text = f'2023-0{i}-01'
        
        return XMLTestGenerator.prettify_xml(root)
    
    @staticmethod
    def generate_nested_xml():
        """Generate deeply nested XML structure."""
        root = ET.Element('company')
        
        # Create departments
        for dept_id in range(1, 4):
            dept = ET.SubElement(root, 'department', id=f'dept_{dept_id}')
            ET.SubElement(dept, 'name').text = f'Department {dept_id}'
            
            # Create teams within departments
            for team_id in range(1, 3):
                team = ET.SubElement(dept, 'team', id=f'team_{dept_id}_{team_id}')
                ET.SubElement(team, 'name').text = f'Team {team_id}'
                
                # Create employees within teams
                for emp_id in range(1, 4):
                    emp = ET.SubElement(team, 'employee', id=f'emp_{dept_id}_{team_id}_{emp_id}')
                    ET.SubElement(emp, 'name').text = f'Employee {emp_id}'
                    ET.SubElement(emp, 'role').text = random.choice(['Developer', 'Manager', 'Analyst'])
                    
                    # Add skills
                    skills = ET.SubElement(emp, 'skills')
                    for skill in ['Python', 'SQL', 'XML']:
                        ET.SubElement(skills, 'skill').text = skill
        
        return XMLTestGenerator.prettify_xml(root)
    
    @staticmethod
    def generate_attributes_heavy_xml():
        """Generate XML with many attributes."""
        root = ET.Element('products')
        
        for i in range(1, 6):
            product = ET.SubElement(root, 'product',
                id=f'prod_{i:03d}',
                name=f'Product {i}',
                category=random.choice(['Electronics', 'Clothing', 'Food']),
                price=str(random.uniform(10, 1000)),
                currency='USD',
                in_stock=str(random.choice(['true', 'false'])),
                weight=str(random.uniform(0.1, 50)),
                dimensions=f'{random.randint(1,100)}x{random.randint(1,100)}x{random.randint(1,100)}',
                manufacturer=f'Company {random.choice(["A", "B", "C"])}',
                sku=f'SKU-{i:05d}',
                barcode=''.join(random.choices(string.digits, k=13))
            )
            # Minimal element content
            ET.SubElement(product, 'description').text = f'Description for product {i}'
        
        return XMLTestGenerator.prettify_xml(root)
    
    @staticmethod
    def generate_mixed_content_xml():
        """Generate XML with mixed content (text and elements)."""
        root = ET.Element('article')
        
        title = ET.SubElement(root, 'title')
        title.text = 'Understanding XML Processing'
        
        content = ET.SubElement(root, 'content')
        content.text = 'XML processing involves '
        
        bold = ET.SubElement(content, 'bold')
        bold.text = 'parsing'
        bold.tail = ' and '
        
        italic = ET.SubElement(content, 'italic')
        italic.text = 'transforming'
        italic.tail = ' structured data. '
        
        link = ET.SubElement(content, 'link', href='https://example.com')
        link.text = 'Learn more'
        link.tail = ' about XML.'
        
        return XMLTestGenerator.prettify_xml(root)
    
    @staticmethod
    def generate_namespace_xml():
        """Generate XML with multiple namespaces."""
        # Register namespaces
        ns = {
            'catalog': 'http://example.com/catalog',
            'book': 'http://example.com/book',
            'meta': 'http://example.com/metadata'
        }
        
        for prefix, uri in ns.items():
            ET.register_namespace(prefix, uri)
        
        root = ET.Element('{http://example.com/catalog}catalog')
        
        for i in range(1, 3):
            book_elem = ET.SubElement(root, '{http://example.com/book}book')
            book_elem.set('{http://example.com/book}id', str(i))
            
            ET.SubElement(book_elem, '{http://example.com/book}title').text = f'Book {i}'
            ET.SubElement(book_elem, '{http://example.com/book}author').text = f'Author {i}'
            
            meta = ET.SubElement(book_elem, '{http://example.com/metadata}metadata')
            ET.SubElement(meta, '{http://example.com/metadata}isbn').text = f'978-0-{i:03d}-12345-6'
            ET.SubElement(meta, '{http://example.com/metadata}language').text = 'en'
        
        return XMLTestGenerator.prettify_xml(root)
    
    @staticmethod
    def generate_empty_elements_xml():
        """Generate XML with various empty elements."""
        root = ET.Element('data')
        
        # Different types of empty elements
        ET.SubElement(root, 'empty1')  # No content
        ET.SubElement(root, 'empty2').text = ''  # Empty string
        ET.SubElement(root, 'empty3').text = None  # None
        
        # Empty with attributes
        ET.SubElement(root, 'empty4', attr='value')
        
        # Self-closing vs explicit closing
        container = ET.SubElement(root, 'container')
        ET.SubElement(container, 'self_closing')
        explicit = ET.SubElement(container, 'explicit_closing')
        explicit.text = ''
        
        return XMLTestGenerator.prettify_xml(root)
    
    @staticmethod
    def generate_special_characters_xml():
        """Generate XML with special characters and CDATA."""
        root = ET.Element('special_chars')
        
        # Regular special characters (will be escaped)
        ET.SubElement(root, 'escaped').text = 'Special chars: < > & " \' © ™'
        
        # Unicode characters
        ET.SubElement(root, 'unicode').text = 'Hello 世界 Привет مرحبا שלום'
        
        # Whitespace variations
        ET.SubElement(root, 'whitespace').text = 'Line1\nLine2\tTabbed\r\nCRLF'
        
        # Mathematical symbols
        ET.SubElement(root, 'math').text = '∑ ∏ ∫ ∂ ∇ ∈ ∉ ∞ π'
        
        # Emoji
        ET.SubElement(root, 'emoji').text = '😀 🚀 🌟 ❤️ 🔥'
        
        # Note: CDATA requires special handling
        cdata_elem = ET.SubElement(root, 'cdata_content')
        cdata_elem.text = '<![CDATA[This contains <unescaped> XML & special chars]]>'
        
        return XMLTestGenerator.prettify_xml(root)
    
    @staticmethod
    def generate_large_xml():
        """Generate a large XML file."""
        root = ET.Element('large_dataset')
        
        # Generate 1000 records
        for i in range(1, 1001):
            record = ET.SubElement(root, 'record', id=str(i))
            ET.SubElement(record, 'timestamp').text = f'2023-01-01T{i%24:02d}:{i%60:02d}:00'
            ET.SubElement(record, 'value').text = str(random.uniform(0, 1000))
            ET.SubElement(record, 'status').text = random.choice(['active', 'inactive', 'pending'])
            ET.SubElement(record, 'category').text = f'CAT_{i%10:02d}'
            
            # Add some nested data
            details = ET.SubElement(record, 'details')
            for j in range(3):
                ET.SubElement(details, 'item', seq=str(j)).text = f'Detail {j} for record {i}'
        
        return ET.tostring(root, encoding='unicode')  # Skip prettify for performance
    
    @staticmethod
    def generate_array_like_xml():
        """Generate XML that represents array/list structures."""
        root = ET.Element('data')
        
        # Simple array
        simple_array = ET.SubElement(root, 'simple_array')
        for i in range(5):
            ET.SubElement(simple_array, 'item').text = str(i)
        
        # Array with attributes
        attr_array = ET.SubElement(root, 'attributed_array')
        for i in range(5):
            ET.SubElement(attr_array, 'item', index=str(i), type='number').text = str(i * 10)
        
        # Nested arrays
        matrix = ET.SubElement(root, 'matrix')
        for i in range(3):
            row = ET.SubElement(matrix, 'row', index=str(i))
            for j in range(3):
                ET.SubElement(row, 'col', index=str(j)).text = str(i * 3 + j)
        
        # Mixed array types
        mixed = ET.SubElement(root, 'mixed_array')
        ET.SubElement(mixed, 'item', type='string').text = 'Hello'
        ET.SubElement(mixed, 'item', type='number').text = '42'
        ET.SubElement(mixed, 'item', type='boolean').text = 'true'
        ET.SubElement(mixed, 'item', type='null')
        
        return XMLTestGenerator.prettify_xml(root)
    
    @staticmethod
    def generate_malformed_xml():
        """Generate intentionally malformed XML for error testing."""
        malformed_examples = [
            # Missing closing tag
            '<?xml version="1.0"?><root><item>Content</root>',
            
            # Mismatched tags
            '<?xml version="1.0"?><root><item>Content</items></root>',
            
            # Invalid characters in tag name
            '<?xml version="1.0"?><root><123invalid>Content</123invalid></root>',
            
            # Unescaped special characters
            '<?xml version="1.0"?><root><item>Price < 100 & > 50</item></root>',
            
            # Multiple root elements
            '<?xml version="1.0"?><root1>Content1</root1><root2>Content2</root2>',
            
            # Invalid attribute syntax
            '<?xml version="1.0"?><root attr=value>Content</root>',
        ]
        
        return malformed_examples
    
    @staticmethod
    def generate_dtd_xml():
        """Generate XML with DTD declaration."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE catalog [
  <!ELEMENT catalog (book+)>
  <!ELEMENT book (title, author, price)>
  <!ATTLIST book id CDATA #REQUIRED>
  <!ELEMENT title (#PCDATA)>
  <!ELEMENT author (#PCDATA)>
  <!ELEMENT price (#PCDATA)>
]>
<catalog>
  <book id="1">
    <title>XML Processing</title>
    <author>John Doe</author>
    <price>29.99</price>
  </book>
</catalog>'''
        return xml_content
    
    @staticmethod
    def generate_processing_instructions_xml():
        """Generate XML with processing instructions."""
        # Create XML with processing instructions
        pi_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="transform.xsl"?>
<?custom-processor param1="value1" param2="value2"?>
<root>
  <?target instruction="do something"?>
  <data>Content</data>
  <?another-pi?>
</root>'''
        return pi_xml


def save_xml_test_files():
    """Save all XML test files."""
    output_dir = Path(__file__).parent.parent / 'data' / 'xml'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Regular XML files
    test_cases = [
        ('simple.xml', XMLTestGenerator.generate_simple_xml()),
        ('nested_deep.xml', XMLTestGenerator.generate_nested_xml()),
        ('attributes_heavy.xml', XMLTestGenerator.generate_attributes_heavy_xml()),
        ('mixed_content.xml', XMLTestGenerator.generate_mixed_content_xml()),
        ('namespaces.xml', XMLTestGenerator.generate_namespace_xml()),
        ('empty_elements.xml', XMLTestGenerator.generate_empty_elements_xml()),
        ('special_characters.xml', XMLTestGenerator.generate_special_characters_xml()),
        ('large_dataset.xml', XMLTestGenerator.generate_large_xml()),
        ('array_structures.xml', XMLTestGenerator.generate_array_like_xml()),
        ('with_dtd.xml', XMLTestGenerator.generate_dtd_xml()),
        ('processing_instructions.xml', XMLTestGenerator.generate_processing_instructions_xml()),
    ]
    
    for filename, content in test_cases:
        filepath = output_dir / filename
        filepath.write_text(content, encoding='utf-8')
        print(f"Created: {filepath}")
    
    # Compressed XML files
    compressed_content = XMLTestGenerator.generate_large_xml()
    
    # GZIP compressed
    gz_path = output_dir / 'compressed.xml.gz'
    with gzip.open(gz_path, 'wt', encoding='utf-8') as f:
        f.write(compressed_content)
    print(f"Created: {gz_path}")
    
    # BZ2 compressed
    bz2_path = output_dir / 'compressed.xml.bz2'
    with bz2.open(bz2_path, 'wt', encoding='utf-8') as f:
        f.write(compressed_content)
    print(f"Created: {bz2_path}")
    
    # Malformed XML files
    malformed_dir = output_dir / 'malformed'
    malformed_dir.mkdir(exist_ok=True)
    
    for i, content in enumerate(XMLTestGenerator.generate_malformed_xml(), 1):
        filepath = malformed_dir / f'malformed_{i}.xml'
        filepath.write_text(content, encoding='utf-8')
        print(f"Created: {filepath}")
    
    # Empty file
    empty_path = output_dir / 'empty.xml'
    empty_path.write_text('', encoding='utf-8')
    print(f"Created: {empty_path}")
    
    # Binary file with .xml extension
    binary_path = output_dir / 'binary_file.xml'
    binary_path.write_bytes(b'\x00\x01\x02\x03\x04\x05')
    print(f"Created: {binary_path}")
    
    print(f"\nGenerated {len(test_cases) + 9} XML test files in {output_dir}")


def generate_xml_schema_files():
    """Generate XSD schema files for testing."""
    output_dir = Path(__file__).parent.parent / 'data' / 'xml' / 'schemas'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Simple schema
    simple_xsd = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="catalog">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="book" maxOccurs="unbounded">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="title" type="xs:string"/>
              <xs:element name="author" type="xs:string"/>
              <xs:element name="price" type="xs:decimal"/>
              <xs:element name="publish_date" type="xs:date"/>
            </xs:sequence>
            <xs:attribute name="id" type="xs:string" use="required"/>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>'''
    
    schema_path = output_dir / 'catalog.xsd'
    schema_path.write_text(simple_xsd, encoding='utf-8')
    print(f"Created: {schema_path}")


if __name__ == '__main__':
    save_xml_test_files()
    generate_xml_schema_files()