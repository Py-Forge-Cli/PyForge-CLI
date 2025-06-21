"""XML structure analyzer for detecting schema and hierarchies."""

import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import logging

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
        if tag.startswith('{'):
            self.namespace, self.local_name = tag[1:].split('}', 1)
    
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
        Analyze XML file structure.
        
        Args:
            file_path: Path to XML file
            
        Returns:
            Dictionary with structure analysis results
        """
        try:
            # Parse XML
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
            return self._build_analysis_results()
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise ValueError(f"Invalid XML file: {e}")
        except Exception as e:
            logger.error(f"Error analyzing XML structure: {e}")
            raise
    
    def _extract_namespaces(self, element: ET.Element) -> Dict[str, str]:
        """Extract namespace declarations from element."""
        namespaces = {}
        for key, value in element.attrib.items():
            if key.startswith('xmlns:'):
                prefix = key[6:]
                namespaces[prefix] = value
            elif key == 'xmlns':
                namespaces[''] = value
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
            if not attr_name.startswith('xmlns'):
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
            if '/' in path:
                parent_path = path.rsplit('/', 1)[0]
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
    
    def _build_analysis_results(self) -> Dict[str, Any]:
        """Build comprehensive analysis results."""
        # Group elements by depth
        elements_by_depth = defaultdict(list)
        for path, elem in self.elements.items():
            depth = path.count('/')
            elements_by_depth[depth].append(elem)
        
        # Build flattened column preview
        columns = []
        for path, elem in sorted(self.elements.items()):
            if elem.has_text or elem.attributes:
                # Element with text content
                if elem.has_text:
                    col_name = path.replace('/', '_')
                    columns.append({
                        'name': col_name,
                        'path': path,
                        'type': 'element',
                        'is_array': elem.is_array
                    })
                
                # Attributes
                for attr in sorted(elem.attributes):
                    col_name = f"{path.replace('/', '_')}@{attr}"
                    columns.append({
                        'name': col_name,
                        'path': f"{path}@{attr}",
                        'type': 'attribute',
                        'is_array': elem.is_array
                    })
        
        return {
            'root_tag': self.root_tag,
            'namespaces': self.namespaces,
            'max_depth': self.max_depth,
            'total_elements': len(self.elements),
            'array_elements': list(self.array_elements),
            'elements': {path: {
                'tag': elem.tag,
                'local_name': elem.local_name,
                'namespace': elem.namespace,
                'attributes': list(elem.attributes),
                'has_text': elem.has_text,
                'has_children': elem.has_children,
                'is_array': elem.is_array,
                'occurrences': elem.occurrences,
                'children': list(elem.children)
            } for path, elem in self.elements.items()},
            'depth_distribution': {
                depth: len(elems) for depth, elems in elements_by_depth.items()
            },
            'suggested_columns': columns
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
        for col in results['suggested_columns'][:20]:  # Show first 20 columns
            array_marker = " [ARRAY]" if col['is_array'] else ""
            lines.append(f"  {col['name']}{array_marker}")
        
        if len(results['suggested_columns']) > 20:
            lines.append(f"  ... and {len(results['suggested_columns']) - 20} more columns")
        
        return "\n".join(lines)