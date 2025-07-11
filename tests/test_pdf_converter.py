"""Tests for PDF converter."""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from cortexpy_cli.converters.pdf_converter import PDFConverter


class TestPDFConverter:
    """Test cases for PDFConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = PDFConverter()

    def test_init(self):
        """Test converter initialization."""
        assert ".pdf" in self.converter.supported_inputs
        assert ".txt" in self.converter.supported_outputs

    def test_parse_page_range_single_page(self):
        """Test parsing single page range."""
        start, end = self.converter._parse_page_range("5", 10)
        assert start == 4  # 0-indexed
        assert end == 4

    def test_parse_page_range_full_range(self):
        """Test parsing full page range."""
        start, end = self.converter._parse_page_range("3-7", 10)
        assert start == 2  # 0-indexed
        assert end == 6

    def test_parse_page_range_from_start(self):
        """Test parsing range from start."""
        start, end = self.converter._parse_page_range("-5", 10)
        assert start == 0
        assert end == 4

    def test_parse_page_range_to_end(self):
        """Test parsing range to end."""
        start, end = self.converter._parse_page_range("3-", 10)
        assert start == 2
        assert end == 9

    def test_parse_page_range_invalid(self):
        """Test parsing invalid page range."""
        start, end = self.converter._parse_page_range("invalid", 10)
        assert start == 0
        assert end == 9  # Full range fallback

    def test_validate_input_nonexistent_file(self):
        """Test validation with nonexistent file."""
        fake_path = Path("nonexistent.pdf")
        assert not self.converter.validate_input(fake_path)

    def test_validate_input_wrong_extension(self):
        """Test validation with wrong file extension."""
        with patch("pathlib.Path.exists", return_value=True):
            fake_path = Path("document.txt")
            assert not self.converter.validate_input(fake_path)

    @patch("fitz.open")
    def test_validate_input_valid_pdf(self, mock_fitz_open):
        """Test validation with valid PDF."""
        mock_doc = Mock()
        mock_fitz_open.return_value = mock_doc

        with patch("pathlib.Path.exists", return_value=True):
            pdf_path = Path("document.pdf")
            assert self.converter.validate_input(pdf_path)

        mock_fitz_open.assert_called_once()
        mock_doc.close.assert_called_once()

    @patch("fitz.open")
    def test_validate_input_invalid_pdf(self, mock_fitz_open):
        """Test validation with invalid PDF file."""
        mock_fitz_open.side_effect = Exception("Invalid PDF")

        with patch("pathlib.Path.exists", return_value=True):
            pdf_path = Path("corrupted.pdf")
            assert not self.converter.validate_input(pdf_path)

    @patch("fitz.open")
    def test_get_metadata_success(self, mock_fitz_open):
        """Test successful metadata extraction."""
        mock_doc = Mock()
        mock_doc.metadata = {
            "title": "Test Document",
            "author": "Test Author",
            "creationDate": "2023-01-01",
        }
        mock_doc.__len__ = Mock(return_value=5)
        mock_fitz_open.return_value = mock_doc

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value.st_size = 1024

            pdf_path = Path("document.pdf")
            metadata = self.converter.get_metadata(pdf_path)

            assert metadata is not None
            assert metadata["title"] == "Test Document"
            assert metadata["author"] == "Test Author"
            assert metadata["page_count"] == 5
            assert metadata["file_size"] == 1024

        mock_doc.close.assert_called_once()

    @patch("fitz.open")
    def test_get_metadata_failure(self, mock_fitz_open):
        """Test metadata extraction failure."""
        mock_fitz_open.side_effect = Exception("Cannot open PDF")

        pdf_path = Path("corrupted.pdf")
        metadata = self.converter.get_metadata(pdf_path)

        assert metadata is None

    @patch("builtins.open", new_callable=mock_open)
    @patch("fitz.open")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.stat")
    def test_convert_success(
        self, mock_stat, mock_mkdir, mock_fitz_open, mock_file_open
    ):
        """Test successful PDF conversion."""
        # Setup mocks
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "Sample text content"
        mock_doc.__len__ = Mock(return_value=1)
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc
        mock_stat.return_value.st_size = 512

        with patch.object(self.converter, "validate_input", return_value=True):
            input_path = Path("document.pdf")
            output_path = Path("output.txt")

            result = self.converter.convert(input_path, output_path)

            assert result is True
            mock_file_open.assert_called_once()
            mock_doc.close.assert_called_once()

    @patch("fitz.open")
    def test_convert_invalid_input(self, mock_fitz_open):
        """Test conversion with invalid input."""
        with patch.object(self.converter, "validate_input", return_value=False):
            input_path = Path("invalid.pdf")
            output_path = Path("output.txt")

            result = self.converter.convert(input_path, output_path)

            assert result is False
            mock_fitz_open.assert_not_called()

    @patch("fitz.open")
    def test_convert_with_page_range(self, mock_fitz_open):
        """Test conversion with page range option."""
        # Setup mocks
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "Page content"
        mock_doc.__len__ = Mock(return_value=10)
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc

        with patch.object(self.converter, "validate_input", return_value=True), patch(
            "builtins.open", mock_open()
        ), patch("pathlib.Path.mkdir"), patch("pathlib.Path.stat") as mock_stat:

            mock_stat.return_value.st_size = 256

            input_path = Path("document.pdf")
            output_path = Path("output.txt")

            result = self.converter.convert(input_path, output_path, page_range="1-3")

            assert result is True
            # Should process pages 0, 1, 2 (0-indexed)
            assert mock_doc.__getitem__.call_count >= 3
