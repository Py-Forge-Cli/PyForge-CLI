"""PDF to text converter using PyMuPDF."""

from pathlib import Path
from typing import Any, Dict, Optional

import fitz
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

from .base import BaseConverter


class PDFConverter(BaseConverter):
    """PDF to text format converter."""

    def __init__(self):
        super().__init__()
        self.supported_inputs = {".pdf"}
        self.supported_outputs = {".txt"}
        self.console = Console()

    def convert(self, input_path: Path, output_path: Path, **options: Any) -> bool:
        """Convert PDF to text format.

        Args:
            input_path: Path to PDF file
            output_path: Path to output text file
            **options: Additional options like 'page_range', 'extract_images'

        Returns:
            bool: True if conversion successful
        """
        try:
            if not self.validate_input(input_path):
                self.console.print(f"[red]Error: Invalid PDF file: {input_path}[/red]")
                return False

            # Open PDF document
            doc = fitz.open(str(input_path))

            # Get conversion options
            page_range = options.get("page_range")
            include_metadata = options.get("include_metadata", False)

            # Determine pages to process
            if page_range:
                start_page, end_page = self._parse_page_range(page_range, len(doc))
                pages_to_process = range(start_page, min(end_page + 1, len(doc)))
            else:
                pages_to_process = range(len(doc))

            # Extract text with progress bar
            extracted_text = []

            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                console=self.console,
            ) as progress:
                task = progress.add_task(
                    f"Converting {input_path.name}", total=len(pages_to_process)
                )

                for page_num in pages_to_process:
                    page = doc[page_num]
                    text = page.get_text()

                    if text.strip():  # Only add non-empty pages
                        if include_metadata:
                            extracted_text.append(f"\n--- Page {page_num + 1} ---\n")
                        extracted_text.append(text)
                        if include_metadata:
                            extracted_text.append(
                                f"\n--- End Page {page_num + 1} ---\n"
                            )

                    progress.advance(task)

            # Write output file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(extracted_text))

            doc.close()

            # Show success message
            self.console.print(
                f"[green][OK] Successfully converted {input_path.name} to {output_path.name}[/green]"
            )
            self.console.print(f"[dim]Pages processed: {len(pages_to_process)}[/dim]")
            self.console.print(
                f"[dim]Output size: {output_path.stat().st_size:,} bytes[/dim]"
            )

            return True

        except Exception as e:
            self.console.print(f"[red]Error converting PDF: {str(e)}[/red]")
            return False

    def validate_input(self, input_path: Path) -> bool:
        """Validate if PDF file can be processed.

        Args:
            input_path: Path to PDF file

        Returns:
            bool: True if file is a valid PDF
        """
        if not input_path.exists():
            return False

        if input_path.suffix.lower() not in self.supported_inputs:
            return False

        try:
            # Try to open the PDF to verify it's valid
            doc = fitz.open(str(input_path))
            doc.close()
            return True
        except Exception:
            return False

    def get_metadata(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from PDF file.

        Args:
            input_path: Path to PDF file

        Returns:
            Optional[Dict[str, Any]]: PDF metadata
        """
        try:
            doc = fitz.open(str(input_path))
            metadata = doc.metadata

            result = {
                "title": metadata.get("title") or None,
                "author": metadata.get("author") or None,
                "subject": metadata.get("subject") or None,
                "creator": metadata.get("creator") or None,
                "producer": metadata.get("producer") or None,
                "keywords": metadata.get("keywords") or None,
                "creation_date": metadata.get("creationDate") or None,
                "modification_date": metadata.get("modDate") or None,
                "page_count": len(doc),
                "file_size": input_path.stat().st_size,
            }

            doc.close()
            return result

        except Exception:
            return None

    def _parse_page_range(self, page_range: str, total_pages: int) -> tuple[int, int]:
        """Parse page range string like '1-5' or '3-' or '-10'.

        Args:
            page_range: Page range string
            total_pages: Total number of pages in document

        Returns:
            tuple[int, int]: (start_page, end_page) 0-indexed
        """
        try:
            if "-" not in page_range:
                # Single page
                page = int(page_range) - 1  # Convert to 0-indexed
                return max(0, page), min(page, total_pages - 1)

            parts = page_range.split("-", 1)

            if parts[0] == "":
                # Format: '-10' (from start to page 10)
                start_page = 0
                end_page = int(parts[1]) - 1
            elif parts[1] == "":
                # Format: '5-' (from page 5 to end)
                start_page = int(parts[0]) - 1
                end_page = total_pages - 1
            else:
                # Format: '5-10' (from page 5 to 10)
                start_page = int(parts[0]) - 1
                end_page = int(parts[1]) - 1

            # Ensure valid range
            start_page = max(0, start_page)
            end_page = min(end_page, total_pages - 1)

            return start_page, end_page

        except (ValueError, IndexError):
            # Invalid format, return full range
            return 0, total_pages - 1
