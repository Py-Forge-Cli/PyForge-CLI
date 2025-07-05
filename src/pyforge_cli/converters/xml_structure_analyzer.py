"""XML structure analyzer for detecting schema and hierarchies."""

import logging
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class XmlElement:
    """Represents an XML element with its metadata."""

    def __init__(self, tag: str, path: str):
        self.tag = tag
        self.path = path
        self.attributes: Set[str] = set()
        self.has_text = False
        self.has_children = False
        self.is_array = False
        self.occurrences = 0
        self.children: Set[str] = set()
        self.namespace = None
        self.local_name = tag

        # Extract namespace if present
        if tag.startswith("{"):
            self.namespace, self.local_name = tag[1:].split("}", 1)

    def __repr__(self):
        return f"XmlElement(tag={self.tag}, path={self.path}, array={self.is_array})"


class XmlStructureAnalyzer:
    """Analyzes XML structure to detect schema, arrays, and nesting."""

    def __init__(self):
        self.elements: Dict[str, XmlElement] = {}
        self.namespaces: Dict[str, str] = {}
        self.max_depth = 0
        self.array_elements: Set[str] = set()
        self.root_tag = None

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze XML file structure, supporting both single and multi-document XML files.

        Args:
            file_path: Path to XML file

        Returns:
            Dictionary with structure analysis results
        """
        try:
            # First, try to parse as single document
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                # Reset state
                self.elements.clear()
                self.namespaces.clear()
                self.array_elements.clear()
                self.max_depth = 0

                # Extract namespaces from root
                self.namespaces = dict(root.attrib.items())
                self.namespaces.update(self._extract_namespaces(root))

                # Set root tag
                self.root_tag = root.tag

                # Analyze structure
                self._analyze_element(root, "", 0)

                # Detect arrays
                self._detect_arrays()

                # Build analysis results
                results = self._build_analysis_results()
                results["is_multi_document"] = False
                results["document_count"] = 1
                return results

            except ET.ParseError as parse_error:
                # Check if this is a multi-document XML file
                if "junk after document element" in str(parse_error):
                    logger.info(
                        "Detected multi-document XML file, attempting to parse each document separately"
                    )
                    return self._analyze_multi_document_file(file_path)
                else:
                    # Re-raise the original error if it's not a multi-document issue
                    raise parse_error

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise ValueError(f"Invalid XML file: {e}")
        except Exception as e:
            logger.error(f"Error analyzing XML structure: {e}")
            raise

    def _analyze_multi_document_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a multi-document XML file by splitting it into individual documents.

        Args:
            file_path: Path to multi-document XML file

        Returns:
            Dictionary with combined analysis results from all documents
        """
        try:
            # Split the file into individual XML documents
            documents = self._split_xml_documents(file_path)

            if not documents:
                raise ValueError("No valid XML documents found in file")

            logger.info(f"Found {len(documents)} XML documents in file")

            # Reset state for combined analysis
            self.elements.clear()
            self.namespaces.clear()
            self.array_elements.clear()
            self.max_depth = 0

            all_root_tags = []
            document_analyses = []

            # Analyze each document separately
            for i, doc_content in enumerate(documents):
                try:
                    # Parse individual document
                    root = ET.fromstring(doc_content)
                    all_root_tags.append(root.tag)

                    # Store first document's root tag as primary
                    if i == 0:
                        self.root_tag = root.tag
                        # Extract namespaces from first document
                        self.namespaces = dict(root.attrib.items())
                        self.namespaces.update(self._extract_namespaces(root))

                    # Analyze this document's structure
                    doc_prefix = f"doc_{i+1}"
                    self._analyze_element(root, doc_prefix, 0)

                    # Store individual document analysis for reference
                    doc_elements = {}
                    for path, elem in self.elements.items():
                        if path.startswith(doc_prefix):
                            doc_elements[path] = elem

                    document_analyses.append(
                        {
                            "document_id": i + 1,
                            "root_tag": root.tag,
                            "elements": len(doc_elements),
                        }
                    )

                except ET.ParseError as e:
                    logger.warning(f"Failed to parse document {i+1}: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"Error analyzing document {i+1}: {e}")
                    continue

            # Detect arrays across all documents
            self._detect_arrays()

            # Build combined analysis results
            results = self._build_analysis_results()
            results["is_multi_document"] = True
            results["document_count"] = len(documents)
            results["root_tags"] = list(set(all_root_tags))  # Unique root tags
            results["document_analyses"] = document_analyses

            return results

        except Exception as e:
            logger.error(f"Error analyzing multi-document XML file: {e}")
            raise ValueError(f"Failed to analyze multi-document XML: {e}")

    def _split_xml_documents(self, file_path: Path) -> List[str]:
        """
        Split a multi-document XML file into individual XML document strings.

        Args:
            file_path: Path to the multi-document XML file

        Returns:
            List of individual XML document strings
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Split on XML declarations to find document boundaries
            # Pattern to match XML declaration at the start of documents
            xml_declaration_pattern = r'<\?xml\s+version\s*=\s*["\'][^"\']*["\']\s*encoding\s*=\s*["\'][^"\']*["\']\s*\?>'

            # Find all XML declarations
            declarations = list(
                re.finditer(xml_declaration_pattern, content, re.IGNORECASE)
            )

            if len(declarations) <= 1:
                # Single document or no XML declarations found
                # Try to split on DOCTYPE or root elements
                return self._split_by_root_elements(content)

            documents = []

            for i, declaration in enumerate(declarations):
                start_pos = declaration.start()

                # Determine end position (start of next declaration or end of file)
                if i + 1 < len(declarations):
                    end_pos = declarations[i + 1].start()
                else:
                    end_pos = len(content)

                # Extract document content
                doc_content = content[start_pos:end_pos].strip()

                if doc_content:
                    # Basic validation - ensure it has both opening and closing tags
                    if self._validate_xml_document(doc_content):
                        documents.append(doc_content)
                    else:
                        logger.warning(
                            f"Document {i+1} appears to be incomplete or invalid"
                        )

            return documents

        except Exception as e:
            logger.error(f"Error splitting XML documents: {e}")
            return []

    def _split_by_root_elements(self, content: str) -> List[str]:
        """
        Fallback method to split XML by identifying root elements.

        Args:
            content: Full XML content

        Returns:
            List of individual XML document strings
        """
        # This is a more complex approach for cases where XML declarations are missing
        # For now, return the original content as a single document
        # This could be enhanced to detect common patterns like repeated root elements

        # Simple heuristic: if content contains multiple closing tags that look like root elements
        # (not indented), try to split there
        lines = content.split("\n")
        potential_end_tags = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Look for closing tags at the start of lines (indicating root level)
            if (
                stripped.startswith("</")
                and not line.startswith("  ")
                and not line.startswith("\t")
            ):
                potential_end_tags.append(i)

        # If we found multiple potential document endings, try to split
        if len(potential_end_tags) > 1:
            documents = []
            start_idx = 0

            for end_idx in potential_end_tags[:-1]:  # Don't include the last one
                # Find the next line that looks like a document start
                next_start = None
                for j in range(end_idx + 1, len(lines)):
                    if lines[j].strip().startswith("<?xml") or lines[
                        j
                    ].strip().startswith("<"):
                        next_start = j
                        break

                if next_start:
                    doc_lines = lines[start_idx:next_start]
                    doc_content = "\n".join(doc_lines).strip()
                    if doc_content and self._validate_xml_document(doc_content):
                        documents.append(doc_content)
                    start_idx = next_start

            # Add the last document
            if start_idx < len(lines):
                doc_content = "\n".join(lines[start_idx:]).strip()
                if doc_content and self._validate_xml_document(doc_content):
                    documents.append(doc_content)

            return documents if documents else [content.strip()]

        return [content.strip()]

    def _validate_xml_document(self, doc_content: str) -> bool:
        """
        Basic validation to check if a string contains a valid XML document.

        Args:
            doc_content: XML document content

        Returns:
            True if content appears to be a valid XML document
        """
        try:
            # Try to parse the document
            ET.fromstring(doc_content)
            return True
        except ET.ParseError:
            return False
        except Exception:
            return False

    def _extract_namespaces(self, element: ET.Element) -> Dict[str, str]:
        """Extract namespace declarations from element."""
        namespaces = {}
        for key, value in element.attrib.items():
            if key.startswith("xmlns:"):
                prefix = key[6:]
                namespaces[prefix] = value
            elif key == "xmlns":
                namespaces[""] = value
        return namespaces

    def _analyze_element(self, element: ET.Element, parent_path: str, depth: int):
        """Recursively analyze XML element structure."""
        # Update max depth
        self.max_depth = max(self.max_depth, depth)

        # Build element path
        element_path = f"{parent_path}/{element.tag}" if parent_path else element.tag

        # Get or create element info
        if element_path not in self.elements:
            self.elements[element_path] = XmlElement(element.tag, element_path)

        elem_info = self.elements[element_path]
        elem_info.occurrences += 1

        # Check for text content
        if element.text and element.text.strip():
            elem_info.has_text = True

        # Analyze attributes
        for attr_name in element.attrib:
            if not attr_name.startswith("xmlns"):
                elem_info.attributes.add(attr_name)

        # Track child elements
        child_tags = Counter()
        for child in element:
            child_tags[child.tag] += 1
            elem_info.children.add(child.tag)

        # Recursively analyze children
        if len(element) > 0:
            elem_info.has_children = True
            for child in element:
                self._analyze_element(child, element_path, depth + 1)

        # Check for repeated children (potential arrays)
        for child_tag, count in child_tags.items():
            if count > 1:
                child_path = f"{element_path}/{child_tag}"
                if child_path in self.elements:
                    self.elements[child_path].is_array = True
                    self.array_elements.add(child_path)

    def _detect_arrays(self):
        """Detect array elements based on occurrence patterns."""
        # Additional array detection based on parent-child relationships
        parent_child_count = defaultdict(lambda: defaultdict(int))

        for path, elem in self.elements.items():
            if "/" in path:
                parent_path = path.rsplit("/", 1)[0]
                if parent_path in self.elements:
                    parent_child_count[parent_path][elem.tag] += elem.occurrences

        # Mark elements as arrays if they appear multiple times under same parent
        for parent_path, children in parent_child_count.items():
            for child_tag, count in children.items():
                if count > 1:
                    child_path = f"{parent_path}/{child_tag}"
                    if child_path in self.elements:
                        self.elements[child_path].is_array = True
                        self.array_elements.add(child_path)

        # Remove false positives: elements that appear once per parent instance
        # but the parent itself is an array
        elements_to_remove = []
        for array_path in list(self.array_elements):
            if "/" in array_path:
                parent_path = array_path.rsplit("/", 1)[0]
                if parent_path in self.array_elements:
                    # Check if this element appears exactly once per parent instance
                    parent_occurrences = self.elements[parent_path].occurrences
                    child_occurrences = self.elements[array_path].occurrences
                    if child_occurrences == parent_occurrences:
                        # This is not really an array, just appears once per parent
                        elements_to_remove.append(array_path)

        for path in elements_to_remove:
            self.array_elements.discard(path)
            if path in self.elements:
                self.elements[path].is_array = False

    def _build_analysis_results(self) -> Dict[str, Any]:
        """Build comprehensive analysis results."""
        # Group elements by depth
        elements_by_depth = defaultdict(list)
        for path, elem in self.elements.items():
            depth = path.count("/")
            elements_by_depth[depth].append(elem)

        # Build flattened column preview
        columns = []
        for path, elem in sorted(self.elements.items()):
            if elem.has_text or elem.attributes:
                # Element with text content
                if elem.has_text:
                    col_name = path.replace("/", "_")
                    columns.append(
                        {
                            "name": col_name,
                            "path": path,
                            "type": "element",
                            "is_array": elem.is_array,
                        }
                    )

                # Attributes
                for attr in sorted(elem.attributes):
                    col_name = f"{path.replace('/', '_')}@{attr}"
                    columns.append(
                        {
                            "name": col_name,
                            "path": f"{path}@{attr}",
                            "type": "attribute",
                            "is_array": elem.is_array,
                        }
                    )

        return {
            "root_tag": self.root_tag,
            "namespaces": self.namespaces,
            "max_depth": self.max_depth,
            "total_elements": len(self.elements),
            "array_elements": list(self.array_elements),
            "elements": {
                path: {
                    "tag": elem.tag,
                    "local_name": elem.local_name,
                    "namespace": elem.namespace,
                    "attributes": list(elem.attributes),
                    "has_text": elem.has_text,
                    "has_children": elem.has_children,
                    "is_array": elem.is_array,
                    "occurrences": elem.occurrences,
                    "children": list(elem.children),
                }
                for path, elem in self.elements.items()
            },
            "depth_distribution": {
                depth: len(elems) for depth, elems in elements_by_depth.items()
            },
            "suggested_columns": columns,
        }

    def get_schema_preview(self) -> str:
        """Generate a human-readable schema preview."""
        lines = []
        lines.append("XML Structure Preview")
        lines.append("=" * 50)
        lines.append(f"Root element: {self.root_tag}")
        lines.append(f"Max nesting depth: {self.max_depth}")
        lines.append(f"Total unique elements: {len(self.elements)}")

        if self.namespaces:
            lines.append("\nNamespaces:")
            for prefix, uri in self.namespaces.items():
                prefix_str = prefix if prefix else "(default)"
                lines.append(f"  {prefix_str}: {uri}")

        if self.array_elements:
            lines.append("\nDetected Arrays:")
            for array_path in sorted(self.array_elements):
                lines.append(f"  {array_path}")

        lines.append("\nSuggested Column Mapping:")
        results = self._build_analysis_results()
        for col in results["suggested_columns"][:20]:  # Show first 20 columns
            array_marker = " [ARRAY]" if col["is_array"] else ""
            lines.append(f"  {col['name']}{array_marker}")

        if len(results["suggested_columns"]) > 20:
            lines.append(
                f"  ... and {len(results['suggested_columns']) - 20} more columns"
            )

        return "\n".join(lines)
