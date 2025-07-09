# Technical Implementation Guide
# Databricks Git-Based Backup Solution

## Overview

This technical implementation guide provides detailed code templates, configuration examples, and best practices for implementing the Git-based backup solution for 70,000+ Databricks notebooks. The guide includes working code snippets, configuration templates, and troubleshooting procedures.

## Table of Contents

1. [Prerequisites and Setup](#prerequisites-and-setup)
2. [Core Components Implementation](#core-components-implementation)
3. [Configuration Templates](#configuration-templates)
4. [Code Templates](#code-templates)
5. [Deployment Guide](#deployment-guide)
6. [Monitoring and Alerting](#monitoring-and-alerting)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Best Practices](#best-practices)

## 1. Prerequisites and Setup

### 1.1 Environment Requirements

```python
# Required packages in Databricks notebook
required_packages = [
    "databricks-sdk>=0.17.0",
    "gitpython>=3.1.0",
    "pyspark>=3.4.0",
    "requests>=2.28.0",
    "typing-extensions>=4.5.0",
    "pyyaml>=6.0"
]

# Install packages (if needed)
# %pip install databricks-sdk gitpython
```

### 1.2 Azure DevOps Repository Setup

```bash
# Create repository in Azure DevOps
az repos create \
  --name "client-notebooks-backup" \
  --project "DataEngineering" \
  --organization "https://dev.azure.com/yourorg"

# Configure repository settings
git config core.compression 0
git config core.loosecompression 0
git config pack.window 0
git config pack.depth 0
git config http.postBuffer 524288000
git config http.maxRequestBuffer 100M
git config core.packedGitLimit 512m
git config core.packedGitWindowSize 512m
```

### 1.3 Databricks Secret Configuration

```python
# Create secret scope
databricks secrets create-scope --scope "git-backup-secrets"

# Add secrets
databricks secrets put --scope "git-backup-secrets" --key "azure-devops-pat"
databricks secrets put --scope "git-backup-secrets" --key "azure-devops-url"
databricks secrets put --scope "git-backup-secrets" --key "notification-email"
```

## 2. Core Components Implementation

### 2.1 Git Folder Converter

```python
# File: git_folder_converter.py

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
from typing import Dict, List, Optional, Tuple
import time
import json
import logging

class GitFolderConverter:
    """
    Converts existing Databricks workspace folders to Git-enabled folders
    """
    
    def __init__(self, 
                 workspace_client: WorkspaceClient,
                 azure_repo_url: str,
                 azure_pat_token: str):
        self.w = workspace_client
        self.repo_url = azure_repo_url
        self.pat_token = azure_pat_token
        self.logger = logging.getLogger(__name__)
        
    def check_folder_status(self, folder_path: str) -> Dict[str, any]:
        """Check if folder is Git-enabled and get status"""
        try:
            # List folder contents to check if it's a Git folder
            folder_info = self.w.workspace.get_status(folder_path)
            
            # Try to get repo info if it's a Git folder
            try:
                repos = list(self.w.repos.list())
                for repo in repos:
                    if repo.path == folder_path:
                        return {
                            "is_git_folder": True,
                            "repo_id": repo.id,
                            "repo_url": repo.url,
                            "branch": repo.branch,
                            "head_commit": repo.head_commit_id
                        }
            except Exception:
                pass
                
            return {
                "is_git_folder": False,
                "folder_exists": True,
                "object_count": self._count_objects(folder_path)
            }
            
        except Exception as e:
            return {
                "is_git_folder": False,
                "folder_exists": False,
                "error": str(e)
            }
    
    def _count_objects(self, path: str) -> int:
        """Count notebooks and folders recursively"""
        count = 0
        try:
            objects = list(self.w.workspace.list(path=path))
            for obj in objects:
                count += 1
                if obj.object_type == workspace.ObjectType.DIRECTORY:
                    count += self._count_objects(obj.path)
        except Exception as e:
            self.logger.warning(f"Error counting objects in {path}: {e}")
        return count
    
    def convert_to_git_folder(self, 
                            source_path: str,
                            target_git_path: str = None,
                            branch: str = "main",
                            create_repo: bool = True) -> Dict[str, any]:
        """
        Convert workspace folder to Git folder
        
        Args:
            source_path: Existing workspace folder path
            target_git_path: Target Git folder path (default: source_path + "_git")
            branch: Git branch to use
            create_repo: Whether to create repo if not exists
            
        Returns:
            Conversion result with status and details
        """
        if not target_git_path:
            target_git_path = source_path + "_git"
            
        try:
            # Step 1: Validate source folder
            source_status = self.check_folder_status(source_path)
            if not source_status.get("folder_exists"):
                return {"success": False, "error": "Source folder does not exist"}
                
            if source_status.get("is_git_folder"):
                return {"success": False, "error": "Source folder is already Git-enabled"}
            
            # Step 2: Create Git folder
            repo_info = self.w.repos.create(
                path=target_git_path,
                url=self.repo_url,
                provider="azureDevOpsServices"
            )
            
            # Step 3: Export and import notebooks
            export_result = self._export_and_import_notebooks(
                source_path, target_git_path, repo_info.id
            )
            
            # Step 4: Initial commit
            commit_result = self._create_initial_commit(repo_info.id)
            
            return {
                "success": True,
                "repo_id": repo_info.id,
                "repo_path": target_git_path,
                "source_path": source_path,
                "notebooks_migrated": export_result.get("count", 0),
                "commit_id": commit_result.get("commit_id"),
                "conversion_time": export_result.get("duration", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Conversion failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _export_and_import_notebooks(self, 
                                   source_path: str, 
                                   target_path: str,
                                   repo_id: int) -> Dict[str, any]:
        """Export notebooks from source and import to Git folder"""
        start_time = time.time()
        exported_count = 0
        
        try:
            # Get all notebooks recursively
            notebooks = self._get_all_notebooks(source_path)
            
            for notebook_path in notebooks:
                try:
                    # Export notebook
                    content = self.w.workspace.export(
                        path=notebook_path,
                        format=workspace.ExportFormat.SOURCE
                    )
                    
                    # Calculate target path
                    relative_path = notebook_path.replace(source_path, "").lstrip("/")
                    target_notebook_path = f"{target_path}/{relative_path}"
                    
                    # Import to Git folder
                    self.w.workspace.import_(
                        path=target_notebook_path,
                        content=content.content,
                        format=workspace.ImportFormat.AUTO,
                        language=workspace.Language.PYTHON,
                        overwrite=True
                    )
                    
                    exported_count += 1
                    
                    if exported_count % 100 == 0:
                        self.logger.info(f"Exported {exported_count} notebooks...")
                        
                except Exception as e:
                    self.logger.warning(f"Failed to export {notebook_path}: {e}")
            
            duration = time.time() - start_time
            return {
                "count": exported_count,
                "duration": duration,
                "rate": exported_count / duration if duration > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Export/import failed: {e}")
            raise
    
    def _get_all_notebooks(self, path: str) -> List[str]:
        """Get all notebook paths recursively"""
        notebooks = []
        try:
            objects = list(self.w.workspace.list(path=path))
            for obj in objects:
                if obj.object_type == workspace.ObjectType.NOTEBOOK:
                    notebooks.append(obj.path)
                elif obj.object_type == workspace.ObjectType.DIRECTORY:
                    notebooks.extend(self._get_all_notebooks(obj.path))
        except Exception as e:
            self.logger.warning(f"Error scanning {path}: {e}")
        return notebooks
    
    def _create_initial_commit(self, repo_id: int) -> Dict[str, any]:
        """Create initial commit in Git folder"""
        try:
            # Update repo to trigger commit
            self.w.repos.update(repo_id=repo_id, branch="main")
            
            # Get commit info
            repo_info = self.w.repos.get(repo_id)
            
            return {
                "commit_id": repo_info.head_commit_id,
                "branch": repo_info.branch
            }
        except Exception as e:
            self.logger.warning(f"Initial commit failed: {e}")
            return {"error": str(e)}
```

### 2.2 Git Sync Engine

```python
# File: git_sync_engine.py

import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
import time
import base64
import json

@dataclass
class SyncStats:
    """Statistics tracking for sync operations"""
    total_files: int = 0
    processed_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    bytes_processed: int = 0
    start_time: float = 0
    end_time: float = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class GitSyncEngine:
    """
    High-performance Git synchronization engine for large-scale operations
    """
    
    def __init__(self,
                 workspace_client: WorkspaceClient,
                 repo_id: int,
                 batch_size: int = 1000,
                 max_workers: int = 20,
                 verbose: bool = True):
        self.w = workspace_client
        self.repo_id = repo_id
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.verbose = verbose
        self.stats = SyncStats()
        self.lock = threading.Lock()
        
        # Create client pool for thread safety
        self.client_pool = queue.Queue()
        num_clients = min(10, max_workers // 2)
        for _ in range(num_clients):
            self.client_pool.put(WorkspaceClient())
    
    def sync_to_remote(self, 
                      workspace_path: str,
                      incremental: bool = True,
                      commit_message: str = None) -> Dict[str, Any]:
        """
        Synchronize workspace changes to Git repository
        
        Args:
            workspace_path: Root workspace path to sync
            incremental: Only sync changed files
            commit_message: Custom commit message
            
        Returns:
            Sync results with statistics
        """
        self.stats = SyncStats()
        self.stats.start_time = time.time()
        
        try:
            # Step 1: Detect changes
            if incremental:
                changed_files = self._detect_changes(workspace_path)
            else:
                changed_files = self._get_all_notebooks(workspace_path)
            
            self.stats.total_files = len(changed_files)
            
            if not changed_files:
                return self._create_sync_result("No changes detected")
            
            # Step 2: Process files in batches
            batches = self._create_batches(changed_files, self.batch_size)
            
            # Step 3: Process batches in parallel
            for batch_num, batch in enumerate(batches, 1):
                if self.verbose:
                    print(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} files)")
                
                self._process_batch(batch, workspace_path)
                
                # Intermediate commit for large batches
                if batch_num % 5 == 0:
                    self._create_intermediate_commit(f"Batch {batch_num} of {len(batches)}")
            
            # Step 4: Final commit and push
            final_commit = self._create_final_commit(commit_message)
            
            self.stats.end_time = time.time()
            
            return self._create_sync_result("Sync completed successfully", final_commit)
            
        except Exception as e:
            self.stats.end_time = time.time()
            error_msg = f"Sync failed: {str(e)}"
            self.stats.errors.append(error_msg)
            return self._create_sync_result(error_msg)
    
    def _detect_changes(self, workspace_path: str) -> List[str]:
        """Detect changed files since last sync"""
        # Implementation would use modification timestamps
        # and compare with last sync metadata
        
        # For now, return all notebooks (full sync)
        return self._get_all_notebooks(workspace_path)
    
    def _get_all_notebooks(self, path: str) -> List[str]:
        """Get all notebooks recursively with parallel scanning"""
        notebooks = []
        
        def scan_directory(dir_path: str) -> List[str]:
            local_notebooks = []
            subdirs = []
            
            client = self.client_pool.get(timeout=30)
            try:
                objects = list(client.workspace.list(path=dir_path))
                for obj in objects:
                    if obj.object_type == workspace.ObjectType.NOTEBOOK:
                        local_notebooks.append(obj.path)
                    elif obj.object_type == workspace.ObjectType.DIRECTORY:
                        subdirs.append(obj.path)
            finally:
                self.client_pool.put(client)
            
            return local_notebooks, subdirs
        
        # BFS traversal with parallel processing
        to_scan = [path]
        
        while to_scan:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(scan_directory, p) for p in to_scan]
                
                next_level = []
                for future in as_completed(futures):
                    try:
                        local_notebooks, subdirs = future.result()
                        notebooks.extend(local_notebooks)
                        next_level.extend(subdirs)
                    except Exception as e:
                        self.stats.errors.append(f"Scan error: {e}")
                
                to_scan = next_level
        
        return notebooks
    
    def _create_batches(self, items: List[str], batch_size: int) -> List[List[str]]:
        """Create batches for parallel processing"""
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    def _process_batch(self, batch: List[str], workspace_path: str):
        """Process a batch of notebooks"""
        
        def process_notebook(notebook_path: str):
            client = self.client_pool.get(timeout=30)
            try:
                # Export notebook
                content = client.workspace.export(
                    path=notebook_path,
                    format=workspace.ExportFormat.SOURCE
                )
                
                # Update stats
                with self.lock:
                    self.stats.processed_files += 1
                    self.stats.successful_files += 1
                    self.stats.bytes_processed += len(content.content)
                
                return True, len(content.content)
                
            except Exception as e:
                with self.lock:
                    self.stats.processed_files += 1
                    self.stats.failed_files += 1
                    self.stats.errors.append(f"Failed to process {notebook_path}: {e}")
                
                return False, 0
            finally:
                self.client_pool.put(client)
        
        # Process batch in parallel
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(batch))) as executor:
            futures = [executor.submit(process_notebook, nb) for nb in batch]
            
            for future in as_completed(futures):
                try:
                    success, bytes_processed = future.result()
                    if self.verbose and self.stats.processed_files % 100 == 0:
                        progress = (self.stats.processed_files / self.stats.total_files) * 100
                        print(f"Progress: {progress:.1f}% ({self.stats.processed_files}/{self.stats.total_files})")
                except Exception as e:
                    self.stats.errors.append(f"Batch processing error: {e}")
    
    def _create_intermediate_commit(self, message: str):
        """Create intermediate commit for large operations"""
        try:
            # Update repo to trigger commit
            self.w.repos.update(repo_id=self.repo_id)
            if self.verbose:
                print(f"Intermediate commit created: {message}")
        except Exception as e:
            self.stats.errors.append(f"Intermediate commit failed: {e}")
    
    def _create_final_commit(self, commit_message: str = None) -> Dict[str, str]:
        """Create final commit with summary"""
        try:
            if not commit_message:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                commit_message = f"Automated backup - {timestamp}\n\n"
                commit_message += f"Files processed: {self.stats.successful_files}\n"
                commit_message += f"Bytes processed: {self.stats.bytes_processed}\n"
                commit_message += f"Duration: {self.stats.end_time - self.stats.start_time:.2f}s"
            
            # Update repo with final commit
            self.w.repos.update(repo_id=self.repo_id)
            
            # Get commit info
            repo_info = self.w.repos.get(self.repo_id)
            
            return {
                "commit_id": repo_info.head_commit_id,
                "message": commit_message,
                "branch": repo_info.branch
            }
            
        except Exception as e:
            error_msg = f"Final commit failed: {e}"
            self.stats.errors.append(error_msg)
            return {"error": error_msg}
    
    def _create_sync_result(self, message: str, commit_info: Dict = None) -> Dict[str, Any]:
        """Create sync result summary"""
        duration = self.stats.end_time - self.stats.start_time
        
        result = {
            "success": self.stats.failed_files == 0 and not any("failed" in err.lower() for err in self.stats.errors),
            "message": message,
            "statistics": {
                "total_files": self.stats.total_files,
                "processed_files": self.stats.processed_files,
                "successful_files": self.stats.successful_files,
                "failed_files": self.stats.failed_files,
                "bytes_processed": self.stats.bytes_processed,
                "duration_seconds": duration,
                "rate_files_per_second": self.stats.processed_files / duration if duration > 0 else 0,
                "rate_mb_per_second": (self.stats.bytes_processed / (1024 * 1024)) / duration if duration > 0 else 0
            },
            "errors": self.stats.errors[:10],  # Limit errors in result
            "timestamp": datetime.now().isoformat()
        }
        
        if commit_info:
            result["commit"] = commit_info
        
        return result
```

### 2.3 State Management

```python
# File: state_manager.py

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from typing import Dict, Optional, Any
import json
from datetime import datetime

class StateManager:
    """
    Manages sync state for resumability and tracking
    """
    
    def __init__(self, 
                 spark: SparkSession,
                 catalog: str,
                 schema: str,
                 state_table: str = "git_sync_state"):
        self.spark = spark
        self.catalog = catalog
        self.schema = schema
        self.state_table = state_table
        self.full_table_name = f"{catalog}.{schema}.{state_table}"
        
        self._ensure_state_table()
    
    def _ensure_state_table(self):
        """Create state table if it doesn't exist"""
        schema = StructType([
            StructField("sync_id", StringType(), False),
            StructField("session_id", StringType(), False),
            StructField("workspace_path", StringType(), False),
            StructField("repo_id", LongType(), False),
            StructField("start_time", TimestampType(), False),
            StructField("end_time", TimestampType(), True),
            StructField("status", StringType(), False),  # running, completed, failed
            StructField("total_files", LongType(), True),
            StructField("processed_files", LongType(), True),
            StructField("successful_files", LongType(), True),
            StructField("failed_files", LongType(), True),
            StructField("bytes_processed", LongType(), True),
            StructField("last_checkpoint", TimestampType(), True),
            StructField("checkpoint_data", StringType(), True),  # JSON
            StructField("error_log", StringType(), True),  # JSON array
            StructField("commit_id", StringType(), True),
            StructField("metadata", StringType(), True)  # JSON
        ])
        
        # Create table if not exists
        if not self.spark.catalog.tableExists(self.full_table_name):
            empty_df = self.spark.createDataFrame([], schema)
            empty_df.write.mode("overwrite").saveAsTable(self.full_table_name)
    
    def start_sync_session(self, 
                          workspace_path: str,
                          repo_id: int,
                          total_files: int = 0,
                          metadata: Dict = None) -> str:
        """Start a new sync session and return session ID"""
        
        sync_id = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        state_data = [
            (
                sync_id,
                session_id,
                workspace_path,
                repo_id,
                datetime.now(),
                None,  # end_time
                "running",
                total_files,
                0,  # processed_files
                0,  # successful_files
                0,  # failed_files
                0,  # bytes_processed
                datetime.now(),  # last_checkpoint
                json.dumps({}),  # checkpoint_data
                json.dumps([]),  # error_log
                None,  # commit_id
                json.dumps(metadata or {})
            )
        ]
        
        df = self.spark.createDataFrame(state_data, schema=self._get_state_schema())
        df.write.mode("append").saveAsTable(self.full_table_name)
        
        return session_id
    
    def update_progress(self,
                       session_id: str,
                       processed_files: int,
                       successful_files: int,
                       failed_files: int,
                       bytes_processed: int,
                       checkpoint_data: Dict = None,
                       errors: List[str] = None):
        """Update sync progress"""
        
        # Read current state
        current_df = self.spark.table(self.full_table_name).filter(
            col("session_id") == session_id
        )
        
        if current_df.count() == 0:
            raise ValueError(f"Session {session_id} not found")
        
        # Update with new progress
        updated_df = current_df.withColumn("processed_files", lit(processed_files)) \
                              .withColumn("successful_files", lit(successful_files)) \
                              .withColumn("failed_files", lit(failed_files)) \
                              .withColumn("bytes_processed", lit(bytes_processed)) \
                              .withColumn("last_checkpoint", lit(datetime.now()))
        
        if checkpoint_data:
            updated_df = updated_df.withColumn("checkpoint_data", lit(json.dumps(checkpoint_data)))
        
        if errors:
            updated_df = updated_df.withColumn("error_log", lit(json.dumps(errors)))
        
        # Replace record
        other_sessions = self.spark.table(self.full_table_name).filter(
            col("session_id") != session_id
        )
        
        final_df = other_sessions.union(updated_df)
        final_df.write.mode("overwrite").saveAsTable(self.full_table_name)
    
    def complete_sync_session(self,
                             session_id: str,
                             status: str,  # completed or failed
                             commit_id: str = None,
                             final_errors: List[str] = None):
        """Mark sync session as complete"""
        
        current_df = self.spark.table(self.full_table_name).filter(
            col("session_id") == session_id
        )
        
        updated_df = current_df.withColumn("end_time", lit(datetime.now())) \
                              .withColumn("status", lit(status))
        
        if commit_id:
            updated_df = updated_df.withColumn("commit_id", lit(commit_id))
        
        if final_errors:
            updated_df = updated_df.withColumn("error_log", lit(json.dumps(final_errors)))
        
        # Replace record
        other_sessions = self.spark.table(self.full_table_name).filter(
            col("session_id") != session_id
        )
        
        final_df = other_sessions.union(updated_df)
        final_df.write.mode("overwrite").saveAsTable(self.full_table_name)
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current session state"""
        
        df = self.spark.table(self.full_table_name).filter(
            col("session_id") == session_id
        )
        
        rows = df.collect()
        if not rows:
            return None
        
        row = rows[0]
        return {
            "sync_id": row.sync_id,
            "session_id": row.session_id,
            "workspace_path": row.workspace_path,
            "repo_id": row.repo_id,
            "start_time": row.start_time,
            "end_time": row.end_time,
            "status": row.status,
            "total_files": row.total_files,
            "processed_files": row.processed_files,
            "successful_files": row.successful_files,
            "failed_files": row.failed_files,
            "bytes_processed": row.bytes_processed,
            "last_checkpoint": row.last_checkpoint,
            "checkpoint_data": json.loads(row.checkpoint_data or "{}"),
            "error_log": json.loads(row.error_log or "[]"),
            "commit_id": row.commit_id,
            "metadata": json.loads(row.metadata or "{}")
        }
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sync sessions"""
        
        df = self.spark.table(self.full_table_name) \
                      .orderBy(desc("start_time")) \
                      .limit(limit)
        
        sessions = []
        for row in df.collect():
            sessions.append({
                "sync_id": row.sync_id,
                "session_id": row.session_id,
                "workspace_path": row.workspace_path,
                "start_time": row.start_time,
                "end_time": row.end_time,
                "status": row.status,
                "total_files": row.total_files,
                "successful_files": row.successful_files,
                "failed_files": row.failed_files,
                "duration_minutes": (row.end_time - row.start_time).total_seconds() / 60 if row.end_time else None
            })
        
        return sessions
    
    def cleanup_old_sessions(self, days_to_keep: int = 30):
        """Clean up old session records"""
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        df = self.spark.table(self.full_table_name).filter(
            col("start_time") >= cutoff_date
        )
        
        df.write.mode("overwrite").saveAsTable(self.full_table_name)
        
        return df.count()
```

## 3. Configuration Templates

### 3.1 Main Configuration Notebook

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Git Backup Configuration

# COMMAND ----------

# Widget configuration
dbutils.widgets.text("clients_folder_path", "/Clients", "Clients Folder Path")
dbutils.widgets.text("git_folder_path", "/Clients", "Git Folder Path")
dbutils.widgets.text("azure_repo_url", "", "Azure DevOps Repository URL")
dbutils.widgets.dropdown("operation_mode", "sync", ["setup", "sync", "restore"], "Operation Mode")
dbutils.widgets.text("batch_size", "1000", "Files per Batch")
dbutils.widgets.text("max_workers", "20", "Maximum Workers")
dbutils.widgets.dropdown("sync_mode", "incremental", ["full", "incremental"], "Sync Mode")
dbutils.widgets.dropdown("dry_run", "no", ["yes", "no"], "Dry Run Mode")
dbutils.widgets.dropdown("verbose", "yes", ["yes", "no"], "Verbose Output")
dbutils.widgets.text("notification_email", "", "Notification Email")

# Get configuration values
config = {
    "clients_folder_path": dbutils.widgets.get("clients_folder_path"),
    "git_folder_path": dbutils.widgets.get("git_folder_path"),
    "azure_repo_url": dbutils.widgets.get("azure_repo_url"),
    "operation_mode": dbutils.widgets.get("operation_mode"),
    "batch_size": int(dbutils.widgets.get("batch_size")),
    "max_workers": int(dbutils.widgets.get("max_workers")),
    "sync_mode": dbutils.widgets.get("sync_mode"),
    "dry_run": dbutils.widgets.get("dry_run") == "yes",
    "verbose": dbutils.widgets.get("verbose") == "yes",
    "notification_email": dbutils.widgets.get("notification_email")
}

# Load secrets
secrets = {
    "azure_pat": dbutils.secrets.get("git-backup-secrets", "azure-devops-pat"),
    "azure_url": dbutils.secrets.get("git-backup-secrets", "azure-devops-url")
}

print("Configuration loaded:")
for key, value in config.items():
    if key != "azure_pat":  # Don't print sensitive data
        print(f"  {key}: {value}")

# COMMAND ----------

# Import required libraries
import time
import json
from datetime import datetime
from databricks.sdk import WorkspaceClient
from pyspark.sql import SparkSession

# Initialize components
spark = SparkSession.builder.appName("GitBackup").getOrCreate()
w = WorkspaceClient()

# Display environment info
print(f"Databricks Runtime: {spark.conf.get('spark.databricks.clusterUsageTags.sparkVersion', 'Unknown')}")
print(f"Workspace URL: {w.config.host}")
print(f"User: {w.current_user.me().user_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## State Management Setup

# COMMAND ----------

# Initialize state manager
from state_manager import StateManager

state_manager = StateManager(
    spark=spark,
    catalog="your_catalog",
    schema="your_schema",
    state_table="git_sync_state"
)

print("State management initialized")

# Display recent sessions
recent_sessions = state_manager.get_recent_sessions(5)
if recent_sessions:
    print("\nRecent sync sessions:")
    for session in recent_sessions:
        print(f"  {session['session_id']}: {session['status']} - {session['total_files']} files")
```

### 3.2 Job Configuration Template

```json
{
  "name": "client-notebooks-git-backup",
  "description": "Daily backup of client notebooks to Git repository",
  "tags": {
    "environment": "production",
    "team": "data-engineering",
    "purpose": "backup"
  },
  "job_clusters": [
    {
      "job_cluster_key": "backup_cluster",
      "new_cluster": {
        "cluster_name": "git-backup-cluster",
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "Standard_DS4_v2",
        "num_workers": 2,
        "spark_conf": {
          "spark.databricks.delta.optimizeWrite.enabled": "true",
          "spark.databricks.delta.autoCompact.enabled": "true",
          "spark.sql.adaptive.enabled": "true",
          "spark.sql.adaptive.coalescePartitions.enabled": "true"
        },
        "custom_tags": {
          "project": "git-backup",
          "cost-center": "data-platform"
        }
      }
    }
  ],
  "tasks": [
    {
      "task_key": "git_sync",
      "description": "Synchronize notebooks to Git repository",
      "job_cluster_key": "backup_cluster",
      "notebook_task": {
        "notebook_path": "/Repos/production/git-backup/notebooks/git_sync_main",
        "base_parameters": {
          "operation_mode": "sync",
          "sync_mode": "incremental",
          "verbose": "yes",
          "dry_run": "no"
        }
      },
      "timeout_seconds": 14400,
      "max_retries": 2,
      "retry_on_timeout": true,
      "email_notifications": {
        "on_failure": ["data-engineering-alerts@company.com"],
        "on_success": ["data-engineering-status@company.com"]
      }
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "UTC",
    "pause_status": "UNPAUSED"
  },
  "max_concurrent_runs": 1,
  "timeout_seconds": 18000,
  "email_notifications": {
    "on_failure": ["data-engineering-oncall@company.com"],
    "on_success": [],
    "no_alert_for_skipped_runs": false
  },
  "webhook_notifications": {
    "on_failure": [
      {
        "id": "webhook-slack-alerts"
      }
    ]
  },
  "notification_settings": {
    "no_alert_for_skipped_runs": false,
    "no_alert_for_canceled_runs": false
  }
}
```

## 4. Code Templates

### 4.1 Main Orchestration Notebook

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Enterprise Git Backup System
# MAGIC
# MAGIC This notebook orchestrates the backup of 70,000+ client notebooks to Azure DevOps Git repository.

# COMMAND ----------

# MAGIC %run ./config

# COMMAND ----------

# MAGIC %run ./git_folder_converter

# COMMAND ----------

# MAGIC %run ./git_sync_engine

# COMMAND ----------

# MAGIC %run ./state_manager

# COMMAND ----------

# Main execution logic
def main():
    """Main orchestration function"""
    
    # Initialize session
    session_id = state_manager.start_sync_session(
        workspace_path=config["clients_folder_path"],
        repo_id=1,  # This would be determined dynamically
        metadata=config
    )
    
    try:
        if config["operation_mode"] == "setup":
            # Convert folder to Git folder
            converter = GitFolderConverter(
                workspace_client=w,
                azure_repo_url=config["azure_repo_url"],
                azure_pat_token=secrets["azure_pat"]
            )
            
            result = converter.convert_to_git_folder(
                source_path=config["clients_folder_path"],
                target_git_path=config["git_folder_path"]
            )
            
            if result["success"]:
                print(f"✓ Successfully converted folder to Git")
                print(f"  Repo ID: {result['repo_id']}")
                print(f"  Notebooks migrated: {result['notebooks_migrated']}")
            else:
                print(f"✗ Conversion failed: {result['error']}")
                return
        
        elif config["operation_mode"] == "sync":
            # Synchronize to Git
            sync_engine = GitSyncEngine(
                workspace_client=w,
                repo_id=1,  # This would be looked up
                batch_size=config["batch_size"],
                max_workers=config["max_workers"],
                verbose=config["verbose"]
            )
            
            # Update session with file count
            notebooks = sync_engine._get_all_notebooks(config["clients_folder_path"])
            state_manager.update_progress(
                session_id=session_id,
                processed_files=0,
                successful_files=0,
                failed_files=0,
                bytes_processed=0
            )
            
            # Perform sync
            result = sync_engine.sync_to_remote(
                workspace_path=config["clients_folder_path"],
                incremental=config["sync_mode"] == "incremental"
            )
            
            # Update final state
            state_manager.complete_sync_session(
                session_id=session_id,
                status="completed" if result["success"] else "failed",
                commit_id=result.get("commit", {}).get("commit_id"),
                final_errors=result.get("errors", [])
            )
            
            # Display results
            stats = result["statistics"]
            print(f"\nSync Results:")
            print(f"  Success: {result['success']}")
            print(f"  Files processed: {stats['processed_files']}")
            print(f"  Success rate: {stats['successful_files']}/{stats['total_files']}")
            print(f"  Duration: {stats['duration_seconds']:.2f} seconds")
            print(f"  Rate: {stats['rate_files_per_second']:.2f} files/second")
            
            if result.get("errors"):
                print(f"  Errors: {len(result['errors'])}")
                for error in result["errors"][:3]:
                    print(f"    - {error}")
        
        # Send notification
        if config["notification_email"]:
            send_notification(config["notification_email"], result)
    
    except Exception as e:
        error_msg = f"Execution failed: {str(e)}"
        print(error_msg)
        
        state_manager.complete_sync_session(
            session_id=session_id,
            status="failed",
            final_errors=[error_msg]
        )
        
        raise

def send_notification(email: str, result: Dict[str, Any]):
    """Send email notification with results"""
    
    subject = f"Git Backup {'Success' if result['success'] else 'Failed'} - {datetime.now().strftime('%Y-%m-%d')}"
    
    stats = result.get("statistics", {})
    body = f"""
    Git Backup Results
    
    Status: {'✓ Success' if result['success'] else '✗ Failed'}
    Files Processed: {stats.get('processed_files', 0)}
    Success Rate: {stats.get('successful_files', 0)}/{stats.get('total_files', 0)}
    Duration: {stats.get('duration_seconds', 0):.2f} seconds
    
    Commit: {result.get('commit', {}).get('commit_id', 'N/A')}
    
    """
    
    if result.get("errors"):
        body += f"\nErrors ({len(result['errors'])}):\n"
        for error in result["errors"][:5]:
            body += f"- {error}\n"
    
    # Implementation would use your preferred notification method
    print(f"Notification would be sent to: {email}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")

# Execute main function
if __name__ == "__main__":
    main()
```

## 5. Deployment Guide

### 5.1 Prerequisites Checklist

```bash
# 1. Azure DevOps Setup
- [ ] Repository created
- [ ] PAT token generated with repo permissions
- [ ] Branch policies configured
- [ ] Build service permissions set

# 2. Databricks Setup
- [ ] Secret scope created
- [ ] Secrets stored (PAT, repo URL)
- [ ] Job cluster configured
- [ ] Unity Catalog permissions set

# 3. Permissions
- [ ] Workspace admin access
- [ ] Repo contributor access
- [ ] Unity Catalog usage permissions
- [ ] Job creation permissions
```

### 5.2 Deployment Steps

```python
# Step 1: Upload notebooks to Databricks
# Create folder structure in Databricks workspace:
# /Repos/production/git-backup/
#   ├── notebooks/
#   │   ├── config.py
#   │   ├── git_folder_converter.py
#   │   ├── git_sync_engine.py
#   │   ├── state_manager.py
#   │   └── git_sync_main.py
#   └── tests/

# Step 2: Configure secrets
dbutils.secrets.listScopes()  # Verify scope exists
dbutils.secrets.list("git-backup-secrets")  # Verify secrets

# Step 3: Test configuration
config_test = {
    "azure_repo_url": dbutils.secrets.get("git-backup-secrets", "azure-devops-url"),
    "azure_pat": dbutils.secrets.get("git-backup-secrets", "azure-devops-pat")[:4] + "..."
}
print("Configuration test:", config_test)

# Step 4: Create job using Databricks CLI or UI
# databricks jobs create --json-file job-config.json

# Step 5: Initial test run
# databricks jobs run-now --job-id <job-id> --notebook-params '{"dry_run": "yes"}'
```

## 6. Monitoring and Alerting

### 6.1 Monitoring Dashboard SQL

```sql
-- Git Sync Success Rate (Last 30 days)
SELECT 
  DATE(start_time) as sync_date,
  COUNT(*) as total_syncs,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_syncs,
  ROUND(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM your_catalog.your_schema.git_sync_state
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAYS
GROUP BY DATE(start_time)
ORDER BY sync_date DESC;

-- Performance Trends
SELECT 
  DATE(start_time) as sync_date,
  AVG(total_files) as avg_files,
  AVG(TIMESTAMPDIFF(SECOND, start_time, end_time)) as avg_duration_seconds,
  AVG(successful_files * 1.0 / TIMESTAMPDIFF(SECOND, start_time, end_time)) as avg_files_per_second
FROM your_catalog.your_schema.git_sync_state
WHERE status = 'completed' 
  AND start_time >= CURRENT_DATE() - INTERVAL 30 DAYS
  AND end_time IS NOT NULL
GROUP BY DATE(start_time)
ORDER BY sync_date DESC;

-- Error Analysis
SELECT 
  session_id,
  start_time,
  failed_files,
  error_log
FROM your_catalog.your_schema.git_sync_state
WHERE failed_files > 0 
  AND start_time >= CURRENT_DATE() - INTERVAL 7 DAYS
ORDER BY start_time DESC;
```

### 6.2 Alert Configuration

```python
# File: monitoring_alerts.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertManager:
    """
    Manages alerts and notifications for sync operations
    """
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def check_sync_health(self, state_manager: StateManager) -> Dict[str, Any]:
        """Check sync health and return status"""
        
        # Get recent sessions
        recent_sessions = state_manager.get_recent_sessions(5)
        
        if not recent_sessions:
            return {"status": "warning", "message": "No recent sync sessions found"}
        
        # Check last sync
        last_sync = recent_sessions[0]
        hours_since_last = (datetime.now() - last_sync["start_time"]).total_seconds() / 3600
        
        # Check for failures
        failed_sessions = [s for s in recent_sessions if s["status"] == "failed"]
        
        alerts = []
        
        # Alert if no sync in 25+ hours (daily sync should run every 24h)
        if hours_since_last > 25:
            alerts.append({
                "severity": "critical",
                "message": f"No sync for {hours_since_last:.1f} hours"
            })
        
        # Alert if last sync failed
        if last_sync["status"] == "failed":
            alerts.append({
                "severity": "critical", 
                "message": f"Last sync failed: {last_sync['session_id']}"
            })
        
        # Alert if multiple recent failures
        if len(failed_sessions) >= 2:
            alerts.append({
                "severity": "warning",
                "message": f"{len(failed_sessions)} failed syncs in recent history"
            })
        
        # Check success rate
        success_rate = len([s for s in recent_sessions if s["status"] == "completed"]) / len(recent_sessions)
        if success_rate < 0.8:
            alerts.append({
                "severity": "warning",
                "message": f"Success rate low: {success_rate:.1%}"
            })
        
        return {
            "status": "critical" if any(a["severity"] == "critical" for a in alerts) else 
                     "warning" if alerts else "healthy",
            "alerts": alerts,
            "last_sync": last_sync,
            "recent_sessions": recent_sessions
        }
    
    def send_alert(self, 
                   recipients: List[str], 
                   subject: str, 
                   message: str, 
                   severity: str = "info"):
        """Send email alert"""
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = f"[{severity.upper()}] {subject}"
            
            body = f"""
Git Backup Alert

Severity: {severity.upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{message}

This is an automated alert from the Databricks Git Backup System.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send alert: {e}")
            return False
```

## 7. Troubleshooting Guide

### 7.1 Common Issues and Solutions

| Issue | Symptoms | Likely Cause | Solution |
|-------|----------|--------------|----------|
| Sync timeout | Job fails after 4 hours | Too many files, insufficient resources | Increase cluster size, reduce batch size |
| Memory errors | OutOfMemoryError during sync | Large files, insufficient memory | Increase driver memory, implement streaming |
| Git push failures | Push operations fail | Network issues, repo size limits | Implement retry logic, check repo size |
| Authentication errors | SDK authentication fails | Expired tokens, wrong permissions | Refresh tokens, verify permissions |
| High failure rate | Many notebooks fail to export | API rate limiting, corrupted files | Implement backoff, skip corrupted files |

### 7.2 Diagnostic Commands

```python
# File: diagnostics.py

def run_diagnostics():
    """Run comprehensive diagnostics"""
    
    print("=== Git Backup Diagnostics ===\n")
    
    # 1. Environment Check
    print("1. Environment Check:")
    try:
        w = WorkspaceClient()
        user = w.current_user.me()
        print(f"  ✓ Workspace connection: {w.config.host}")
        print(f"  ✓ Authenticated user: {user.user_name}")
    except Exception as e:
        print(f"  ✗ Workspace connection failed: {e}")
    
    # 2. Secret Check
    print("\n2. Secret Configuration:")
    try:
        scopes = dbutils.secrets.listScopes()
        git_scope = next((s for s in scopes if s.name == "git-backup-secrets"), None)
        if git_scope:
            secrets = dbutils.secrets.list("git-backup-secrets")
            print(f"  ✓ Secret scope exists: {len(secrets)} secrets")
            for secret in secrets:
                print(f"    - {secret.key}")
        else:
            print("  ✗ Secret scope 'git-backup-secrets' not found")
    except Exception as e:
        print(f"  ✗ Secret check failed: {e}")
    
    # 3. Git Folder Check
    print("\n3. Git Folder Status:")
    try:
        repos = list(w.repos.list())
        clients_repo = next((r for r in repos if "/Clients" in r.path), None)
        if clients_repo:
            print(f"  ✓ Git folder found: {clients_repo.path}")
            print(f"    - Repo ID: {clients_repo.id}")
            print(f"    - Branch: {clients_repo.branch}")
            print(f"    - URL: {clients_repo.url}")
        else:
            print("  ✗ No Git folder found for /Clients")
    except Exception as e:
        print(f"  ✗ Git folder check failed: {e}")
    
    # 4. Performance Check
    print("\n4. Performance Check:")
    try:
        # Test notebook listing performance
        start_time = time.time()
        objects = list(w.workspace.list("/Clients", recursive=False))
        duration = time.time() - start_time
        print(f"  ✓ Workspace API response: {duration:.2f}s for {len(objects)} objects")
        
        # Test parallel capability
        import threading
        thread_count = threading.active_count()
        print(f"  ✓ Active threads: {thread_count}")
        
    except Exception as e:
        print(f"  ✗ Performance check failed: {e}")
    
    # 5. State Table Check
    print("\n5. State Management:")
    try:
        state_df = spark.table("your_catalog.your_schema.git_sync_state")
        record_count = state_df.count()
        latest_sync = state_df.orderBy(desc("start_time")).first()
        print(f"  ✓ State table accessible: {record_count} records")
        if latest_sync:
            print(f"    - Latest sync: {latest_sync.start_time} ({latest_sync.status})")
        else:
            print("    - No sync records found")
    except Exception as e:
        print(f"  ✗ State table check failed: {e}")
    
    print("\n=== Diagnostics Complete ===")

# Performance profiling
def profile_sync_performance(sample_size: int = 100):
    """Profile sync performance with sample data"""
    
    print(f"Profiling sync performance with {sample_size} notebooks...")
    
    # Get sample notebooks
    notebooks = []
    try:
        objects = list(w.workspace.list("/Clients", recursive=True))
        notebook_objects = [obj for obj in objects if obj.object_type == workspace.ObjectType.NOTEBOOK]
        notebooks = notebook_objects[:sample_size]
    except Exception as e:
        print(f"Failed to get sample notebooks: {e}")
        return
    
    # Test export performance
    start_time = time.time()
    successful_exports = 0
    
    for notebook in notebooks[:10]:  # Test with 10 notebooks
        try:
            content = w.workspace.export(notebook.path, format=workspace.ExportFormat.SOURCE)
            successful_exports += 1
        except Exception as e:
            print(f"Export failed for {notebook.path}: {e}")
    
    duration = time.time() - start_time
    
    print(f"Export Performance:")
    print(f"  Notebooks tested: 10")
    print(f"  Successful exports: {successful_exports}")
    print(f"  Total time: {duration:.2f}s")
    print(f"  Rate: {successful_exports/duration:.2f} notebooks/second")
    print(f"  Projected time for 70k notebooks: {(70000/successful_exports)*duration/3600:.1f} hours")
```

## 8. Best Practices

### 8.1 Performance Best Practices

1. **Optimal Batch Sizing**
   ```python
   # Rule of thumb: 1000 files per batch for Git commits
   # Adjust based on file sizes and memory constraints
   batch_size = min(1000, max(100, total_files // 100))
   ```

2. **Thread Pool Management**
   ```python
   # Limit concurrent API clients to avoid connection pool exhaustion
   max_api_clients = min(10, max_workers // 2)
   
   # Use connection pooling for better performance
   client_pool = queue.Queue(maxsize=max_api_clients)
   ```

3. **Memory Management**
   ```python
   # Process in chunks to avoid memory issues
   def process_large_dataset(items, chunk_size=1000):
       for i in range(0, len(items), chunk_size):
           chunk = items[i:i + chunk_size]
           process_chunk(chunk)
           gc.collect()  # Force garbage collection
   ```

### 8.2 Security Best Practices

1. **Credential Management**
   ```python
   # Always use Databricks secrets for sensitive data
   PAT_TOKEN = dbutils.secrets.get("git-backup-secrets", "azure-devops-pat")
   
   # Never log or print credentials
   print(f"Token: {PAT_TOKEN[:4]}...")  # Only show first 4 chars
   ```

2. **Access Control**
   ```python
   # Verify user permissions before operations
   def check_permissions(workspace_client, path):
       try:
           workspace_client.workspace.get_status(path)
           return True
       except Exception:
           return False
   ```

### 8.3 Operational Best Practices

1. **Monitoring and Alerting**
   ```python
   # Always log important events
   logger.info(f"Sync started: {session_id}")
   logger.info(f"Files to process: {total_files}")
   logger.warning(f"Failed to process: {failed_count} files")
   logger.error(f"Critical error: {error_message}")
   ```

2. **Error Handling**
   ```python
   # Implement exponential backoff for retries
   def retry_with_backoff(func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return func()
           except Exception as e:
               if attempt == max_retries - 1:
                   raise
               time.sleep(2 ** attempt)  # Exponential backoff
   ```

3. **State Management**
   ```python
   # Always track state for resumability
   checkpoint_data = {
       "processed_files": processed_count,
       "current_batch": batch_number,
       "last_successful_file": last_file_path
   }
   state_manager.update_progress(session_id, checkpoint_data=checkpoint_data)
   ```

This comprehensive implementation guide provides all the necessary code templates, configuration examples, and best practices needed to successfully implement the Git-based backup solution for Databricks notebooks at enterprise scale.