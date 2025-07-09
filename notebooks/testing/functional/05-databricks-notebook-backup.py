# Databricks notebook source
# MAGIC %md
# MAGIC # Databricks Workspace Notebook Backup System
# MAGIC
# MAGIC This notebook provides a comprehensive backup solution for Databricks Workspace notebooks with:
# MAGIC - **Step 1**: Create inventory of all notebooks with metadata
# MAGIC - **Step 2**: Multi-threaded backup to Unity Catalog Volumes
# MAGIC - **Step 3**: Restore functionality (placeholder for future implementation)
# MAGIC
# MAGIC ## Features:
# MAGIC - Folder-level multi-threading for optimal performance
# MAGIC - Progress tracking and performance metrics
# MAGIC - Error handling with retry logic
# MAGIC - Backup versioning with timestamps

# COMMAND ----------
# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

def get_optimal_thread_count(user_threads: int = None) -> int:
    """Determine optimal thread count based on CPU cores and user preference"""
    import multiprocessing
    import builtins
    
    # Get CPU count
    cpu_count = multiprocessing.cpu_count()
    
    # Get Spark configuration if available
    try:
        spark_cores = int(spark.conf.get("spark.driver.cores", cpu_count))
        cpu_count = spark_cores
    except:
        pass
    
    # Calculate optimal threads (2x CPU count for I/O bound operations)
    optimal_threads = cpu_count * 2
    
    # Apply bounds
    min_threads = 5
    max_threads = 100  # Increased max limit
    
    if user_threads:
        # Use user-specified value if provided, but within bounds
        thread_count = builtins.max(min_threads, builtins.min(max_threads, user_threads))
    else:
        # Use optimal calculated value
        thread_count = builtins.max(min_threads, builtins.min(max_threads, optimal_threads))
    
    print(f"System Information:")
    print(f"  - CPU cores detected: {cpu_count}")
    print(f"  - Optimal thread count: {optimal_threads}")
    print(f"  - Using thread count: {thread_count}")
    
    return thread_count

# Create widgets for configuration
dbutils.widgets.text("workspace_path", "/", "Workspace Path to Backup")
dbutils.widgets.text("backup_volume_path", "/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/backup", "Backup Volume Path")
dbutils.widgets.text("catalog", "cortex_dev_catalog", "Catalog Name")
dbutils.widgets.text("schema", "0000_santosh", "Schema Name")
dbutils.widgets.text("inventory_table", "notebooks_inventory", "Inventory Table Name")
dbutils.widgets.text("max_threads", "0", "Maximum Threads (0=auto, 5-100)")
dbutils.widgets.dropdown("dry_run", "no", ["yes", "no"], "Dry Run Mode")
dbutils.widgets.dropdown("force_refresh", "yes", ["yes", "no"], "Force Inventory Refresh")
dbutils.widgets.dropdown("verbose", "yes", ["yes", "no"], "Verbose Output")
dbutils.widgets.dropdown("parallel_scan", "yes", ["yes", "no"], "Use Parallel Scanning")

# Get widget values
workspace_path = dbutils.widgets.get("workspace_path")
backup_volume_path = dbutils.widgets.get("backup_volume_path")
catalog = dbutils.widgets.get("catalog")
schema_name = dbutils.widgets.get("schema")  # Renamed to avoid conflict with pyspark.sql.types.schema
inventory_table = dbutils.widgets.get("inventory_table")
max_threads = int(dbutils.widgets.get("max_threads"))
dry_run = dbutils.widgets.get("dry_run") == "yes"
force_refresh = dbutils.widgets.get("force_refresh") == "yes"
verbose = dbutils.widgets.get("verbose") == "yes"
parallel_scan = dbutils.widgets.get("parallel_scan") == "yes"

# Validate thread count and get optimal value
# Use built-in functions to avoid conflict with PySpark functions
import builtins
# If 0, use auto-detection, otherwise use user value
max_threads = get_optimal_thread_count(max_threads if max_threads > 0 else None)

# Display configuration
print("=" * 80)
print("Databricks Notebook Backup Configuration")
print("=" * 80)
print(f"Workspace Path: {workspace_path}")
print(f"Backup Volume Path: {backup_volume_path}")
print(f"Inventory Table: {catalog}.{schema_name}.{inventory_table}")
print(f"Max Threads: {max_threads}")
print(f"Dry Run: {dry_run}")
print(f"Force Refresh: {force_refresh}")
print(f"Verbose: {verbose}")
print(f"Parallel Scan: {parallel_scan}")
print("=" * 80)

