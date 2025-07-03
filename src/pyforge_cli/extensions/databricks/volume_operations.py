"""
Unity Catalog Volume Operations Module

This module provides operations for working with Unity Catalog Volumes in Databricks,
including path validation, file operations, and metadata retrieval.
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VolumeInfo:
    """Information about a Unity Catalog Volume."""
    catalog: str
    schema: str
    volume: str
    path: str
    exists: bool = False
    is_managed: Optional[bool] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    size_bytes: Optional[int] = None
    file_count: Optional[int] = None


@dataclass
class VolumeFile:
    """Information about a file in a Volume."""
    path: str
    name: str
    size: int
    modified_time: datetime
    is_directory: bool
    extension: Optional[str] = None


class VolumeOperations:
    """
    Handles Unity Catalog Volume operations.
    
    Provides methods for validating Volume paths, listing contents,
    checking permissions, and performing file operations.
    """
    
    # Volume path pattern: /Volumes/catalog/schema/volume/path
    VOLUME_PATH_PATTERN = re.compile(
        r'^/Volumes/([^/]+)/([^/]+)/([^/]+)(?:/(.*))?$',
        re.IGNORECASE
    )
    
    def __init__(self):
        """Initialize Volume operations handler."""
        self.logger = logging.getLogger("pyforge.extensions.databricks.volumes")
        self._spark = None
        self._dbutils = None
        
    def parse_volume_path(self, path: str) -> Optional[VolumeInfo]:
        """
        Parse a Unity Catalog Volume path.
        
        Args:
            path: Path to parse (e.g., /Volumes/main/default/my_volume/data.csv)
            
        Returns:
            Optional[VolumeInfo]: Parsed volume information or None if invalid
        """
        # Normalize path
        path = str(path).strip()
        if not path.startswith("/Volumes"):
            # Try to fix common mistakes
            if path.startswith("Volumes/"):
                path = "/" + path
            elif path.startswith("volumes/"):
                path = "/V" + path[1:]
            else:
                return None
        
        match = self.VOLUME_PATH_PATTERN.match(path)
        if not match:
            self.logger.warning(f"Invalid Volume path format: {path}")
            return None
        
        catalog = match.group(1)
        schema = match.group(2)
        volume = match.group(3)
        file_path = match.group(4) or ""
        
        return VolumeInfo(
            catalog=catalog,
            schema=schema,
            volume=volume,
            path=file_path
        )
    
    def validate_volume_access(self, volume_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate access to a Unity Catalog Volume.
        
        Args:
            volume_path: Volume path to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        volume_info = self.parse_volume_path(volume_path)
        if not volume_info:
            return False, f"Invalid Volume path format: {volume_path}"
        
        try:
            # Get Spark session
            spark = self._get_spark_session()
            if not spark:
                return False, "Spark session not available"
            
            # Check if catalog exists
            try:
                catalogs = [row.catalog for row in spark.sql("SHOW CATALOGS").collect()]
                if volume_info.catalog not in catalogs:
                    return False, f"Catalog '{volume_info.catalog}' not found"
            except Exception as e:
                return False, f"Cannot list catalogs: {str(e)}"
            
            # Check if schema exists
            try:
                spark.sql(f"USE CATALOG `{volume_info.catalog}`")
                schemas = [row.schema for row in spark.sql("SHOW SCHEMAS").collect()]
                if volume_info.schema not in schemas:
                    return False, f"Schema '{volume_info.schema}' not found in catalog '{volume_info.catalog}'"
            except Exception as e:
                return False, f"Cannot access schema: {str(e)}"
            
            # Check if volume exists
            try:
                spark.sql(f"USE SCHEMA `{volume_info.schema}`")
                volumes = spark.sql("SHOW VOLUMES").collect()
                volume_names = [row.volume_name for row in volumes]
                if volume_info.volume not in volume_names:
                    return False, f"Volume '{volume_info.volume}' not found"
            except Exception as e:
                return False, f"Cannot list volumes: {str(e)}"
            
            # Try to access the volume path
            full_path = self._construct_volume_path(volume_info)
            if os.path.exists(full_path):
                if os.access(full_path, os.R_OK):
                    return True, None
                else:
                    return False, f"No read permission for volume: {full_path}"
            else:
                # Volume exists in catalog but path might be empty
                return True, None
                
        except Exception as e:
            return False, f"Error validating volume access: {str(e)}"
    
    def list_volume_contents(
        self, 
        volume_path: str, 
        recursive: bool = False,
        pattern: Optional[str] = None
    ) -> List[VolumeFile]:
        """
        List contents of a Volume.
        
        Args:
            volume_path: Volume path to list
            recursive: List recursively
            pattern: File pattern to match (e.g., "*.csv")
            
        Returns:
            List[VolumeFile]: List of files/directories in the volume
        """
        volume_info = self.parse_volume_path(volume_path)
        if not volume_info:
            self.logger.error(f"Invalid volume path: {volume_path}")
            return []
        
        try:
            dbutils = self._get_dbutils()
            if dbutils:
                # Use dbutils for listing (preferred method)
                return self._list_with_dbutils(volume_path, recursive, pattern)
            else:
                # Fallback to OS-based listing
                return self._list_with_os(volume_path, recursive, pattern)
                
        except Exception as e:
            self.logger.error(f"Error listing volume contents: {e}")
            return []
    
    def get_volume_metadata(self, volume_path: str) -> Optional[VolumeInfo]:
        """
        Get metadata for a Volume.
        
        Args:
            volume_path: Volume path
            
        Returns:
            Optional[VolumeInfo]: Volume metadata or None
        """
        volume_info = self.parse_volume_path(volume_path)
        if not volume_info:
            return None
        
        try:
            spark = self._get_spark_session()
            if not spark:
                return None
            
            # Get volume details from catalog
            volume_details = spark.sql(f"""
                DESCRIBE VOLUME `{volume_info.catalog}`.`{volume_info.schema}`.`{volume_info.volume}`
            """).collect()
            
            # Parse volume properties
            properties = {row['info_name']: row['info_value'] for row in volume_details}
            
            # Update volume info
            volume_info.exists = True
            volume_info.is_managed = properties.get('Is_managed', '').lower() == 'true'
            
            # Get creation time if available
            created = properties.get('Created Time')
            if created:
                try:
                    volume_info.created_at = datetime.fromisoformat(created)
                except:
                    pass
            
            # Get volume statistics
            stats = self._get_volume_statistics(volume_path)
            if stats:
                volume_info.size_bytes = stats.get('total_size')
                volume_info.file_count = stats.get('file_count')
                volume_info.modified_at = stats.get('last_modified')
            
            return volume_info
            
        except Exception as e:
            self.logger.error(f"Error getting volume metadata: {e}")
            return None
    
    def create_volume_directory(self, volume_path: str) -> bool:
        """
        Create a directory in a Volume.
        
        Args:
            volume_path: Directory path to create
            
        Returns:
            bool: True if successful
        """
        try:
            dbutils = self._get_dbutils()
            if dbutils:
                dbutils.fs.mkdirs(volume_path)
                return True
            else:
                # Fallback to OS
                os.makedirs(volume_path, exist_ok=True)
                return True
                
        except Exception as e:
            self.logger.error(f"Error creating directory: {e}")
            return False
    
    def copy_to_volume(
        self, 
        source_path: str, 
        volume_path: str,
        overwrite: bool = False
    ) -> bool:
        """
        Copy a file to a Volume.
        
        Args:
            source_path: Source file path
            volume_path: Destination volume path
            overwrite: Whether to overwrite existing files
            
        Returns:
            bool: True if successful
        """
        try:
            dbutils = self._get_dbutils()
            if dbutils:
                # Check if destination exists
                if not overwrite:
                    try:
                        dbutils.fs.ls(volume_path)
                        self.logger.error(f"Destination already exists: {volume_path}")
                        return False
                    except:
                        pass  # File doesn't exist, proceed
                
                # Copy file
                dbutils.fs.cp(source_path, volume_path, recurse=True)
                return True
            else:
                # Fallback to standard copy
                import shutil
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, volume_path, dirs_exist_ok=overwrite)
                else:
                    shutil.copy2(source_path, volume_path)
                return True
                
        except Exception as e:
            self.logger.error(f"Error copying to volume: {e}")
            return False
    
    def delete_from_volume(self, volume_path: str, recursive: bool = False) -> bool:
        """
        Delete a file or directory from a Volume.
        
        Args:
            volume_path: Path to delete
            recursive: Delete recursively for directories
            
        Returns:
            bool: True if successful
        """
        try:
            dbutils = self._get_dbutils()
            if dbutils:
                dbutils.fs.rm(volume_path, recurse=recursive)
                return True
            else:
                # Fallback to OS
                if os.path.isdir(volume_path):
                    if recursive:
                        import shutil
                        shutil.rmtree(volume_path)
                    else:
                        os.rmdir(volume_path)
                else:
                    os.remove(volume_path)
                return True
                
        except Exception as e:
            self.logger.error(f"Error deleting from volume: {e}")
            return False
    
    def get_file_info(self, volume_path: str) -> Optional[VolumeFile]:
        """
        Get information about a specific file in a Volume.
        
        Args:
            volume_path: File path
            
        Returns:
            Optional[VolumeFile]: File information or None
        """
        try:
            dbutils = self._get_dbutils()
            if dbutils:
                file_info = dbutils.fs.ls(volume_path)[0]
                return VolumeFile(
                    path=file_info.path,
                    name=file_info.name,
                    size=file_info.size,
                    modified_time=datetime.fromtimestamp(file_info.modificationTime / 1000),
                    is_directory=file_info.isDir(),
                    extension=Path(file_info.name).suffix if not file_info.isDir() else None
                )
            else:
                # Fallback to OS
                stat = os.stat(volume_path)
                path_obj = Path(volume_path)
                return VolumeFile(
                    path=str(path_obj),
                    name=path_obj.name,
                    size=stat.st_size,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                    is_directory=path_obj.is_dir(),
                    extension=path_obj.suffix if path_obj.is_file() else None
                )
                
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return None
    
    # Private helper methods
    
    def _get_spark_session(self):
        """Get or create Spark session."""
        if self._spark is None:
            try:
                from pyspark.sql import SparkSession
                self._spark = SparkSession.builder.getOrCreate()
            except Exception as e:
                self.logger.warning(f"Could not get Spark session: {e}")
        return self._spark
    
    def _get_dbutils(self):
        """Get dbutils if available."""
        if self._dbutils is None:
            try:
                from pyspark.dbutils import DBUtils
                spark = self._get_spark_session()
                if spark:
                    self._dbutils = DBUtils(spark)
            except Exception:
                # Try alternative method
                try:
                    import IPython
                    self._dbutils = IPython.get_ipython().user_ns.get("dbutils")
                except Exception:
                    self.logger.debug("dbutils not available")
        return self._dbutils
    
    def _construct_volume_path(self, volume_info: VolumeInfo) -> str:
        """Construct full volume path."""
        base = f"/Volumes/{volume_info.catalog}/{volume_info.schema}/{volume_info.volume}"
        if volume_info.path:
            return f"{base}/{volume_info.path}"
        return base
    
    def _list_with_dbutils(
        self, 
        path: str, 
        recursive: bool, 
        pattern: Optional[str]
    ) -> List[VolumeFile]:
        """List files using dbutils."""
        dbutils = self._get_dbutils()
        files = []
        
        try:
            if recursive:
                # Recursive listing
                def _recursive_list(current_path):
                    items = dbutils.fs.ls(current_path)
                    for item in items:
                        if item.isDir():
                            _recursive_list(item.path)
                        else:
                            files.append(VolumeFile(
                                path=item.path,
                                name=item.name,
                                size=item.size,
                                modified_time=datetime.fromtimestamp(item.modificationTime / 1000),
                                is_directory=False,
                                extension=Path(item.name).suffix
                            ))
                
                _recursive_list(path)
            else:
                # Non-recursive listing
                items = dbutils.fs.ls(path)
                for item in items:
                    files.append(VolumeFile(
                        path=item.path,
                        name=item.name,
                        size=item.size,
                        modified_time=datetime.fromtimestamp(item.modificationTime / 1000),
                        is_directory=item.isDir(),
                        extension=Path(item.name).suffix if not item.isDir() else None
                    ))
            
            # Apply pattern filter if specified
            if pattern:
                import fnmatch
                files = [f for f in files if fnmatch.fnmatch(f.name, pattern)]
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing with dbutils: {e}")
            return []
    
    def _list_with_os(
        self, 
        path: str, 
        recursive: bool, 
        pattern: Optional[str]
    ) -> List[VolumeFile]:
        """List files using OS methods."""
        files = []
        
        try:
            if recursive:
                for root, dirs, filenames in os.walk(path):
                    for name in filenames:
                        full_path = os.path.join(root, name)
                        stat = os.stat(full_path)
                        files.append(VolumeFile(
                            path=full_path,
                            name=name,
                            size=stat.st_size,
                            modified_time=datetime.fromtimestamp(stat.st_mtime),
                            is_directory=False,
                            extension=Path(name).suffix
                        ))
                    for name in dirs:
                        full_path = os.path.join(root, name)
                        stat = os.stat(full_path)
                        files.append(VolumeFile(
                            path=full_path,
                            name=name,
                            size=stat.st_size,
                            modified_time=datetime.fromtimestamp(stat.st_mtime),
                            is_directory=True,
                            extension=None
                        ))
            else:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    stat = os.stat(full_path)
                    files.append(VolumeFile(
                        path=full_path,
                        name=item,
                        size=stat.st_size,
                        modified_time=datetime.fromtimestamp(stat.st_mtime),
                        is_directory=os.path.isdir(full_path),
                        extension=Path(item).suffix if os.path.isfile(full_path) else None
                    ))
            
            # Apply pattern filter
            if pattern:
                import fnmatch
                files = [f for f in files if fnmatch.fnmatch(f.name, pattern)]
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing with OS: {e}")
            return []
    
    def _get_volume_statistics(self, volume_path: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a volume."""
        try:
            files = self.list_volume_contents(volume_path, recursive=True)
            
            if not files:
                return {
                    'total_size': 0,
                    'file_count': 0,
                    'directory_count': 0,
                    'last_modified': None
                }
            
            total_size = sum(f.size for f in files if not f.is_directory)
            file_count = sum(1 for f in files if not f.is_directory)
            dir_count = sum(1 for f in files if f.is_directory)
            last_modified = max(f.modified_time for f in files) if files else None
            
            return {
                'total_size': total_size,
                'file_count': file_count,
                'directory_count': dir_count,
                'last_modified': last_modified
            }
            
        except Exception as e:
            self.logger.error(f"Error getting volume statistics: {e}")
            return None