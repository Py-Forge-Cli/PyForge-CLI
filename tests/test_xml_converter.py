"""Unit tests for XML converter functionality."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import xml.etree.ElementTree as ET

from pyforge_cli.converters.xml import XMLConverter


class TestXMLConverter:
    """Test suite for XML converter."""
    
    @pytest.fixture
    def converter(self):
        """Create an XML converter instance."""
        return XMLConverter()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_get_metadata_simple_xml(self, converter, temp_dir):
        """Test metadata extraction from simple XML file."""
        xml_file = temp_dir / 'simple.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <person>
        <name>John Doe</name>
        <age>30</age>
    </person>
    <person>
        <name>Jane Smith</name>
        <age>25</age>
    </person>
</root>'''
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        assert metadata['file_name'] == 'simple.xml'
        assert metadata['file_format'] == 'XML'
        assert metadata['file_extension'] == '.xml'
        assert metadata['file_size'] > 0
        assert 'root_element' in metadata
        assert 'total_elements' in metadata
        assert 'max_depth' in metadata
        assert 'namespaces' in metadata
        assert metadata['encoding'] == 'UTF-8'
        
    def test_get_metadata_with_namespaces(self, converter, temp_dir):
        """Test metadata extraction from XML with namespaces."""
        xml_file = temp_dir / 'namespaces.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:ns1="http://example.com/ns1" xmlns:ns2="http://example.com/ns2">
    <ns1:element1>Content1</ns1:element1>
    <ns2:element2>Content2</ns2:element2>
</root>'''
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        assert len(metadata['namespaces']) > 0
        assert 'http://example.com/ns1' in str(metadata['namespaces'])
        assert 'http://example.com/ns2' in str(metadata['namespaces'])
        
    def test_get_metadata_deep_nesting(self, converter, temp_dir):
        """Test metadata extraction from deeply nested XML."""
        xml_file = temp_dir / 'deep.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<level1>
    <level2>
        <level3>
            <level4>
                <level5>Deep content</level5>
            </level4>
        </level3>
    </level2>
</level1>'''
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        assert metadata['max_depth'] >= 5
        assert metadata['total_elements'] >= 5
        
    def test_get_metadata_with_attributes(self, converter, temp_dir):
        """Test metadata extraction from XML with attributes."""
        xml_file = temp_dir / 'attributes.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="1" category="fiction" available="true">
        <title lang="en">Book Title</title>
        <author nationality="US">Author Name</author>
    </book>
    <book id="2" category="non-fiction" available="false">
        <title lang="fr">Livre Titre</title>
        <author nationality="FR">Nom Auteur</author>
    </book>
</catalog>'''
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        assert metadata['total_elements'] >= 6  # catalog, 2 books, 2 titles, 2 authors
        
    def test_get_metadata_empty_xml(self, converter, temp_dir):
        """Test metadata extraction from empty XML file."""
        xml_file = temp_dir / 'empty.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root></root>'''
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        assert metadata['total_elements'] == 1  # Just the root element
        assert metadata['max_depth'] == 1
        
    def test_get_metadata_malformed_xml(self, converter, temp_dir):
        """Test metadata extraction from malformed XML file."""
        xml_file = temp_dir / 'malformed.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <unclosed>Content
    <another>More content</another>
</root>'''
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        # Should handle malformed XML gracefully
        assert metadata is None or isinstance(metadata, dict)
        
    def test_get_metadata_large_xml(self, converter, temp_dir):
        """Test metadata extraction from large XML file."""
        xml_file = temp_dir / 'large.xml'
        
        # Build a large XML document
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<data>']
        for i in range(1000):
            lines.append(f'    <record id="{i}"><value>Data {i}</value></record>')
        lines.append('</data>')
        
        xml_content = '\n'.join(lines)
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        assert metadata['total_elements'] >= 2000  # data + 1000 records + 1000 values
        assert metadata['file_size'] > 10000  # Should be substantial
        
    def test_get_metadata_different_encodings(self, converter, temp_dir):
        """Test metadata extraction from XML with different encodings."""
        xml_file = temp_dir / 'utf16.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-16"?>
<root>
    <text>Unicode content: ñáéíóú</text>
</root>'''
        xml_file.write_text(xml_content, encoding='utf-16')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        assert metadata['encoding'] == 'UTF-16'
        
    def test_get_metadata_corrupted_file(self, converter, temp_dir):
        """Test metadata extraction from corrupted XML file."""
        xml_file = temp_dir / 'corrupted.xml'
        xml_file.write_bytes(b'\x00\x01\x02\x03Invalid XML content')
        
        metadata = converter.get_metadata(xml_file)
        
        # Should return None for corrupted files
        assert metadata is None
        
    def test_get_metadata_nonexistent_file(self, converter):
        """Test metadata extraction from non-existent file."""
        from pathlib import Path
        
        nonexistent_file = Path('/nonexistent/file.xml')
        metadata = converter.get_metadata(nonexistent_file)
        
        # Should return None for non-existent files
        assert metadata is None
        
    def test_get_metadata_mixed_content(self, converter, temp_dir):
        """Test metadata extraction from XML with mixed content."""
        xml_file = temp_dir / 'mixed.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<document>
    <section>
        Text before element <emphasis>emphasized text</emphasis> text after element.
        <paragraph>
            Another paragraph with <link href="http://example.com">link</link> inside.
        </paragraph>
    </section>
</document>'''
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        assert metadata['total_elements'] >= 5  # document, section, emphasis, paragraph, link
        
    def test_get_metadata_processing_instructions(self, converter, temp_dir):
        """Test metadata extraction from XML with processing instructions."""
        xml_file = temp_dir / 'processing.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="style.xsl"?>
<!DOCTYPE root SYSTEM "example.dtd">
<root>
    <data>Content</data>
</root>'''
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        # Should handle processing instructions and DTD
        assert metadata['total_elements'] >= 2  # root, data
        
    def test_get_metadata_cdata_sections(self, converter, temp_dir):
        """Test metadata extraction from XML with CDATA sections."""
        xml_file = temp_dir / 'cdata.xml'
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <script><![CDATA[
        function test() {
            return "Hello <World>";
        }
    ]]></script>
    <description><![CDATA[This contains special chars: &<>"']]></description>
</root>'''
        xml_file.write_text(xml_content, encoding='utf-8')
        
        metadata = converter.get_metadata(xml_file)
        
        assert metadata is not None
        assert metadata['total_elements'] >= 3  # root, script, description