# COMMAND ----------
# MAGIC %md
# MAGIC ## No Library Installation Required
# MAGIC
# MAGIC The Databricks SDK is pre-installed in the Databricks Serverless environment, so no additional installation is needed.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Import Libraries and Setup

# COMMAND ----------

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import threading
import queue
from dataclasses import dataclass
from collections import defaultdict
# Import base64 after other imports to avoid conflicts
import base64 as b64

# Databricks SDK imports
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *

# Initialize Spark session
spark = SparkSession.builder.appName("NotebookBackup").getOrCreate()

# Initialize Databricks SDK client with proper authentication
def get_workspace_client():
    """Get WorkspaceClient with proper authentication for both Serverless and Classic compute"""
    try:
        # Try default authentication (works in Serverless)
        return WorkspaceClient()
    except (ValueError, Exception) as e:
        if "cannot configure default credentials" in str(e) or "DATABRICKS_HOST" in str(e):
            # Classic compute - use notebook context
            import os
            
            try:
                # Get host and token from notebook context
                context = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
                host = context.apiUrl().get()
                token = context.apiToken().get()
                
                # Clean up the host URL if needed
                if host and not host.startswith("http"):
                    host = f"https://{host}"
                
                # Set environment variables for SDK authentication
                os.environ["DATABRICKS_HOST"] = host
                os.environ["DATABRICKS_TOKEN"] = token
                
                # Now create client with environment variables set
                return WorkspaceClient()
            except Exception as inner_e:
                print(f"Error setting up Classic compute authentication: {inner_e}")
                print("Attempting alternative authentication method...")
                
                # Alternative: Try using databricks-connect style config
                try:
                    # Get workspace URL from Spark config
                    workspace_url = spark.conf.get("spark.databricks.workspaceUrl", "")
                    if workspace_url:
                        os.environ["DATABRICKS_HOST"] = f"https://{workspace_url}"
                        # Token should already be set
                        return WorkspaceClient()
                except:
                    pass
                
                raise Exception(f"Failed to authenticate in Classic compute: {inner_e}")
        else:
            raise

# Initialize global client
w = get_workspace_client()

# Detect compute environment
try:
    # This will work in Serverless
    test_client = WorkspaceClient()
    compute_type = "Serverless"
    print(f"Running on {compute_type} Compute")
except Exception as e:
    compute_type = "Classic"
    print(f"Running on {compute_type} Compute")
    print(f"Authentication method: Environment variables set from notebook context")

# Thread-safe statistics
class BackupStats:
    def __init__(self):
        self.lock = Lock()
        self.total_notebooks = 0
        self.successful_backups = 0
        self.failed_backups = 0
        self.folders_processed = 0
        self.bytes_processed = 0
        self.start_time = time.time()
        self.errors = []
    
    def increment_success(self, size_bytes: int = 0):
        with self.lock:
            self.successful_backups += 1
            self.bytes_processed += size_bytes
    
    def increment_failure(self, error_msg: str):
        with self.lock:
            self.failed_backups += 1
            self.errors.append(error_msg)
    
    def increment_folder(self):
        with self.lock:
            self.folders_processed += 1
    
    def get_progress(self) -> Dict[str, Any]:
        with self.lock:
            elapsed = time.time() - self.start_time
            processed = self.successful_backups + self.failed_backups
            rate = processed / elapsed if elapsed > 0 else 0
            # Use builtins.round to avoid conflict with PySpark's round function
            return {
                "processed": processed,
                "total": self.total_notebooks,
                "success": self.successful_backups,
                "failed": self.failed_backups,
                "folders": self.folders_processed,
                "rate_per_sec": builtins.round(rate, 2),
                "elapsed_sec": builtins.round(elapsed, 2),
                "mb_processed": builtins.round(self.bytes_processed / (1024 * 1024), 2)
            }

# Global stats instance
backup_stats = BackupStats()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 1: Create Notebook Inventory

# COMMAND ----------

@dataclass
class NotebookInfo:
    """Data class for notebook information"""
    notebook_name: str
    notebook_path: str
    folder_path: str
    language: str
    created_at: datetime
    modified_at: datetime
    size_bytes: int = 0
    object_id: int = None

