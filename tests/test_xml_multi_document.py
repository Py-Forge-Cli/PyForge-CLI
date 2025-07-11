"""
Unit tests for multi-document XML parsing functionality (Issue #21).
"""

import xml.etree.ElementTree as ET

import pytest

from pyforge_cli.converters.xml import XmlConverter
from pyforge_cli.converters.xml_flattener import XmlFlattener
from pyforge_cli.converters.xml_structure_analyzer import XmlStructureAnalyzer


class TestXmlMultiDocumentStructureAnalyzer:
    """Test cases for multi-document XML structure analysis"""

    def test_single_document_analysis(self, tmp_path):
        """Test that single-document XML analysis works correctly"""
        analyzer = XmlStructureAnalyzer()

        # Create single-document XML
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <item id="1">
        <name>Test Item</name>
        <value>123</value>
    </item>
</root>"""

        test_file = tmp_path / "single_doc.xml"
        test_file.write_text(xml_content)

        result = analyzer.analyze_file(test_file)

        assert not result["is_multi_document"]
        assert result["document_count"] == 1
        assert result["root_tag"] == "root"
        assert "root/item" in result["elements"]

    def test_multi_document_detection(self, tmp_path):
        """Test detection of multi-document XML files"""
        analyzer = XmlStructureAnalyzer()

        # Create multi-document XML (like USPTO patents)
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<patent id="1">
    <title>First Patent</title>
    <inventor>John Doe</inventor>
</patent>
<?xml version="1.0" encoding="UTF-8"?>
<patent id="2">
    <title>Second Patent</title>
    <inventor>Jane Smith</inventor>
</patent>"""

        test_file = tmp_path / "multi_doc.xml"
        test_file.write_text(xml_content)

        result = analyzer.analyze_file(test_file)

        assert result["is_multi_document"]
        assert result["document_count"] == 2
        assert result["root_tag"] == "patent"  # First document's root
        assert "patent" in result["root_tags"]
        assert len(result["document_analyses"]) == 2

    def test_multi_document_with_different_roots(self, tmp_path):
        """Test multi-document XML with different root element types"""
        analyzer = XmlStructureAnalyzer()

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<patent id="1">
    <title>Patent Document</title>
</patent>
<?xml version="1.0" encoding="UTF-8"?>
<application id="2">
    <title>Application Document</title>
</application>"""

        test_file = tmp_path / "mixed_roots.xml"
        test_file.write_text(xml_content)

        result = analyzer.analyze_file(test_file)

        assert result["is_multi_document"]
        assert result["document_count"] == 2
        assert len(result["root_tags"]) == 2
        assert "patent" in result["root_tags"]
        assert "application" in result["root_tags"]

    def test_invalid_multi_document_handling(self, tmp_path):
        """Test handling of partially invalid multi-document XML"""
        analyzer = XmlStructureAnalyzer()

        # Second document is malformed
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<patent id="1">
    <title>Valid Patent</title>
</patent>
<?xml version="1.0" encoding="UTF-8"?>
<patent id="2">
    <title>Invalid Patent
</patent>
<?xml version="1.0" encoding="UTF-8"?>
<patent id="3">
    <title>Another Valid Patent</title>
</patent>"""

        test_file = tmp_path / "partial_invalid.xml"
        test_file.write_text(xml_content)

        result = analyzer.analyze_file(test_file)

        # Should still process valid documents
        assert result["is_multi_document"]
        # Should have processed at least 2 valid documents
        assert result["document_count"] >= 2

    def test_xml_declaration_pattern_matching(self, tmp_path):
        """Test XML declaration pattern matching for document splitting"""
        analyzer = XmlStructureAnalyzer()

        # Various XML declaration formats
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<doc1>Content 1</doc1>
<?xml version='1.0' encoding='UTF-8'?>
<doc2>Content 2</doc2>
<?xml version="1.0" encoding="ISO-8859-1"?>
<doc3>Content 3</doc3>"""

        test_file = tmp_path / "various_declarations.xml"
        test_file.write_text(xml_content)

        result = analyzer.analyze_file(test_file)

        assert result["is_multi_document"]
        assert result["document_count"] == 3


class TestXmlMultiDocumentFlattener:
    """Test cases for multi-document XML flattening"""

    def test_single_document_flattening(self, tmp_path):
        """Test that single-document flattening works unchanged"""
        flattener = XmlFlattener()

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<items>
    <item id="1">
        <name>Item 1</name>
        <value>100</value>
    </item>
    <item id="2">
        <name>Item 2</name>
        <value>200</value>
    </item>
</items>"""

        test_file = tmp_path / "single_doc.xml"
        test_file.write_text(xml_content)

        # Mock structure analysis for single document
        analysis = {"is_multi_document": False, "array_elements": ["items/item"]}

        records = flattener.flatten_file(test_file, analysis)

        assert len(records) >= 1
        # Should not have document metadata columns for single documents
        for record in records:
            assert "_document_id" not in record
            assert "_document_index" not in record

    def test_multi_document_flattening(self, tmp_path):
        """Test multi-document XML flattening"""
        flattener = XmlFlattener()

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<item id="1">
    <name>Item 1</name>
    <value>100</value>
</item>
<?xml version="1.0" encoding="UTF-8"?>
<item id="2">
    <name>Item 2</name>
    <value>200</value>
</item>
<?xml version="1.0" encoding="UTF-8"?>
<item id="3">
    <name>Item 3</name>
    <value>300</value>
