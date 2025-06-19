"""
DBF (dBase) database file reader with table discovery.
Supports various DBF formats and memo files.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import pandas as pd
import struct
from datetime import datetime, date

from ..detectors.database_detector import DatabaseInfo, DatabaseType


@dataclass
class DBFFieldInfo:
    """Information about a DBF field"""
    name: str
    type: str  # C=Character, N=Numeric, L=Logical, D=Date, M=Memo, etc.
    length: int
    decimal_places: int
    position: int


@dataclass
class DBFTableInfo:
    """Information about a DBF table (file)"""
    name: str
    file_path: Path
    record_count: int
    field_count: int
    last_update: Optional[date]
    version: str
    encoding: str
    has_memo: bool
    memo_file_path: Optional[Path]
    fields: List[DBFFieldInfo]
    estimated_size: int


class DBFTableDiscovery:
    """
    Discovers and analyzes DBF database files.
    DBF files are single-table databases, so discovery finds the table structure.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.table_info: Optional[DBFTableInfo] = None
        self._dbf_file = None
        
        # DBF version signatures
        self.version_map = {
            0x02: 'FoxBASE',
            0x03: 'FoxBASE+/dBASE III PLUS, no memo',
            0x04: 'dBASE IV w/o memo',
            0x05: 'dBASE V w/o memo',
            0x30: 'Visual FoxPro',
            0x31: 'Visual FoxPro, autoincrement',
            0x32: 'Visual FoxPro with field type Varchar',
            0x43: 'dBASE IV SQL table files, no memo',
            0x63: 'dBASE IV SQL system files, no memo',
            0x83: 'FoxBASE+/dBASE III PLUS, with memo',
            0x8B: 'dBASE IV with memo',
            0x8E: 'dBASE IV with SQL table',
            0xCB: 'dBASE IV SQL table files, with memo',
            0xF5: 'FoxPro 2.x (or earlier) with memo',
            0xFB: 'FoxPro without memo',
        }
        
        # Field type descriptions
        self.field_types = {
            'C': 'Character',
            'N': 'Numeric',
            'L': 'Logical',
            'D': 'Date',
            'M': 'Memo',
            'F': 'Float',
            'B': 'Binary',
            'G': 'General',
            'P': 'Picture',
            'Y': 'Currency',
            'T': 'DateTime',
            'I': 'Integer',
            'V': 'Varchar',
            'X': 'Varchar Binary',
            '@': 'Timestamp',
            'O': 'Double',
            '+': 'Autoincrement'
        }
    
    def connect(self, file_path: Union[str, Path]) -> bool:
        """
        Connect to DBF file and analyze structure.
        
        Args:
            file_path: Path to DBF file
            
        Returns:
            True if connection successful
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"DBF file not found: {file_path}")
        
        if file_path.suffix.lower() != '.dbf':
            raise ValueError(f"File is not a DBF file: {file_path}")
        
        self.logger.info(f"Analyzing DBF file: {file_path}")
        
        try:
            # Try dbfread library first
            from dbfread import DBF
            
            # Attempt to open with encoding detection
            self._dbf_file = self._open_with_encoding_detection(file_path)
            
            # Analyze the file structure
            self.table_info = self._analyze_dbf_structure(file_path)
            
            self.logger.info(f"✓ Connected to DBF: {self.table_info.record_count} records, {self.table_info.field_count} fields")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to DBF file: {e}")
            raise ConnectionError(f"Cannot open DBF file: {e}")
    
    def _open_with_encoding_detection(self, file_path: Path):
        """Open DBF file with automatic encoding detection"""
        from dbfread import DBF
        
        # Common DBF encodings to try, prioritizing Windows encodings for business data
        encodings = ['cp1252', 'iso-8859-1', 'latin1', 'cp850', 'utf-8', 'ascii']
        
        for encoding in encodings:
            try:
                dbf = DBF(str(file_path), encoding=encoding)
                # Test by reading field names and first few records
                _ = dbf.field_names
                # Test reading first record to ensure data is readable
                test_count = 0
                for record in dbf:
                    test_count += 1
                    if test_count >= 3:  # Test first 3 records
                        break
                self.logger.debug(f"Successfully opened DBF with encoding: {encoding}")
                return DBF(str(file_path), encoding=encoding)  # Return fresh instance
            except (UnicodeDecodeError, UnicodeError) as e:
                self.logger.debug(f"Unicode error with encoding {encoding}: {e}")
                continue
            except Exception as e:
                self.logger.debug(f"Failed to open with encoding {encoding}: {e}")
                continue
        
        # Fallback: try without encoding
        try:
            dbf = DBF(str(file_path))
            self.logger.warning("Opened DBF without explicit encoding")
            return dbf
        except Exception as e:
            raise ConnectionError(f"Could not open DBF with any encoding: {e}")
    
    def _analyze_dbf_structure(self, file_path: Path) -> DBFTableInfo:
        """Analyze DBF file structure by reading header"""
        
        # Read DBF header directly for detailed info
        with open(file_path, 'rb') as f:
            header = f.read(32)
            
            if len(header) < 32:
                raise ValueError("Invalid DBF file: header too short")
            
            # Parse header
            version_byte = header[0]
            version = self.version_map.get(version_byte, f"Unknown (0x{version_byte:02X})")
            
            # Last update date
            last_update = None
            year, month, day = struct.unpack('<3B', header[1:4])
            if year > 0 and month > 0 and day > 0:
                try:
                    # Y2K handling
                    full_year = 1900 + year if year >= 80 else 2000 + year
                    last_update = date(full_year, month, day)
                except ValueError:
                    pass  # Invalid date
            
            # Record info
            record_count = struct.unpack('<L', header[4:8])[0]
            header_length = struct.unpack('<H', header[8:10])[0]
            record_length = struct.unpack('<H', header[10:12])[0]
            
            # Calculate field count
            field_count = (header_length - 33) // 32  # 32 bytes per field descriptor + 1 byte terminator
            
        # Get field information from dbfread
        fields = []
        for i, field in enumerate(self._dbf_file.fields):
            fields.append(DBFFieldInfo(
                name=field.name,
                type=field.type,
                length=field.length,
                decimal_places=getattr(field, 'decimal_count', 0),
                position=i + 1
            ))
        
        # Check for memo file
        has_memo = any(field.type == 'M' for field in fields)
        memo_file_path = None
        
        if has_memo:
            # Look for memo files (.dbt, .fpt)
            for ext in ['.dbt', '.fpt', '.DBT', '.FPT']:
                memo_path = file_path.with_suffix(ext)
                if memo_path.exists():
                    memo_file_path = memo_path
                    break
        
        # Estimate encoding
        encoding = getattr(self._dbf_file, 'encoding', 'cp850') or 'cp850'
        
        # Calculate file size
        estimated_size = file_path.stat().st_size
        
        return DBFTableInfo(
            name=file_path.stem,
            file_path=file_path,
            record_count=record_count,
            field_count=len(fields),
            last_update=last_update,
            version=version,
            encoding=encoding,
            has_memo=has_memo,
            memo_file_path=memo_file_path,
            fields=fields,
            estimated_size=estimated_size
        )
    
    def list_tables(self) -> List[str]:
        """
        List tables in DBF file.
        DBF files contain only one table, so returns the file name.
        
        Returns:
            List with single table name
        """
        if not self.table_info:
            raise ConnectionError("Not connected to DBF file")
        
        return [self.table_info.name]
    
    def get_table_info(self, table_name: Optional[str] = None) -> DBFTableInfo:
        """
        Get detailed information about the table.
        
        Args:
            table_name: Ignored for DBF (single table)
            
        Returns:
            DBFTableInfo object
        """
        if not self.table_info:
            raise ConnectionError("Not connected to DBF file")
        
        return self.table_info
    
    def read_table(self, table_name: Optional[str] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Read table data as DataFrame.
        
        Args:
            table_name: Ignored for DBF (single table)
            limit: Optional limit on number of records
            
        Returns:
            DataFrame with table data
        """
        if not self.table_info:
            raise ConnectionError("Not connected to DBF file")
        
        try:
            # Re-open the DBF file for reading data
            dbf_file = self._open_with_encoding_detection(self.table_info.file_path)
            
            # Read records with error handling
            records = []
            error_count = 0
            for i, record in enumerate(dbf_file):
                if limit and i >= limit:
                    break
                try:
                    # Ensure all values are handled properly
                    clean_record = {}
                    for key, value in record.items():
                        if isinstance(value, str):
                            # Handle potential encoding issues in string values
                            clean_record[key] = value
                        else:
                            clean_record[key] = value
                    records.append(clean_record)
                except (UnicodeDecodeError, UnicodeError) as ue:
                    error_count += 1
                    self.logger.warning(f"Unicode error in record {i}: {ue}")
                    # Skip problematic records or try to clean them
                    if error_count > 100:  # Too many errors
                        raise ue
                    continue
                except Exception as re:
                    error_count += 1
                    self.logger.warning(f"Error in record {i}: {re}")
                    if error_count > 100:  # Too many errors
                        raise re
                    continue
            
            if not records:
                raise ValueError("No readable records found in DBF file")
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            if error_count > 0:
                self.logger.warning(f"Skipped {error_count} problematic records due to encoding issues")
            
            self.logger.debug(f"Read {len(df)} records from DBF file")
            return df
            
        except Exception as e:
            self.logger.error(f"Error reading DBF data: {e}")
            raise
    
    def get_field_sample(self, field_name: str, sample_size: int = 10) -> List[Any]:
        """
        Get sample values from a specific field.
        
        Args:
            field_name: Name of the field
            sample_size: Number of sample values
            
        Returns:
            List of sample values
        """
        if not self._dbf_file:
            raise ConnectionError("Not connected to DBF file")
        
        samples = []
        for i, record in enumerate(self._dbf_file):
            if i >= sample_size:
                break
            
            if field_name in record:
                samples.append(record[field_name])
            else:
                break
        
        return samples
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Get comprehensive DBF file summary"""
        if not self.table_info:
            raise ConnectionError("Not connected to DBF file")
        
        # Get field details
        fields_info = []
        for field in self.table_info.fields:
            field_info = {
                'name': field.name,
                'type': field.type,
                'type_description': self.field_types.get(field.type, 'Unknown'),
                'length': field.length,
                'decimal_places': field.decimal_places,
                'position': field.position
            }
            
            # Get sample values for the field
            try:
                samples = self.get_field_sample(field.name, 3)
                field_info['sample_values'] = samples
            except:
                field_info['sample_values'] = []
            
            fields_info.append(field_info)
        
        return {
            'file_path': str(self.table_info.file_path),
            'table_name': self.table_info.name,
            'version': self.table_info.version,
            'record_count': self.table_info.record_count,
            'field_count': self.table_info.field_count,
            'last_update': self.table_info.last_update.isoformat() if self.table_info.last_update else None,
            'encoding': self.table_info.encoding,
            'has_memo': self.table_info.has_memo,
            'memo_file': str(self.table_info.memo_file_path) if self.table_info.memo_file_path else None,
            'estimated_size': self.table_info.estimated_size,
            'fields': fields_info
        }
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate DBF data integrity and report issues"""
        if not self._dbf_file:
            raise ConnectionError("Not connected to DBF file")
        
        issues = []
        field_stats = {}
        
        # Check each field
        for field in self.table_info.fields:
            stats = {
                'null_count': 0,
                'unique_count': 0,
                'sample_values': [],
                'has_issues': False
            }
            
            values = set()
            
            try:
                # Sample first 100 records for analysis
                for i, record in enumerate(self._dbf_file):
                    if i >= 100:
                        break
                    
                    value = record.get(field.name)
                    
                    if value is None or value == '':
                        stats['null_count'] += 1
                    else:
                        values.add(str(value)[:50])  # Truncate long values
                    
                    if len(stats['sample_values']) < 5:
                        stats['sample_values'].append(value)
                
                stats['unique_count'] = len(values)
                
                # Check for potential issues
                if field.type == 'D':  # Date field
                    # Check for invalid dates
                    for sample in stats['sample_values']:
                        if sample and not isinstance(sample, (date, datetime)):
                            try:
                                datetime.strptime(str(sample), '%Y%m%d')
                            except ValueError:
                                stats['has_issues'] = True
                                issues.append(f"Invalid date format in field {field.name}: {sample}")
                
            except Exception as e:
                stats['has_issues'] = True
                issues.append(f"Error analyzing field {field.name}: {e}")
            
            field_stats[field.name] = stats
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'field_statistics': field_stats
        }
    
    def close(self):
        """Close DBF file"""
        self._dbf_file = None
        self.table_info = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience functions
def discover_dbf_table(file_path: Union[str, Path]) -> str:
    """
    Discover table in DBF file (returns file name).
    
    Args:
        file_path: Path to DBF file
        
    Returns:
        Table name (file stem)
    """
    with DBFTableDiscovery() as discovery:
        discovery.connect(file_path)
        return discovery.list_tables()[0]


def get_dbf_summary(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get comprehensive DBF file summary.
    
    Args:
        file_path: Path to DBF file
        
    Returns:
        Database summary dictionary
    """
    with DBFTableDiscovery() as discovery:
        discovery.connect(file_path)
        return discovery.get_database_summary()


def validate_dbf_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Validate DBF file integrity.
    
    Args:
        file_path: Path to DBF file
        
    Returns:
        Validation results dictionary
    """
    with DBFTableDiscovery() as discovery:
        discovery.connect(file_path)
        return discovery.validate_data_integrity()