class ParallelWorkspaceScanner:
    """Parallel scanner for Databricks workspace notebooks"""
    
    def __init__(self, max_workers: int = 20, verbose: bool = True):
        self.max_workers = max_workers
        self.verbose = verbose
        self.notebooks_found = []
        self.directories_scanned = 0
        self.errors = []
        self.lock = Lock()
        self.start_time = time.time()
        
        # Create a pool of WorkspaceClient instances to reuse
        self.client_pool = queue.Queue()
        # Limit clients to half the number of workers to avoid connection pool exhaustion
        self.max_clients = builtins.max(5, builtins.min(10, max_workers // 2))
        for _ in range(self.max_clients):
            self.client_pool.put(get_workspace_client())
    
    def scan_directory(self, path: str) -> List[str]:
        """Scan a single directory and return subdirectories and notebook paths"""
        subdirs = []
        local_notebooks = []
        w_thread = None
        
        try:
            # Get a client from the pool
            w_thread = self.client_pool.get(timeout=30)
            objects = list(w_thread.workspace.list(path=path))
            
            for obj in objects:
                if obj.object_type == workspace.ObjectType.NOTEBOOK:
                    local_notebooks.append(obj.path)
                elif obj.object_type == workspace.ObjectType.DIRECTORY:
                    subdirs.append(obj.path)
            
            # Thread-safe updates
            with self.lock:
                self.notebooks_found.extend(local_notebooks)
                self.directories_scanned += 1
                
            if self.verbose and self.directories_scanned % 10 == 0:
                elapsed = time.time() - self.start_time
                print(f"  Progress: {self.directories_scanned} directories scanned, "
                      f"{len(self.notebooks_found)} notebooks found ({elapsed:.1f}s)")
                
        except Exception as e:
            error_msg = f"Error scanning {path}: {str(e)}"
            with self.lock:
                self.errors.append(error_msg)
            if self.verbose:
                print(f"  ⚠️  {error_msg}")
        finally:
            # Always return the client to the pool
            if w_thread:
                self.client_pool.put(w_thread)
                
        return subdirs
    
    def parallel_scan(self, workspace_path: str) -> List[str]:
        """Perform parallel breadth-first scanning of workspace"""
        print(f"Starting parallel scan with {self.max_workers} workers...")
        print(f"Using {self.max_clients} shared API clients to avoid connection pool exhaustion")
        to_scan = [workspace_path]
        all_notebooks = []
        
        while to_scan:
            # Process current level directories in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self.scan_directory, path) for path in to_scan]
                
                # Collect subdirectories for next iteration
                next_level = []
                for future in as_completed(futures):
                    try:
                        subdirs = future.result()
                        next_level.extend(subdirs)
                    except Exception as e:
                        print(f"  ⚠️  Future failed: {e}")
                
                to_scan = next_level
        
        # Final summary
        elapsed = time.time() - self.start_time
        print(f"\nScan completed in {elapsed:.1f} seconds:")
        print(f"  - Directories scanned: {self.directories_scanned}")
        print(f"  - Notebooks found: {len(self.notebooks_found)}")
        print(f"  - Errors encountered: {len(self.errors)}")
        
        return self.notebooks_found
    
    def get_notebook_metadata(self, notebook_path: str) -> Optional[NotebookInfo]:
        """Get metadata for a single notebook"""
        w_thread = None
        try:
            # Get a client from the pool
            w_thread = self.client_pool.get(timeout=30)
            status = w_thread.workspace.get_status(notebook_path)
            
            return NotebookInfo(
                notebook_name=Path(notebook_path).name,
                notebook_path=notebook_path,
                folder_path=str(Path(notebook_path).parent),
                language=status.language.value if status.language else "UNKNOWN",
                created_at=datetime.fromtimestamp(status.created_at / 1000) if status.created_at else None,
                modified_at=datetime.fromtimestamp(status.modified_at / 1000) if status.modified_at else None,
                size_bytes=status.size if hasattr(status, 'size') else 0,
                object_id=status.object_id
            )
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  Error getting metadata for {notebook_path}: {e}")
            return None
        finally:
            # Always return the client to the pool
            if w_thread:
                self.client_pool.put(w_thread)
    
    def parallel_get_metadata(self, notebook_paths: List[str]) -> List[NotebookInfo]:
        """Get metadata for all notebooks in parallel"""
        print(f"\nFetching metadata for {len(notebook_paths)} notebooks...")
        notebooks_info = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.get_notebook_metadata, path): path 
                      for path in notebook_paths}
            
            for future in as_completed(futures):
                completed += 1
                if completed % 50 == 0 and self.verbose:
                    print(f"  Progress: {completed}/{len(notebook_paths)} notebooks processed")
                
                info = future.result()
                if info:
                    notebooks_info.append(info)
        
        print(f"Metadata fetched for {len(notebooks_info)} notebooks")
        return notebooks_info

