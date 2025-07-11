"""XML flattening engine for converting hierarchical XML to tabular format."""

import json
import logging
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class XmlFlattener:
    """Flattens XML hierarchical structure into tabular format."""

    def __init__(self):
        self.flatten_strategy = "conservative"
        self.array_handling = "expand"
        self.namespace_handling = "preserve"

    def flatten_file(
        self,
        file_path: Path,
        structure_analysis: Dict[str, Any],
        flatten_strategy: str = "conservative",
        array_handling: str = "expand",
        namespace_handling: str = "preserve",
    ) -> List[Dict[str, str]]:
        """
        Flatten XML file to list of records, supporting both single and multi-document XML.

        Args:
            file_path: Path to XML file
            structure_analysis: Analysis from XmlStructureAnalyzer
            flatten_strategy: Flattening strategy ('conservative', 'moderate', 'aggressive')
            array_handling: Array handling ('expand', 'concatenate', 'json_string')
            namespace_handling: Namespace handling ('preserve', 'strip', 'prefix')

        Returns:
            List of dictionaries representing flattened records
        """
        self.flatten_strategy = flatten_strategy
        self.array_handling = array_handling
        self.namespace_handling = namespace_handling

        try:
            # Check if this is a multi-document XML file
            is_multi_doc = structure_analysis.get("is_multi_document", False)

            if is_multi_doc:
                return self._flatten_multi_document_file(file_path, structure_analysis)
            else:
                # Single document - use existing logic
                tree = ET.parse(file_path)
                root = tree.getroot()

                # Get array elements from analysis
                array_elements = set(structure_analysis.get("array_elements", []))

                # Flatten based on strategy
                if flatten_strategy == "conservative":
                    return self._flatten_conservative(root, array_elements)
                elif flatten_strategy == "moderate":
                    return self._flatten_moderate(root, array_elements)
                elif flatten_strategy == "aggressive":
                    return self._flatten_aggressive(root, array_elements)
                else:
                    raise ValueError(f"Unknown flatten strategy: {flatten_strategy}")

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise ValueError(f"Invalid XML file: {e}") from e
        except Exception as e:
            logger.error(f"Error flattening XML: {e}")
            raise

    def _flatten_multi_document_file(
        self, file_path: Path, structure_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Flatten a multi-document XML file by processing each document separately.

        Args:
            file_path: Path to multi-document XML file
            structure_analysis: Analysis results from XmlStructureAnalyzer

        Returns:
            List of flattened records from all documents
        """
        try:
            # Split the file into individual documents (reuse logic from analyzer)
            documents = self._split_xml_documents(file_path)

            if not documents:
                logger.warning("No valid XML documents found in multi-document file")
                return []

            logger.info(f"Processing {len(documents)} XML documents for flattening")

            all_records = []
            array_elements = set(structure_analysis.get("array_elements", []))

            # Process each document separately
            for i, doc_content in enumerate(documents):
                try:
                    # Parse individual document
                    root = ET.fromstring(doc_content)

                    # Flatten this document based on strategy
                    if self.flatten_strategy == "conservative":
                        doc_records = self._flatten_conservative(root, array_elements)
                    elif self.flatten_strategy == "moderate":
                        doc_records = self._flatten_moderate(root, array_elements)
                    elif self.flatten_strategy == "aggressive":
                        doc_records = self._flatten_aggressive(root, array_elements)
                    else:
                        raise ValueError(
                            f"Unknown flatten strategy: {self.flatten_strategy}"
                        )

                    # Add document metadata to each record
                    for record in doc_records:
                        record["_document_id"] = i + 1
                        record["_document_index"] = i

                    all_records.extend(doc_records)

                except ET.ParseError as e:
                    logger.warning(f"Failed to parse document {i + 1}: {e}")
                    # Create an error record for this document
                    error_record = {
                        "_document_id": i + 1,
                        "_document_index": i,
                        "_parse_error": str(e),
                    }
                    all_records.append(error_record)
                    continue
                except Exception as e:
                    logger.warning(f"Error processing document {i + 1}: {e}")
                    continue

            logger.info(
                f"Successfully flattened {len(all_records)} records from {len(documents)} documents"
            )
            return all_records

        except Exception as e:
            logger.error(f"Error flattening multi-document XML: {e}")
            raise ValueError(f"Failed to flatten multi-document XML: {e}") from e

    def _split_xml_documents(self, file_path: Path) -> List[str]:
        """
        Split a multi-document XML file into individual XML document strings.
        (Reused from XmlStructureAnalyzer for consistency)
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Split on XML declarations to find document boundaries
            xml_declaration_pattern = r'<\?xml\s+version\s*=\s*["\'][^"\']*["\']\s*encoding\s*=\s*["\'][^"\']*["\']\s*\?>'

            # Find all XML declarations
            declarations = list(
                re.finditer(xml_declaration_pattern, content, re.IGNORECASE)
            )

            if len(declarations) <= 1:
                # Single document or no XML declarations found
                return [content.strip()]

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
                    # Basic validation
                    try:
                        ET.fromstring(doc_content)
                        documents.append(doc_content)
                    except ET.ParseError:
                        logger.warning(
                            f"Document {i + 1} appears to be invalid, skipping"
                        )
                        continue

            return documents

        except Exception as e:
            logger.error(f"Error splitting XML documents: {e}")
            return []

    def _flatten_conservative(
        self, root: ET.Element, array_elements: set
    ) -> List[Dict[str, str]]:
        """
        Conservative flattening: Minimal flattening, preserve structure.
        Creates records only for elements that contain data or are arrays.
        """
        records = []

        # Find the main data containers (elements with repeated children or leaf data)
        data_containers = self._find_data_containers(root, array_elements)

        if not data_containers:
            # If no clear data containers, flatten the root element
            record = self._extract_element_data(root, "", array_elements)
            if record:
                records.append(record)
        else:
            # Process each data container
            for container_path, elements in data_containers.items():
                for element in elements:
                    record = self._extract_element_data(
                        element, container_path, array_elements
                    )
                    if record:
                        records.append(record)

        return records

    def _flatten_moderate(
        self, root: ET.Element, array_elements: set
    ) -> List[Dict[str, str]]:
        """
        Moderate flattening: Balance between structure and usability.
        Creates records for logical data units.
        """
        records = []

        # Find elements that represent logical records
        record_elements = self._find_record_elements(root, array_elements)

        for element in record_elements:
            record = self._extract_element_data_moderate(element, "", array_elements)
            if record:
                records.append(record)

        return records

    def _flatten_aggressive(
        self, root: ET.Element, array_elements: set
    ) -> List[Dict[str, str]]:
        """
        Aggressive flattening: Maximum flattening for analytics.
        Creates one record per unique combination of leaf values.
        """
        # For aggressive flattening, we create a record for each unique path combination
        all_paths = self._get_all_leaf_paths(root, "")

        # Group paths by their array parent
        path_groups = self._group_paths_by_arrays(all_paths, array_elements)

        records = []
        for group in path_groups:
            record = {}
            for path, value in group.items():
                column_name = self._path_to_column_name(path)
                record[column_name] = str(value) if value is not None else ""
            if record:
                records.append(record)

        return records

    def _find_data_containers(
        self, root: ET.Element, array_elements: set
    ) -> Dict[str, List[ET.Element]]:
        """Find elements that contain the main data."""
        containers = defaultdict(list)

        # For simple XML without arrays, treat the root as the data container
        if not array_elements:
            containers[root.tag].append(root)
            return dict(containers)

        def traverse(element, path):
            current_path = f"{path}/{element.tag}" if path else element.tag

            # Check if this element is an array
            if current_path in array_elements:
                containers[current_path].append(element)
            else:
                # Traverse children to find arrays
                for child in element:
                    traverse(child, current_path)

        traverse(root, "")

        # If no containers found, use root
        if not containers:
            containers[root.tag].append(root)

        return dict(containers)

    def _find_record_elements(
        self, root: ET.Element, array_elements: set
    ) -> List[ET.Element]:
        """Find elements that represent logical records."""
        record_elements = []

        def traverse(element, path):
            current_path = f"{path}/{element.tag}" if path else element.tag

            # If this is an array element, each instance is a record
            if current_path in array_elements:
                record_elements.append(element)
            else:
                # Traverse children
                for child in element:
                    traverse(child, current_path)

        traverse(root, "")

        # If no array elements found, use root
        if not record_elements:
            record_elements.append(root)

        return record_elements

    def _extract_element_data(
        self, element: ET.Element, parent_path: str, array_elements: set
    ) -> Dict[str, str]:
        """Extract data from an element and its children."""
        record = {}

        # Add attributes
        for attr_name, attr_value in element.attrib.items():
            column_name = self._format_attribute_name(
                element.tag, attr_name, parent_path
            )
            record[column_name] = str(attr_value)

        # Add text content if present and element has no children
        if element.text and element.text.strip() and len(element) == 0:
            column_name = self._format_element_name(element.tag, parent_path)
            record[column_name] = element.text.strip()

        # Process children
        processed_array_tags = set()

        for child in element:
            child_path = f"{parent_path}/{element.tag}" if parent_path else element.tag
            full_child_path = f"{child_path}/{child.tag}"

            if (
                full_child_path in array_elements
                and child.tag not in processed_array_tags
            ):
                # Handle array child - collect all instances
                array_values = []
                attributes_found = {}

                for sibling in element:
                    if sibling.tag == child.tag:
                        value = self._get_element_value(sibling)
                        if value:
                            array_values.append(value)

                        # Collect attributes from the first instance
                        if not attributes_found:
                            for attr_name, attr_value in sibling.attrib.items():
                                column_name = self._format_attribute_name(
                                    child.tag, attr_name, child_path
                                )
                                attributes_found[column_name] = str(attr_value)

                # Add array values
                if array_values:
                    column_name = self._format_element_name(child.tag, child_path)
                    record[column_name] = self._format_array_values(array_values)

                # Add attributes
                record.update(attributes_found)

                processed_array_tags.add(child.tag)

            elif child.tag not in processed_array_tags:
                # Handle single child
                if len(child) == 0:
                    # Element with only text and attributes (leaf element)
                    # Add text content
                    if child.text and child.text.strip():
                        column_name = self._format_element_name(child.tag, child_path)
                        record[column_name] = child.text.strip()

                    # Add attributes
                    for attr_name, attr_value in child.attrib.items():
                        column_name = self._format_attribute_name(
                            child.tag, attr_name, child_path
                        )
                        record[column_name] = str(attr_value)
                else:
                    # Complex child with children - could contain arrays
                    # Check if any grandchildren are arrays
                    has_array_children = False
                    for grandchild in child:
                        grandchild_path = f"{child_path}/{child.tag}/{grandchild.tag}"
                        if grandchild_path in array_elements:
                            has_array_children = True
                            break

                    if has_array_children:
                        # This element contains array children - handle specially
                        # Look for array grandchildren and collect their values
                        for grandchild in child:
                            grandchild_path = (
                                f"{child_path}/{child.tag}/{grandchild.tag}"
                            )
                            if grandchild_path in array_elements:
                                # Collect all instances of this array element
                                array_values = []
                                for sibling in child:
                                    if sibling.tag == grandchild.tag:
                                        value = self._get_element_value(sibling)
                                        if value:
                                            array_values.append(value)

                                if array_values:
                                    column_name = self._format_element_name(
                                        grandchild.tag, f"{child_path}/{child.tag}"
                                    )
                                    record[column_name] = self._format_array_values(
                                        array_values
                                    )
                                break  # Only process one array type per parent
                    else:
                        # Regular complex child - recursively extract
                        child_data = self._extract_element_data(
                            child, child_path, array_elements
                        )
                        record.update(child_data)

        return record

    def _extract_element_data_moderate(
        self, element: ET.Element, parent_path: str, array_elements: set
    ) -> Dict[str, str]:
        """Extract data with moderate flattening strategy."""
        record = {}
        current_path = f"{parent_path}/{element.tag}" if parent_path else element.tag

        # Add attributes with prefixed names
        for attr_name, attr_value in element.attrib.items():
            column_name = f"{element.tag}@{attr_name}"
            record[column_name] = str(attr_value)

        # Add text content
        if element.text and element.text.strip():
            record[element.tag] = element.text.strip()

        # Process children
        for child in element:
            child_path = f"{current_path}/{child.tag}"

            if child_path in array_elements:
                # Collect all array values
                array_values = []
                for sibling in element:
                    if sibling.tag == child.tag:
                        value = self._get_element_value(sibling)
                        if value:
                            array_values.append(value)

                if array_values:
                    record[child.tag] = self._format_array_values(array_values)
            else:
                # Single child
                child_value = self._get_element_value(child)
                if child_value:
                    record[child.tag] = child_value

        return record

    def _get_all_leaf_paths(self, element: ET.Element, path: str) -> Dict[str, Any]:
        """Get all leaf paths and their values."""
        paths = {}
        current_path = f"{path}/{element.tag}" if path else element.tag

        # Add attributes
        for attr_name, attr_value in element.attrib.items():
            attr_path = f"{current_path}@{attr_name}"
            paths[attr_path] = attr_value

        # Add text if present and no children
        if element.text and element.text.strip() and len(element) == 0:
            paths[current_path] = element.text.strip()

        # Recursively process children
        for child in element:
            child_paths = self._get_all_leaf_paths(child, current_path)
            paths.update(child_paths)

        return paths

    def _group_paths_by_arrays(
        self, paths: Dict[str, Any], array_elements: set
    ) -> List[Dict[str, Any]]:
        """Group paths by their array context."""
        # For now, return all paths as a single group
        # TODO: Implement proper array-based grouping
        return [paths] if paths else []

    def _get_element_value(self, element: ET.Element) -> Optional[str]:
        """Get the value of an element (text content or formatted children)."""
        if element.text and element.text.strip():
            return element.text.strip()
        elif len(element) == 0:
            return ""
        else:
            # Element has children, format as simple structure
            parts = []
            for attr_name, attr_value in element.attrib.items():
                parts.append(f"{attr_name}={attr_value}")

            for child in element:
                child_value = self._get_element_value(child)
                if child_value:
                    parts.append(f"{child.tag}:{child_value}")

            return "; ".join(parts) if parts else ""

    def _format_array_values(self, values: List[str]) -> str:
        """Format array values based on array handling strategy."""
        if self.array_handling == "concatenate":
            return "; ".join(values)
        elif self.array_handling == "json_string":
            return json.dumps(values)
        else:  # expand - for now return concatenated, full expand handled at record level
            return "; ".join(values)

    def _format_element_name(self, tag: str, parent_path: str) -> str:
        """Format element name for column."""
        clean_tag = self._clean_tag_name(tag)
        if parent_path:
            clean_parent = parent_path.replace("/", "_")
            return f"{clean_parent}_{clean_tag}"
        return clean_tag

    def _format_attribute_name(self, tag: str, attr_name: str, parent_path: str) -> str:
        """Format attribute name for column."""
        clean_tag = self._clean_tag_name(tag)
        clean_attr = self._clean_tag_name(attr_name)

        if parent_path:
            clean_parent = parent_path.replace("/", "_")
            return f"{clean_parent}_{clean_tag}@{clean_attr}"
        return f"{clean_tag}@{clean_attr}"

    def _path_to_column_name(self, path: str) -> str:
        """Convert XML path to column name."""
        # Handle attributes
        if "@" in path:
            element_path, attr_name = path.rsplit("@", 1)
            clean_path = element_path.replace("/", "_")
            clean_attr = self._clean_tag_name(attr_name)
            return f"{clean_path}@{clean_attr}"
        else:
            return path.replace("/", "_")

    def _clean_tag_name(self, tag: str) -> str:
        """Clean tag name based on namespace handling."""
        if self.namespace_handling == "strip":
            # Remove namespace
            if tag.startswith("{"):
                return tag.split("}", 1)[1]
            return tag
        elif self.namespace_handling == "prefix":
            # Convert namespace to prefix
            if tag.startswith("{"):
                namespace, local_name = tag[1:].split("}", 1)
                # Use simple prefix from namespace
                prefix = namespace.split("/")[-1][:3]  # Use last part, max 3 chars
                return f"{prefix}_{local_name}"
            return tag
        else:  # preserve
            return tag