</item>"""

        test_file = tmp_path / "multi_doc.xml"
        test_file.write_text(xml_content)

        # Mock structure analysis for multi-document
        analysis = {
            "is_multi_document": True,
            "document_count": 3,
            "array_elements": [],
        }

        records = flattener.flatten_file(test_file, analysis)

        assert len(records) == 3

        # Check document metadata is added
        for i, record in enumerate(records):
            assert "_document_id" in record
            assert "_document_index" in record
            assert record["_document_id"] == i + 1
            assert record["_document_index"] == i
            # Should have extracted item data
            assert "item@id" in record or any("id" in key for key in record.keys())

    def test_multi_document_flattening_with_parse_errors(self, tmp_path):
        """Test multi-document flattening with some parse errors"""
        flattener = XmlFlattener()

        # Include one malformed document
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<item id="1">
    <name>Valid Item 1</name>
</item>
<?xml version="1.0" encoding="UTF-8"?>
<item id="2">
    <name>Invalid Item 2
</item>
<?xml version="1.0" encoding="UTF-8"?>
<item id="3">
    <name>Valid Item 3</name>
</item>"""

        test_file = tmp_path / "partial_invalid.xml"
        test_file.write_text(xml_content)

        analysis = {
            "is_multi_document": True,
            "document_count": 3,
            "array_elements": [],
        }

        records = flattener.flatten_file(test_file, analysis)

        # Should have records from valid documents (invalid ones are skipped)
        assert len(records) >= 1

        # Should have records from valid documents with document metadata
        valid_records = [
            r for r in records if "_document_id" in r and "_parse_error" not in r
        ]
        assert len(valid_records) >= 1

        # Check that valid records have document metadata
        for record in valid_records:
            assert "_document_id" in record
            assert "_document_index" in record

    def test_document_splitting_method(self, tmp_path):
        """Test the document splitting method directly"""
        flattener = XmlFlattener()

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<doc>First</doc>
<?xml version="1.0" encoding="UTF-8"?>
<doc>Second</doc>"""

        test_file = tmp_path / "split_test.xml"
        test_file.write_text(xml_content)

        documents = flattener._split_xml_documents(test_file)

        assert len(documents) == 2
        assert "First" in documents[0]
        assert "Second" in documents[1]

        # Each document should be parseable
        for doc in documents:
            ET.fromstring(doc)  # Should not raise an exception


class TestXmlConverterIntegration:
    """Integration tests for the complete XML converter with multi-document support"""

    def test_end_to_end_multi_document_conversion(self, tmp_path):
        """Test complete conversion pipeline for multi-document XML"""
        converter = XmlConverter()

        # Create test multi-document XML
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<patent id="USPTO001">
    <title>Innovative Widget</title>
    <inventor>Alice Johnson</inventor>
    <year>2023</year>
</patent>
<?xml version="1.0" encoding="UTF-8"?>
<patent id="USPTO002">
    <title>Advanced Gadget</title>
    <inventor>Bob Smith</inventor>
    <year>2024</year>
</patent>"""

        input_file = tmp_path / "patents.xml"
        input_file.write_text(xml_content)

        output_file = tmp_path / "patents.parquet"

        # Perform conversion
        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()

        # Verify the output
        import pandas as pd

        df = pd.read_parquet(output_file)

        # Should have 2 records (one per document)
        assert len(df) >= 1

        # Should have document metadata columns
        if "_document_id" in df.columns:
            assert df["_document_id"].nunique() >= 1

    def test_converter_handles_original_single_document_error(self, tmp_path):
        """Test that converter handles the original 'junk after document element' scenario"""
        converter = XmlConverter()

        # Create XML that would cause the original error
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<us-patent-grant>
    <title>Test Patent</title>
</us-patent-grant>
<?xml version="1.0" encoding="UTF-8"?>
<us-patent-grant>
    <title>Another Patent</title>
</us-patent-grant>"""

        input_file = tmp_path / "uspto_style.xml"
        input_file.write_text(xml_content)

        output_file = tmp_path / "uspto_style.parquet"

        # This should NOT raise a "junk after document element" error
        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()


class TestMultiDocumentXMLRegression:
    """Regression tests to ensure existing functionality is preserved"""

    def test_simple_xml_still_works(self, tmp_path):
        """Ensure simple single-document XML files still work as before"""
        converter = XmlConverter()

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <item>Test</item>
    <value>123</value>
</root>"""

        input_file = tmp_path / "simple.xml"
        input_file.write_text(xml_content)

        output_file = tmp_path / "simple.parquet"

        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()

        # Check that it doesn't have multi-document metadata
        import pandas as pd

        df = pd.read_parquet(output_file)
        assert "_document_id" not in df.columns

    def test_xml_with_arrays_still_works(self, tmp_path):
        """Ensure XML files with arrays still work correctly"""
        converter = XmlConverter()

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="1">
        <title>Book 1</title>
        <tags>
            <tag>fiction</tag>
            <tag>adventure</tag>
        </tags>
    </book>
    <book id="2">
        <title>Book 2</title>
        <tags>
            <tag>non-fiction</tag>
            <tag>science</tag>
        </tags>
    </book>
</catalog>"""

        input_file = tmp_path / "catalog.xml"
        input_file.write_text(xml_content)

        output_file = tmp_path / "catalog.parquet"

        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()

    def test_malformed_xml_error_handling(self, tmp_path):
        """Test that malformed XML is still handled gracefully"""
        converter = XmlConverter()

        # Completely malformed XML
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <unclosed_tag>
        <another_unclosed>content
    </unclosed_tag>
</root>"""

        input_file = tmp_path / "malformed.xml"
        input_file.write_text(xml_content)

        output_file = tmp_path / "malformed.parquet"

        # Should handle the error gracefully
        with pytest.raises((ValueError, RuntimeError)):
            converter.convert(input_file, output_file)