def scan_workspace_notebooks_sequential(path: str, recursive: bool = True) -> List[NotebookInfo]:
    """Sequential scan - legacy implementation for comparison"""
    notebooks = []
    
    try:
        objects = w.workspace.list(path=path)
        
        for obj in objects:
            if obj.object_type == workspace.ObjectType.NOTEBOOK:
                # Extract folder path
                folder_path = str(Path(obj.path).parent)
                
                # Get detailed status for timestamps
                try:
                    status = w.workspace.get_status(obj.path)
                    created_at = datetime.fromtimestamp(status.created_at / 1000) if status.created_at else None
                    modified_at = datetime.fromtimestamp(status.modified_at / 1000) if status.modified_at else None
                    
                    notebook = NotebookInfo(
                        notebook_name=Path(obj.path).name,
                        notebook_path=obj.path,
                        folder_path=folder_path,
                        language=status.language.value if status.language else "UNKNOWN",
                        created_at=created_at,
                        modified_at=modified_at,
                        size_bytes=status.size if hasattr(status, 'size') else 0,
                        object_id=status.object_id
                    )
                    notebooks.append(notebook)
                    
                except Exception as e:
                    if verbose:
                        print(f"Warning: Could not get status for {obj.path}: {e}")
                    
            elif obj.object_type == workspace.ObjectType.DIRECTORY and recursive:
                # Recursively scan subdirectories
                notebooks.extend(scan_workspace_notebooks_sequential(obj.path, recursive))
                
    except Exception as e:
        print(f"Error scanning {path}: {e}")
        
    return notebooks

def scan_workspace_notebooks(path: str, recursive: bool = True) -> List[NotebookInfo]:
    """Default function - uses parallel scanning"""
    scanner = ParallelWorkspaceScanner(max_workers=max_threads, verbose=verbose)
    notebook_paths = scanner.parallel_scan(path)
    return scanner.parallel_get_metadata(notebook_paths)

def create_inventory_table(use_parallel: bool = True):
    """Create or update the notebook inventory table"""
    print(f"\nStep 1: Creating Notebook Inventory")
    print("-" * 40)
    
    # Check if we should refresh
    table_exists = spark.catalog.tableExists(f"{catalog}.{schema_name}.{inventory_table}")
    
    if table_exists and not force_refresh:
        print(f"Inventory table already exists. Use 'Force Refresh' to update.")
        return
    
    # Scan workspace
    print(f"Scanning workspace: {workspace_path}")
    print(f"Scan mode: {'Parallel' if use_parallel else 'Sequential'}")
    start_time = time.time()
    
    if use_parallel:
        # Use the new parallel scanner
        scanner = ParallelWorkspaceScanner(max_workers=max_threads, verbose=verbose)
        notebook_paths = scanner.parallel_scan(workspace_path)
        notebooks = scanner.parallel_get_metadata(notebook_paths)
    else:
        # Use the legacy sequential scanner
        notebooks = scan_workspace_notebooks_sequential(workspace_path)
    
    scan_time = time.time() - start_time
    print(f"\nTotal scan time: {scan_time:.2f} seconds")
    print(f"Found {len(notebooks)} notebooks")
    
    if not notebooks:
        print("No notebooks found to backup!")
        return
    
    # Convert to DataFrame
    schema = StructType([
        StructField("notebook_name", StringType(), False),
        StructField("notebook_path", StringType(), False),
        StructField("folder_path", StringType(), False),
        StructField("language", StringType(), True),
        StructField("created_at", TimestampType(), True),
        StructField("modified_at", TimestampType(), True),
        StructField("size_bytes", LongType(), True),
        StructField("object_id", LongType(), True),
        StructField("inventory_timestamp", TimestampType(), False)
    ])
    
    # Add inventory timestamp
    inventory_timestamp = datetime.now()
    rows = []
    for nb in notebooks:
        rows.append((
            nb.notebook_name,
            nb.notebook_path,
            nb.folder_path,
            nb.language,
            nb.created_at,
            nb.modified_at,
            nb.size_bytes,
            nb.object_id,
            inventory_timestamp
        ))
    
    df = spark.createDataFrame(rows, schema)
    
    # Write to Delta table
    df.write \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(f"{catalog}.{schema_name}.{inventory_table}")
    
    # Display summary
    summary_df = df.groupBy("folder_path") \
        .agg(
            count("*").alias("notebook_count"),
            sum("size_bytes").alias("total_bytes"),
            max("modified_at").alias("latest_modified")
        ) \
        .orderBy(desc("notebook_count"))
    
    print(f"\nInventory Summary by Folder:")
    summary_df.show(20, truncate=False)
    
    # Update global stats
    backup_stats.total_notebooks = len(notebooks)
    
    print(f"\n✓ Inventory table created: {catalog}.{schema_name}.{inventory_table}")
    print(f"  Total notebooks: {len(notebooks)}")
    print(f"  Total folders: {summary_df.count()}")

