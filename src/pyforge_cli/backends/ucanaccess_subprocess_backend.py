"""UCanAccess subprocess backend for Databricks Serverless compatibility.

This backend runs UCanAccess via Java subprocess instead of JPype,
making it compatible with restricted environments like Databricks Serverless.
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional
import pandas as pd

from .base import DatabaseBackend
from .jar_manager import UCanAccessJARManager


class UCanAccessSubprocessBackend(DatabaseBackend):
    """UCanAccess backend using subprocess for Databricks Serverless compatibility."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.jar_manager = UCanAccessJARManager()
        self.db_path = None
        self._temp_file_path = None
        self._tables_cache = None
    
    def is_available(self) -> bool:
        """Check if subprocess UCanAccess backend is available.
        
        This should work in Databricks Serverless since it uses subprocess.
        
        Returns:
            True if Java is available via subprocess, False otherwise
        """
        try:
            # Check Java runtime via subprocess
            if not self._check_java_subprocess():
                self.logger.debug("Java runtime not available via subprocess")
                return False
            
            # Check/download UCanAccess JAR
            if not self.jar_manager.ensure_jar_available():
                self.logger.debug("UCanAccess JAR not available")
                return False
            
            self.logger.info("UCanAccess subprocess backend is available")
            return True
            
        except Exception as e:
            self.logger.debug(f"UCanAccess subprocess availability check failed: {e}")
            return False
    
    def connect(self, db_path: str, password: str = None) -> bool:
        """Connect to Access database (prepare for subprocess operations).
        
        Args:
            db_path: Path to Access database file
            password: Optional password (not supported in subprocess mode)
            
        Returns:
            True if file is accessible, False otherwise
        """
        try:
            if password:
                self.logger.warning("Password-protected databases not supported in subprocess mode")
                return False
            
            # Handle Databricks Unity Catalog volume paths
            if db_path.startswith("/Volumes/"):
                self.logger.info(f"Detected Unity Catalog volume path: {db_path}")
                
                # Copy to local storage for Java access
                import tempfile
                temp_dir = tempfile.gettempdir()
                file_name = os.path.basename(db_path)
                local_path = os.path.join(temp_dir, f"pyforge_{os.getpid()}_{file_name}")
                
                try:
                    # Copy from volume to local storage
                    copy_cmd = f"cp '{db_path}' '{local_path}'"
                    result = subprocess.run(copy_cmd, shell=True, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        self.logger.error(f"Failed to copy file from volume: {result.stderr}")
                        return False
                    
                    self.db_path = local_path
                    self._temp_file_path = local_path
                    self.logger.info(f"Successfully copied volume file to local storage: {local_path}")
                    
                except Exception as e:
                    self.logger.error(f"Error copying file from volume: {e}")
                    return False
            else:
                self.db_path = os.path.abspath(db_path)
                self._temp_file_path = None
            
            # Verify file exists
            if not os.path.exists(self.db_path):
                self.logger.error(f"Database file not found: {self.db_path}")
                return False
            
            # Test access by listing tables
            tables = self.list_tables()
            if tables is not None:
                self.logger.info(f"UCanAccess subprocess connected to: {db_path}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"UCanAccess subprocess connection failed: {e}")
            return False
    
    def list_tables(self) -> List[str]:
        """List all user tables using Java subprocess.
        
        Returns:
            List of table names, or empty list on error
        """
        if not self.db_path:
            raise RuntimeError("Not connected to database")
        
        # Use cached result if available
        if self._tables_cache is not None:
            return self._tables_cache
        
        try:
            # Create a Java program to list tables
            java_code = self._create_list_tables_java()
            
            # Run Java subprocess
            result = self._run_java_code(java_code)
            
            if result['success']:
                tables = result['tables']
                # Filter out system tables
                user_tables = [t for t in tables if not t.startswith('MSys') and not t.startswith('~')]
                self._tables_cache = sorted(user_tables)
                self.logger.info(f"Found {len(self._tables_cache)} user tables via subprocess")
                return self._tables_cache
            else:
                self.logger.error(f"Failed to list tables: {result.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error listing tables via subprocess: {e}")
            return []
    
    def read_table(self, table_name: str) -> pd.DataFrame:
        """Read table data using Java subprocess to export to CSV.
        
        Args:
            table_name: Name of table to read
            
        Returns:
            DataFrame containing table data
        """
        if not self.db_path:
            raise RuntimeError("Not connected to database")
        
        try:
            # Create a Java program to export table to CSV
            java_code = self._create_export_table_java(table_name)
            
            # Run Java subprocess
            result = self._run_java_code(java_code)
            
            if result['success'] and 'csv_file' in result:
                # Read the CSV file
                df = pd.read_csv(result['csv_file'], dtype=str, na_values=[''], keep_default_na=False)
                
                # Clean up temp file
                try:
                    os.unlink(result['csv_file'])
                except:
                    pass
                
                self.logger.debug(f"Read {len(df)} records from {table_name} via subprocess")
                return df
            else:
                error_msg = result.get('error', 'Unknown error')
                self.logger.error(f"Failed to read table {table_name}: {error_msg}")
                raise RuntimeError(f"Cannot read table {table_name}: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error reading table {table_name} via subprocess: {e}")
            raise
    
    def close(self):
        """Close connection and cleanup resources."""
        # Clean up temporary file if it exists
        if self._temp_file_path and os.path.exists(self._temp_file_path):
            try:
                os.remove(self._temp_file_path)
                self.logger.debug(f"Cleaned up temporary file: {self._temp_file_path}")
            except Exception as e:
                self.logger.warning(f"Error cleaning up temporary file: {e}")
            finally:
                self._temp_file_path = None
        
        self.db_path = None
        self._tables_cache = None
    
    def _check_java_subprocess(self) -> bool:
        """Check if Java is available via subprocess.
        
        Returns:
            True if Java can be executed, False otherwise
        """
        try:
            result = subprocess.run(
                ['java', '-version'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_info = result.stderr if result.stderr else result.stdout
                self.logger.debug(f"Java available via subprocess: {version_info.split()[0]}")
                return True
            else:
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            self.logger.debug(f"Java subprocess check failed: {e}")
            return False
    
    def _create_list_tables_java(self) -> str:
        """Create Java code to list tables using UCanAccess.
        
        Returns:
            Java source code as string
        """
        return '''
import java.sql.*;
import java.util.*;
import java.io.*;

public class ListTables {
    public static void main(String[] args) {
        String dbPath = args[0];
        String outputFile = args[1];
        
        try {
            // Load UCanAccess driver
            Class.forName("net.ucanaccess.jdbc.UcanaccessDriver");
            
            // Connect to database
            String url = "jdbc:ucanaccess://" + dbPath + ";memory=true";
            Connection conn = DriverManager.getConnection(url);
            
            // Get database metadata
            DatabaseMetaData meta = conn.getMetaData();
            ResultSet tables = meta.getTables(null, null, "%", new String[]{"TABLE"});
            
            // Collect table names
            List<String> tableList = new ArrayList<>();
            while (tables.next()) {
                String tableName = tables.getString("TABLE_NAME");
                tableList.add(tableName);
            }
            
            // Write result as JSON
            PrintWriter writer = new PrintWriter(outputFile);
            writer.println("{");
            writer.println("  \\"success\\": true,");
            writer.print("  \\"tables\\": [");
            for (int i = 0; i < tableList.size(); i++) {
                writer.print("\\"" + tableList.get(i) + "\\"");
                if (i < tableList.size() - 1) writer.print(", ");
            }
            writer.println("]");
            writer.println("}");
            writer.close();
            
            // Cleanup
            tables.close();
            conn.close();
            
        } catch (Exception e) {
            try {
                PrintWriter writer = new PrintWriter(outputFile);
                writer.println("{");
                writer.println("  \\"success\\": false,");
                writer.println("  \\"error\\": \\"" + e.getMessage().replace("\\"", "'") + "\\"");
                writer.println("}");
                writer.close();
            } catch (Exception e2) {
                e.printStackTrace();
            }
        }
    }
}
'''
    
    def _create_export_table_java(self, table_name: str) -> str:
        """Create Java code to export a table to CSV using UCanAccess.
        
        Args:
            table_name: Name of table to export
            
        Returns:
            Java source code as string
        """
        return f'''
import java.sql.*;
import java.io.*;

public class ExportTable {{
    public static void main(String[] args) {{
        String dbPath = args[0];
        String outputFile = args[1];
        String csvFile = args[2];
        
        try {{
            // Load UCanAccess driver
            Class.forName("net.ucanaccess.jdbc.UcanaccessDriver");
            
            // Connect to database
            String url = "jdbc:ucanaccess://" + dbPath + ";memory=true";
            Connection conn = DriverManager.getConnection(url);
            
            // Query the table
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM [{table_name}]");
            
            // Get metadata
            ResultSetMetaData meta = rs.getMetaData();
            int columnCount = meta.getColumnCount();
            
            // Write to CSV
            PrintWriter csv = new PrintWriter(csvFile);
            
            // Write headers
            for (int i = 1; i <= columnCount; i++) {{
                csv.print(meta.getColumnName(i));
                if (i < columnCount) csv.print(",");
            }}
            csv.println();
            
            // Write data
            while (rs.next()) {{
                for (int i = 1; i <= columnCount; i++) {{
                    String value = rs.getString(i);
                    if (value == null) value = "";
                    // Escape quotes and commas
                    if (value.contains(",") || value.contains("\\"")) {{
                        value = "\\"" + value.replace("\\"", "\\"\\"") + "\\"";
                    }}
                    csv.print(value);
                    if (i < columnCount) csv.print(",");
                }}
                csv.println();
            }}
            
            csv.close();
            rs.close();
            stmt.close();
            conn.close();
            
            // Write success result
            PrintWriter writer = new PrintWriter(outputFile);
            writer.println("{{");
            writer.println("  \\"success\\": true,");
            writer.println("  \\"csv_file\\": \\"" + csvFile.replace("\\\\", "/") + "\\"");
            writer.println("}}");
            writer.close();
            
        }} catch (Exception e) {{
            try {{
                PrintWriter writer = new PrintWriter(outputFile);
                writer.println("{{");
                writer.println("  \\"success\\": false,");
                writer.println("  \\"error\\": \\"" + e.getMessage().replace("\\"", "'").replace("\\n", " ") + "\\"");
                writer.println("}}");
                writer.close();
            }} catch (Exception e2) {{
                e.printStackTrace();
            }}
        }}
    }}
}}
'''
    
    def _run_java_code(self, java_code: str) -> dict:
        """Run Java code via subprocess with UCanAccess classpath.
        
        Args:
            java_code: Java source code to compile and run
            
        Returns:
            Dictionary with results (success, error, or data)
        """
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Determine class name from code
            import re
            class_match = re.search(r'public\s+class\s+(\w+)', java_code)
            if not class_match:
                raise RuntimeError("Could not determine Java class name")
            class_name = class_match.group(1)
            
            # Write Java source file with correct filename
            java_file = os.path.join(temp_dir, f"{class_name}.java")
            with open(java_file, 'w') as f:
                f.write(java_code)
            
            # Get all JAR paths
            jar_paths = self._get_all_jar_paths()
            classpath = ':'.join(jar_paths)  # Use : for Unix, ; for Windows
            if os.name == 'nt':
                classpath = ';'.join(jar_paths)
            
            # Compile Java code
            compile_cmd = ['javac', '-cp', classpath, java_file]
            compile_result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=temp_dir)
            
            if compile_result.returncode != 0:
                self.logger.error(f"Java compilation failed: {compile_result.stderr}")
                return {'success': False, 'error': f"Compilation failed: {compile_result.stderr}"}
            
            # Prepare output file
            output_file = os.path.join(temp_dir, 'output.json')
            
            # Prepare CSV file for table export
            csv_file = os.path.join(temp_dir, 'table_data.csv')
            
            # Run Java code
            run_cmd = ['java', '-cp', f'.{os.pathsep}{classpath}', class_name, self.db_path, output_file, csv_file]
            run_result = subprocess.run(run_cmd, capture_output=True, text=True, cwd=temp_dir, timeout=60)
            
            if run_result.returncode != 0:
                self.logger.error(f"Java execution failed: {run_result.stderr}")
                return {'success': False, 'error': f"Execution failed: {run_result.stderr}"}
            
            # Read output
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    return json.load(f)
            else:
                return {'success': False, 'error': 'No output generated'}
                
        except Exception as e:
            self.logger.error(f"Error running Java code: {e}")
            return {'success': False, 'error': str(e)}
            
        finally:
            # Cleanup temp files (except CSV which caller will handle)
            try:
                for file in os.listdir(temp_dir):
                    if not file.endswith('.csv'):
                        os.unlink(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
            except:
                pass
    
    def _get_all_jar_paths(self) -> List[str]:
        """Get paths to all required JAR files for UCanAccess.
        
        Returns:
            List of absolute paths to JAR files
        """
        jar_dir = self.jar_manager.bundled_jar_dir
        jar_paths = []
        
        # Required JAR files for UCanAccess 4.0.4
        required_jars = [
            'ucanaccess-4.0.4.jar',
            'commons-lang3-3.8.1.jar',
            'commons-logging-1.2.jar',
            'hsqldb-2.5.0.jar',
            'jackcess-3.0.1.jar'
        ]
        
        for jar_name in required_jars:
            jar_path = jar_dir / jar_name
            if jar_path.exists():
                jar_paths.append(str(jar_path))
            else:
                self.logger.warning(f"Required JAR not found: {jar_path}")
        
        return jar_paths
    
    def get_connection_info(self) -> dict:
        """Get information about the current connection.
        
        Returns:
            Dictionary with connection information
        """
        return {
            'backend': 'UCanAccess-Subprocess',
            'connected': self.db_path is not None,
            'db_path': self.db_path,
            'method': 'Java subprocess (Databricks Serverless compatible)',
            'jar_info': self.jar_manager.get_jar_info()
        }