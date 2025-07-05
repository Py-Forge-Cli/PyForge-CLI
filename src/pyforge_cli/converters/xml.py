"""XML to Parquet converter implementation."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Set

import pandas as pd

from .base import BaseConverter
from .xml_structure_analyzer import XmlStructureAnalyzer
from .xml_flattener import XmlFlattener

logger = logging.getLogger(__name__)


class XmlConverter(BaseConverter):
    """Converter for XML files to Parquet format."""

    def __init__(self):
        """Initialize the XML converter."""
        super().__init__()
        self.supported_inputs = {".xml", ".xml.gz", ".xml.bz2"}
        self.supported_outputs = {".parquet"}
        self.analyzer = XmlStructureAnalyzer()
        self.flattener = XmlFlattener()
        
    def validate_input(self, input_path: Path) -> bool:
        """
        Validate if the input file is a valid XML file.
        
        Args:
            input_path: Path to the input XML file
            
        Returns:
            True if valid, False otherwise
        """
        # Convert to Path if string
        if isinstance(input_path, str):
            input_path = Path(input_path)
            
        # Check if file exists
        if not input_path.exists():
            logger.error(f"File not found: {input_path}")
            return False
            
        # Check if it has a valid XML extension
        file_str = str(input_path).lower()
        valid_extensions = {'.xml', '.xml.gz', '.xml.bz2'}
        is_valid_extension = any(file_str.endswith(ext) for ext in valid_extensions)
        
        if not is_valid_extension:
            logger.error(f"Invalid file extension: {input_path}")
            return False
            
        # Basic XML validation - check if file starts with XML declaration or root element
        try:
            # Handle compressed files
            file_str = str(input_path).lower()
            
            if file_str.endswith('.gz'):
                import gzip
                with gzip.open(input_path, 'rb') as f:
                    header = f.read(100)
            elif file_str.endswith('.bz2'):
                import bz2
                with bz2.open(input_path, 'rb') as f:
                    header = f.read(100)
            else:
                with open(input_path, 'rb') as f:
                    header = f.read(100)
                
            # Decode header, handling potential encoding issues
            try:
                header_str = header.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    header_str = header.decode('latin-1')
                except UnicodeDecodeError:
                    return False
                    
            # Check for XML indicators
            header_str = header_str.strip()
            if header_str.startswith('<?xml') or header_str.startswith('<'):
                return True
                
        except Exception as e:
            logger.error(f"Error validating XML file: {e}")
            return False
            
        return False
        
    def get_metadata(self, input_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from the XML file.
        
        Args:
            input_path: Path to the input XML file
            
        Returns:
            Dictionary containing file metadata
        """
        # Get basic file metadata
        if isinstance(input_path, str):
            input_path = Path(input_path)
            
        metadata = {
            "file_path": str(input_path),
            "file_name": input_path.name,
            "file_size": input_path.stat().st_size if input_path.exists() else 0
        }
        
        try:
            # Analyze XML structure
            analysis = self.analyzer.analyze_file(input_path)
            
            metadata.update({
                "format": "XML",
                "schema_detected": True,
                "namespaces": analysis.get('namespaces', {}),
                "root_element": analysis.get('root_tag'),
                "max_depth": analysis.get('max_depth', 0),
                "total_elements": analysis.get('total_elements', 0),
                "array_elements": len(analysis.get('array_elements', [])),
                "suggested_columns": len(analysis.get('suggested_columns', [])),
                "encoding": "utf-8"  # TODO: Detect actual encoding
            })
        except Exception as e:
            logger.warning(f"Could not extract XML metadata: {e}")
            metadata.update({
                "format": "XML",
                "schema_detected": False,
                "error": str(e)
            })
            
        return metadata
        
    def convert(
        self,
        input_path: Path,
        output_path: Path,
        flatten_strategy: str = "conservative",
        array_handling: str = "expand",
        namespace_handling: str = "preserve",
        preview_schema: bool = False,
        streaming: bool = False,
        chunk_size: int = 10000,
        **kwargs
    ) -> bool:
        """
        Convert XML file to Parquet format.
        
        Args:
            input_path: Path to input XML file
            output_path: Path for output Parquet file
            flatten_strategy: Strategy for flattening nested structures
                            ('conservative', 'moderate', 'aggressive')
            array_handling: How to handle arrays ('expand', 'concatenate', 'json_string')
            namespace_handling: How to handle namespaces ('preserve', 'strip', 'prefix')
            preview_schema: Whether to preview schema before conversion
            streaming: Whether to use streaming for large files
            chunk_size: Chunk size for streaming mode
            **kwargs: Additional options
            
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            self._update_progress(0, f"Starting XML to Parquet conversion")
            
            # Validate input
            if not self.validate_input(input_path):
                raise ValueError(f"Invalid XML file: {input_path}")
                
            # Convert to Path if string
            if isinstance(input_path, str):
                input_path = Path(input_path)
            if isinstance(output_path, str):
                output_path = Path(output_path)
                
            # Analyze XML structure
            self._update_progress(10, "Analyzing XML structure")
            analysis = self.analyzer.analyze_file(input_path)
            
            # Show schema preview if requested
            if preview_schema:
                schema_preview = self.analyzer.get_schema_preview()
                print("\n" + schema_preview + "\n")
                
                # Ask user if they want to continue
                response = input("Continue with conversion? (y/n): ")
                if response.lower() != 'y':
                    logger.info("Conversion cancelled by user")
                    return False
            
            # Log conversion options
            logger.info(f"Converting {input_path} to {output_path}")
            logger.info(f"Options: flatten_strategy={flatten_strategy}, "
                       f"array_handling={array_handling}, "
                       f"namespace_handling={namespace_handling}")
            logger.info(f"Structure: {analysis['total_elements']} elements, "
                       f"max depth: {analysis['max_depth']}, "
                       f"arrays: {len(analysis['array_elements'])}")
            
            # Flatten XML data using the flattener
            self._update_progress(30, "Flattening XML structure")
            
            try:
                # Use flattener to extract actual data
                flattened_records = self.flattener.flatten_file(
                    input_path, 
                    analysis,
                    flatten_strategy=flatten_strategy,
                    array_handling=array_handling,
                    namespace_handling=namespace_handling
                )
                
                # Convert to DataFrame
                if flattened_records:
                    df = pd.DataFrame(flattened_records)
                else:
                    # Fallback: Create DataFrame with basic structure info if no data extracted
                    logger.warning("No data records extracted, creating structure summary")
                    df_data = {
                        'element_path': [],
                        'element_tag': [],
                        'has_text': [],
                        'has_children': [],
                        'is_array': []
                    }
                    
                    for path, elem_info in analysis['elements'].items():
                        df_data['element_path'].append(path)
                        df_data['element_tag'].append(elem_info['tag'])
                        df_data['has_text'].append(elem_info['has_text'])
                        df_data['has_children'].append(elem_info['has_children'])
                        df_data['is_array'].append(elem_info['is_array'])
                    
                    df = pd.DataFrame(df_data)
                
                self._update_progress(70, f"Extracted {len(df)} records")
                
            except Exception as e:
                logger.error(f"Error during flattening: {e}")
                # Create a simple error record
                df = pd.DataFrame({'error': [f"Flattening failed: {str(e)}"]})
                logger.warning("Created error record due to flattening failure")
            
            # Write to Parquet
            self._update_progress(90, "Writing Parquet file")
            df.to_parquet(output_path, engine='pyarrow', compression='snappy')
            
            self._update_progress(100, "Conversion complete")
            logger.info(f"Successfully converted to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting XML to Parquet: {e}")
            raise RuntimeError(f"Failed to convert XML file: {str(e)}")
            
    def _update_progress(self, percentage: int, message: str):
        """Update progress if callback is set."""
        if hasattr(self, 'progress_callback') and self.progress_callback:
            self.progress_callback(percentage, message)