# Run inventory creation
create_inventory_table(use_parallel=parallel_scan)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 2: Multi-threaded Backup Implementation

# COMMAND ----------

class NotebookBackupWorker:
    """Worker class for backing up notebooks"""
    
    def __init__(self, backup_base_path: str, timestamp: str, workspace_path: str, client_pool: queue.Queue):
        self.backup_base_path = backup_base_path
        self.timestamp = timestamp
        self.workspace_path = workspace_path
        self.client_pool = client_pool  # Use shared client pool
        
    def export_notebook(self, notebook: Dict[str, Any], retry_count: int = 2) -> Tuple[bool, Dict[str, Any]]:
        """Export a single notebook and return its content"""
        w = None
        last_error = None
        
        for attempt in range(retry_count + 1):
            try:
                # Get a client from the pool
                w = self.client_pool.get(timeout=30)
                
                # Export notebook as SOURCE format (.py)
                content = w.workspace.export(
                    path=notebook['notebook_path'],
                    format=workspace.ExportFormat.SOURCE
                )
                
                # Decode content
                decoded_content = b64.b64decode(content.content)
                size_bytes = len(decoded_content)
                
                # Construct backup path
                relative_path = notebook['notebook_path'].replace(self.workspace_path, "").lstrip("/")
                backup_file_path = f"{self.backup_base_path}/{self.timestamp}/{relative_path}.py"
                
                return True, {
                    "notebook_path": notebook['notebook_path'],
                    "backup_path": backup_file_path,
                    "content": decoded_content.decode('utf-8'),
                    "size_bytes": size_bytes
                }
                
            except Exception as e:
                last_error = e
                error_details = str(e) if str(e) else "No error details available"
                
                # Check for rate limiting - retry after delay
                if "Too many requests" in error_details or "429" in error_details:
                    if attempt < retry_count:
                        import time
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                
                # For permission errors, don't retry
                if "Permission denied" in error_details or "403" in error_details:
                    break
                    
                # For other errors, retry if attempts remaining
                if attempt < retry_count:
                    import time
                    time.sleep(0.5)  # Brief pause before retry
                    continue
                    
            finally:
                # Always return the client to the pool
                if w:
                    self.client_pool.put(w)
                    w = None
        
        # All attempts failed
        error_type = type(last_error).__name__
        error_details = str(last_error) if str(last_error) else "No error details available"
        
        # Categorize error
        if "Too many requests" in error_details or "429" in error_details:
            error_msg = f"Rate limited after {retry_count + 1} attempts: {error_details}"
        elif "Permission denied" in error_details or "403" in error_details:
            error_msg = f"Access denied: {error_details}"
        elif "Not found" in error_details or "404" in error_details:
            error_msg = f"Notebook not found: {error_details}"
        else:
            error_msg = f"{error_type}: {error_details}"
        
        return False, {"error": f"Failed to export {notebook['notebook_path']}: {error_msg}"}
    
    def backup_folder(self, folder_path: str, notebooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export all notebooks in a folder and return their contents"""
        folder_results = {
            "folder": folder_path,
            "total": len(notebooks),
            "notebooks_to_backup": []
        }
        
        if verbose:
            print(f"Thread {threading.current_thread().name}: Processing {folder_path} ({len(notebooks)} notebooks)")
        
        for notebook in notebooks:
            if verbose and len(notebooks) > 0:
                print(f"  Processing notebook: {notebook.get('notebook_path', 'Unknown path')}")
            success, result = self.export_notebook(notebook)
            
            if success:
                folder_results["notebooks_to_backup"].append(result)
            else:
                folder_results["notebooks_to_backup"].append({
                    "error": result.get("error", "Unknown error"),
                    "notebook_path": notebook.get('notebook_path', 'Unknown')
                })
        
        return folder_results

def run_multithreaded_backup():
    """Run multi-threaded backup process"""
    print(f"\nStep 2: Multi-threaded Backup")
    print("-" * 40)
    
    # Load inventory
    inventory_df = spark.table(f"{catalog}.{schema_name}.{inventory_table}")
    
    # Group by folder
    folder_groups = inventory_df.groupBy("folder_path").agg(
        collect_list(struct(
            col("notebook_name"),
            col("notebook_path"),
            col("language"),
            col("size_bytes")
        )).alias("notebooks")
    ).collect()
    
    print(f"Found {len(folder_groups)} folders to process")
    print(f"Using {max_threads} threads for parallel processing")
    
    # Create backup timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a client pool for backup workers
    backup_client_pool = queue.Queue()
    # Limit to 10 clients maximum to avoid connection pool issues
    num_backup_clients = builtins.min(10, max_threads // 2)
    print(f"Creating pool of {num_backup_clients} API clients for backup operations")
    for _ in range(num_backup_clients):
        backup_client_pool.put(get_workspace_client())
    
    # Initialize worker with shared client pool
    worker = NotebookBackupWorker(backup_volume_path, timestamp, workspace_path, backup_client_pool)
    
    # Process folders in parallel
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submit tasks
        future_to_folder = {}
        
        for row in folder_groups:
            folder_path = row['folder_path']
            notebooks = [nb.asDict() for nb in row['notebooks']]
            
            if verbose and len(notebooks) > 0:
                print(f"Submitting folder {folder_path} with first notebook: {notebooks[0] if notebooks else 'None'}")
            
            future = executor.submit(worker.backup_folder, folder_path, notebooks)
            future_to_folder[future] = folder_path
        
        # Process completed tasks
        for future in as_completed(future_to_folder):
            folder_path = future_to_folder[future]
            try:
                result = future.result()
                results.append(result)
                
                # Process notebooks from this folder
                success_count = 0
                failed_count = 0
                
                for nb_data in result["notebooks_to_backup"]:
                    if "error" in nb_data:
                        failed_count += 1
                        error_msg = nb_data["error"]
                        backup_stats.increment_failure(error_msg)
                        if verbose:
                            print(f"  ✗ Failed: {nb_data.get('notebook_path', 'Unknown')}")
                            print(f"    Error: {error_msg}")
                    else:
                        # Write the notebook to volume
                        try:
                            if not dry_run:
                                dbutils.fs.put(nb_data["backup_path"], nb_data["content"], overwrite=True)
                            success_count += 1
                            backup_stats.increment_success(nb_data["size_bytes"])
                        except Exception as write_error:
                            failed_count += 1
                            backup_stats.increment_failure(f"Write error: {str(write_error)}")
                            if verbose:
                                print(f"  ✗ Write failed: {nb_data['notebook_path']}")
                
                backup_stats.increment_folder()
                
                if verbose:
                    print(f"✓ Completed: {folder_path} " +
                          f"(Success: {success_count}, Failed: {failed_count})")
                    
            except Exception as e:
                print(f"✗ Error processing {folder_path}: {e}")
    
    # Final statistics
    elapsed_time = time.time() - start_time
    final_stats = backup_stats.get_progress()
    
    print("\n" + "=" * 60)
    print("Backup Summary")
    print("=" * 60)
    print(f"Total Notebooks: {final_stats['total']}")
    print(f"Successfully Backed Up: {final_stats['success']}")
    print(f"Failed: {final_stats['failed']}")
    print(f"Folders Processed: {final_stats['folders']}")
    print(f"Data Processed: {final_stats['mb_processed']:.2f} MB")
    print(f"Elapsed Time: {elapsed_time:.2f} seconds")
    print(f"Average Rate: {final_stats['rate_per_sec']:.2f} notebooks/second")
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No files were actually written")
    else:
        print(f"\n✓ Backup Location: {backup_volume_path}/{timestamp}/")
    
    # Show error breakdown if there are errors
    if backup_stats.errors:
        print(f"\n📊 Error Analysis:")
        error_types = {}
        for error in backup_stats.errors:
            if "Rate limited" in error or "Too many requests" in error:
                error_types["Rate Limited"] = error_types.get("Rate Limited", 0) + 1
            elif "Access denied" in error or "Permission denied" in error:
                error_types["Access Denied"] = error_types.get("Access Denied", 0) + 1
            elif "Not found" in error or "404" in error:
                error_types["Not Found"] = error_types.get("Not Found", 0) + 1
            else:
                error_types["Other"] = error_types.get("Other", 0) + 1
        
        for error_type, count in error_types.items():
            print(f"  - {error_type}: {count} failures")
        
        print(f"\n💡 Recommendations:")
        if error_types.get("Rate Limited", 0) > 0:
            print("  - Consider reducing thread count to avoid rate limiting")
        if error_types.get("Access Denied", 0) > 0:
            print("  - Some notebooks may be in restricted folders (e.g., CONTENT_LIBRARY)")
        if error_types.get("Not Found", 0) > 0:
            print("  - Some notebooks may have been deleted between scan and backup")
    
    # Save backup metadata with error categorization
    if not dry_run:
        # Categorize errors for better reporting
        error_categories = {
            "rate_limited": [],
            "access_denied": [],
            "not_found": [],
            "other_errors": []
        }
        
        for error in backup_stats.errors:
            if "Rate limited" in error or "Too many requests" in error:
                error_categories["rate_limited"].append(error)
            elif "Access denied" in error or "Permission denied" in error:
                error_categories["access_denied"].append(error)
            elif "Not found" in error or "404" in error:
                error_categories["not_found"].append(error)
            else:
                error_categories["other_errors"].append(error)
        
        metadata = {
            "timestamp": timestamp,
            "source_path": workspace_path,
            "backup_path": f"{backup_volume_path}/{timestamp}",
            "statistics": final_stats,
            "errors": backup_stats.errors[:100],  # Limit errors in metadata
            "error_summary": {
                "rate_limited": len(error_categories["rate_limited"]),
                "access_denied": len(error_categories["access_denied"]),
                "not_found": len(error_categories["not_found"]),
                "other_errors": len(error_categories["other_errors"])
            },
            "configuration": {
                "max_threads": max_threads,
                "catalog": catalog,
                "schema": schema_name,
                "inventory_table": inventory_table
            }
        }
        
        metadata_path = f"{backup_volume_path}/{timestamp}/backup_metadata.json"
        dbutils.fs.put(metadata_path, json.dumps(metadata, indent=2, default=str), overwrite=True)
        print(f"✓ Backup metadata saved: {metadata_path}")
    
    return results

# Run backup
if not dry_run or (dry_run and input("Proceed with dry run? (yes/no): ").lower() == "yes"):
    backup_results = run_multithreaded_backup()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 3: Restore Functionality (Placeholder)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Restore Implementation Placeholder
# MAGIC
# MAGIC The restore functionality will be implemented in a future version. Here's the planned structure:

# COMMAND ----------

class NotebookRestoreWorker:
    """Worker class for restoring notebooks from backup - TO BE IMPLEMENTED"""
    
    def __init__(self, backup_path: str):
        self.backup_path = backup_path
        self.w = WorkspaceClient()
    
    def restore_notebook(self, source_path: str, target_path: str) -> Tuple[bool, str]:
        """Restore a single notebook - PLACEHOLDER"""
        # TODO: Implementation
        # 1. Read notebook content from volume
        # 2. Determine format and language
        # 3. Import to workspace using workspace.import_()
        # 4. Handle conflicts (overwrite/skip/rename)
        pass
    
    def restore_folder(self, folder_path: str, notebooks: List[str]) -> Dict[str, Any]:
        """Restore all notebooks in a folder - PLACEHOLDER"""
        # TODO: Implementation
        # 1. Create folder structure if needed
        # 2. Restore each notebook
        # 3. Track progress and errors
        pass

def run_multithreaded_restore(backup_timestamp: str, target_workspace_path: Optional[str] = None):
    """Run multi-threaded restore process - PLACEHOLDER"""
    # TODO: Implementation
    # 1. Load backup metadata
    # 2. Validate backup integrity
    # 3. Group by folders
    # 4. Process in parallel with ThreadPoolExecutor
    # 5. Generate restore report
    
    print("Restore functionality not yet implemented")
    print("Planned features:")
    print("- Selective restore by folder/pattern")
    print("- Conflict resolution options")
    print("- Dry run mode")
    print("- Progress tracking")
    print("- Parallel restore with configurable threads")

# Example placeholder call
# run_multithreaded_restore("20240115_120000", "/Users/restored/")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Utility Functions

# COMMAND ----------

def list_available_backups():
    """List all available backups in the volume"""
    try:
        backups = []
        
        # List directories in backup path
        items = dbutils.fs.ls(backup_volume_path)
        
        for item in items:
            if item.isDir() and item.name.strip('/').replace('_', '').isdigit():
                # Try to read metadata
                metadata_path = f"{item.path}backup_metadata.json"
                try:
                    content = dbutils.fs.head(metadata_path, max_bytes=10000)
                    metadata = json.loads(content)
                    
                    backups.append({
                        "timestamp": item.name.strip('/'),
                        "path": item.path,
                        "notebooks": metadata['statistics']['total'],
                        "success": metadata['statistics']['success'],
                        "size_mb": metadata['statistics'].get('mb_processed', 0)
                    })
                except:
                    # Metadata not found or invalid
                    backups.append({
                        "timestamp": item.name.strip('/'),
                        "path": item.path,
                        "notebooks": "Unknown",
                        "success": "Unknown",
                        "size_mb": 0
                    })
        
        # Convert to DataFrame for display
        if backups:
            backups_df = spark.createDataFrame(backups)
            print("Available Backups:")
            backups_df.orderBy(desc("timestamp")).show(20, truncate=False)
        else:
            print("No backups found")
            
    except Exception as e:
        print(f"Error listing backups: {e}")

# List available backups
print("\n" + "=" * 60)
list_available_backups()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Performance Analysis

# COMMAND ----------

def analyze_backup_performance():
    """Analyze backup performance metrics"""
    if backup_stats.total_notebooks == 0:
        print("No backup has been run yet")
        return
    
    stats = backup_stats.get_progress()
    
    # Calculate additional metrics
    success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
    avg_notebook_size = (stats['mb_processed'] * 1024 * 1024 / stats['success']) if stats['success'] > 0 else 0
    theoretical_single_thread_time = stats['total'] / stats['rate_per_sec'] if stats['rate_per_sec'] > 0 else 0
    speedup_factor = theoretical_single_thread_time / stats['elapsed_sec'] if stats['elapsed_sec'] > 0 else 1
    
    print("\nPerformance Analysis")
    print("=" * 60)
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Average Notebook Size: {avg_notebook_size / 1024:.2f} KB")
    print(f"Throughput: {stats['rate_per_sec']:.2f} notebooks/second")
    print(f"Data Transfer Rate: {stats['mb_processed'] / stats['elapsed_sec']:.2f} MB/second")
    print(f"\nMulti-threading Performance:")
    print(f"Theoretical Single-threaded Time: {theoretical_single_thread_time:.1f} seconds")
    print(f"Actual Multi-threaded Time: {stats['elapsed_sec']:.1f} seconds")
    print(f"Speedup Factor: {speedup_factor:.1f}x")
    print(f"Thread Efficiency: {speedup_factor / max_threads * 100:.1f}%")
    
    if backup_stats.errors:
        print(f"\nErrors Encountered: {len(backup_stats.errors)}")
        print("First 5 errors:")
        for i, error in enumerate(backup_stats.errors[:5]):
            print(f"  {i+1}. {error[:100]}...")

# Analyze performance if backup was run
if backup_stats.total_notebooks > 0:
    analyze_backup_performance()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC 1. **Schedule Regular Backups**: Create a Databricks job to run this notebook on a schedule
# MAGIC 2. **Implement Restore**: Complete the restore functionality in Step 3
# MAGIC 3. **Add Retention Policy**: Implement automatic cleanup of old backups
# MAGIC 4. **Enhanced Monitoring**: Send backup metrics to monitoring system
# MAGIC 5. **Incremental Backups**: Only backup changed notebooks since last backup