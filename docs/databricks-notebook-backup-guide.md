# Databricks Workspace Notebook Backup to Unity Catalog Volumes

This guide provides comprehensive information on backing up Databricks Workspace notebooks to Unity Catalog Volumes using CLI and SDK approaches.

## Overview

Backing up notebooks from Databricks Workspace to Unity Catalog Volumes involves two main steps:
1. Exporting notebooks from the Workspace
2. Uploading the exported notebooks to Unity Catalog Volumes

## Prerequisites

- Databricks CLI installed and configured
- Databricks SDK for Python (optional, for SDK approach)
- Databricks Runtime 13.3 LTS or above (required for Unity Catalog Volumes)
- Appropriate permissions for workspace access and volume write operations

## Method 1: Using Databricks CLI

### Step 1: Export Notebooks from Workspace

#### Export a Single Notebook
```bash
# Export in SOURCE format (default)
databricks workspace export /path/to/notebook ./local/path/notebook.py

# Export in JUPYTER format
databricks workspace export --format JUPYTER /path/to/notebook ./local/path/notebook.ipynb

# Export with overwrite
databricks workspace export --overwrite --format SOURCE /path/to/notebook ./local/path/notebook.py
```

#### Export an Entire Directory (Recommended for Backup)
```bash
# Export directory recursively
databricks workspace export_dir /workspace/folder ./local/backup/folder

# Export with overwrite option
databricks workspace export_dir --overwrite /workspace/folder ./local/backup/folder
```

### Step 2: Upload to Unity Catalog Volume

```bash
# Upload single file to volume
databricks fs cp ./local/path/notebook.py dbfs:/Volumes/catalog_name/schema_name/volume_name/backups/notebook.py

# Upload entire directory to volume
databricks fs cp -r ./local/backup/folder dbfs:/Volumes/catalog_name/schema_name/volume_name/backups/

# Upload with overwrite
databricks fs cp --overwrite ./local/path/notebook.py dbfs:/Volumes/catalog_name/schema_name/volume_name/backups/notebook.py
```

## Method 2: Using Databricks SDK for Python

### Complete Python Script for Backup

```python
#!/usr/bin/env python3
"""
Databricks Notebook Backup Script
Backs up workspace notebooks to Unity Catalog Volumes
"""

import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace

class NotebookBackup:
    def __init__(self, profile="DEFAULT"):
        self.w = WorkspaceClient(profile=profile)
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_notebook(self, notebook_path, format="SOURCE"):
        """Export a single notebook from workspace"""
        try:
            content = self.w.workspace.export(
                path=notebook_path,
                format=getattr(workspace.ExportFormat, format)
            )
            return content.content
        except Exception as e:
            print(f"Error exporting {notebook_path}: {e}")
            return None
    
    def list_notebooks(self, path, recursive=True):
        """List all notebooks in a workspace path"""
        notebooks = []
        try:
            objects = self.w.workspace.list(path=path)
            for obj in objects:
                if obj.object_type == workspace.ObjectType.NOTEBOOK:
                    notebooks.append(obj.path)
                elif obj.object_type == workspace.ObjectType.DIRECTORY and recursive:
                    notebooks.extend(self.list_notebooks(obj.path, recursive))
        except Exception as e:
            print(f"Error listing notebooks in {path}: {e}")
        return notebooks
    
    def backup_to_volume(self, workspace_path, volume_path, format="SOURCE"):
        """Backup notebooks from workspace to Unity Catalog volume"""
        # List all notebooks
        notebooks = self.list_notebooks(workspace_path)
        print(f"Found {len(notebooks)} notebooks to backup")
        
        # Create backup metadata
        backup_metadata = {
            "timestamp": self.backup_timestamp,
            "source_path": workspace_path,
            "volume_path": volume_path,
            "notebooks": []
        }
        
        # Export and upload each notebook
        with tempfile.TemporaryDirectory() as temp_dir:
            for notebook_path in notebooks:
                print(f"Backing up: {notebook_path}")
                
                # Export notebook
                content = self.export_notebook(notebook_path, format)
                if content:
                    # Determine file extension based on format
                    ext_map = {
                        "SOURCE": self._get_source_extension(notebook_path),
                        "JUPYTER": ".ipynb",
                        "HTML": ".html",
                        "DBC": ".dbc"
                    }
                    extension = ext_map.get(format, "")
                    
                    # Create relative path for backup
                    relative_path = notebook_path.replace(workspace_path, "").lstrip("/")
                    backup_file_name = f"{relative_path}{extension}"
                    
                    # Save to temp file
                    temp_file = Path(temp_dir) / backup_file_name
                    temp_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Decode base64 content and write
                    import base64
                    decoded_content = base64.b64decode(content)
                    temp_file.write_bytes(decoded_content)
                    
                    # Upload to volume
                    volume_file_path = f"{volume_path}/{self.backup_timestamp}/{backup_file_name}"
                    try:
                        self.w.files.upload(volume_file_path, temp_file.read_bytes())
                        backup_metadata["notebooks"].append({
                            "source": notebook_path,
                            "backup": volume_file_path,
                            "size": len(decoded_content)
                        })
                        print(f"  ✓ Backed up to: {volume_file_path}")
                    except Exception as e:
                        print(f"  ✗ Failed to upload: {e}")
            
            # Save backup metadata
            metadata_path = f"{volume_path}/{self.backup_timestamp}/backup_metadata.json"
            self.w.files.upload(metadata_path, json.dumps(backup_metadata, indent=2))
            print(f"\nBackup metadata saved to: {metadata_path}")
        
        return backup_metadata
    
    def _get_source_extension(self, notebook_path):
        """Get file extension for SOURCE format based on notebook language"""
        try:
            # Get notebook info to determine language
            obj = self.w.workspace.get_status(notebook_path)
            language_extensions = {
                workspace.Language.PYTHON: ".py",
                workspace.Language.SCALA: ".scala",
                workspace.Language.SQL: ".sql",
                workspace.Language.R: ".r"
            }
            return language_extensions.get(obj.language, ".txt")
        except:
            return ".txt"
    
    def restore_from_volume(self, volume_backup_path, target_workspace_path):
        """Restore notebooks from volume backup to workspace"""
        # Read backup metadata
        metadata_path = f"{volume_backup_path}/backup_metadata.json"
        try:
            metadata_content = self.w.files.download(metadata_path).contents
            metadata = json.loads(metadata_content.decode())
            
            print(f"Restoring backup from: {metadata['timestamp']}")
            print(f"Original source: {metadata['source_path']}")
            
            for notebook_info in metadata["notebooks"]:
                source_path = notebook_info["source"]
                backup_path = notebook_info["backup"]
                
                # Calculate target path
                relative_path = source_path.replace(metadata["source_path"], "").lstrip("/")
                target_path = f"{target_workspace_path}/{relative_path}"
                
                print(f"Restoring: {target_path}")
                
                # Download from volume
                content = self.w.files.download(backup_path).contents
                
                # Import to workspace
                self.w.workspace.import_(
                    path=target_path,
                    content=base64.b64encode(content).decode(),
                    format=workspace.ImportFormat.AUTO,
                    overwrite=True
                )
                print(f"  ✓ Restored: {target_path}")
                
        except Exception as e:
            print(f"Error during restore: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize backup client
    backup = NotebookBackup(profile="DEFAULT")
    
    # Backup notebooks
    backup_metadata = backup.backup_to_volume(
        workspace_path="/Users/user@company.com/projects",
        volume_path="/Volumes/catalog/schema/backup_volume/notebook_backups",
        format="SOURCE"
    )
    
    # Restore notebooks (example)
    # backup.restore_from_volume(
    #     volume_backup_path="/Volumes/catalog/schema/backup_volume/notebook_backups/20240115_120000",
    #     target_workspace_path="/Users/user@company.com/restored_notebooks"
    # )
```

## Method 3: Hybrid Approach with Shell Script

### Backup Script (backup_notebooks.sh)

```bash
#!/bin/bash

# Configuration
WORKSPACE_PATH="/Users/user@company.com/notebooks"
VOLUME_PATH="dbfs:/Volumes/catalog/schema/volume/backups"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
LOCAL_TEMP="/tmp/notebook_backup_${BACKUP_DATE}"

# Create local temp directory
mkdir -p "${LOCAL_TEMP}"

# Export notebooks from workspace
echo "Exporting notebooks from workspace..."
databricks workspace export_dir --overwrite "${WORKSPACE_PATH}" "${LOCAL_TEMP}"

# Create backup directory in volume
echo "Creating backup directory in volume..."
databricks fs mkdirs "${VOLUME_PATH}/${BACKUP_DATE}"

# Upload to volume
echo "Uploading notebooks to volume..."
databricks fs cp -r "${LOCAL_TEMP}" "${VOLUME_PATH}/${BACKUP_DATE}/"

# Create backup metadata
echo "Creating backup metadata..."
cat > "${LOCAL_TEMP}/backup_info.json" <<EOF
{
  "backup_date": "${BACKUP_DATE}",
  "source_path": "${WORKSPACE_PATH}",
  "volume_path": "${VOLUME_PATH}/${BACKUP_DATE}",
  "notebook_count": $(find "${LOCAL_TEMP}" -type f | wc -l)
}
EOF

# Upload metadata
databricks fs cp "${LOCAL_TEMP}/backup_info.json" "${VOLUME_PATH}/${BACKUP_DATE}/"

# Cleanup
rm -rf "${LOCAL_TEMP}"

echo "Backup completed: ${VOLUME_PATH}/${BACKUP_DATE}"
```

## Best Practices

### 1. Backup Strategy
- Schedule regular backups (daily/weekly)
- Implement rotation policy to manage storage
- Keep multiple backup versions
- Test restore procedures regularly

### 2. Organization
```
/Volumes/catalog/schema/backup_volume/
├── notebook_backups/
│   ├── 20240115_120000/
│   │   ├── backup_metadata.json
│   │   ├── project1/
│   │   │   ├── notebook1.py
│   │   │   └── notebook2.py
│   │   └── project2/
│   │       └── analysis.py
│   └── 20240116_120000/
│       └── ...
```

### 3. Metadata Tracking
Always save backup metadata including:
- Timestamp
- Source paths
- Number of notebooks
- Backup format
- User who initiated backup

### 4. Security Considerations
- Use appropriate IAM roles and permissions
- Encrypt sensitive notebooks
- Audit backup access
- Implement retention policies

## Limitations and Considerations

1. **Runtime Requirements**: Unity Catalog Volumes require Databricks Runtime 13.3 LTS or above

2. **Format Considerations**:
   - SOURCE format preserves code but loses some notebook metadata
   - JUPYTER format preserves more metadata but may have compatibility issues
   - DBC format is Databricks-specific archive format

3. **Size Limitations**: Consider volume storage limits and costs for large notebook collections

4. **Performance**: For large workspace exports, consider:
   - Parallel exports for different directories
   - Incremental backups
   - Compression before upload

## Automation Example

### Scheduled Backup Job

```python
# Databricks Job Configuration (JSON)
{
  "name": "Notebook Backup Job",
  "tasks": [{
    "task_key": "backup_notebooks",
    "python_wheel_task": {
      "package_name": "notebook_backup",
      "entry_point": "backup_all"
    },
    "libraries": [{
      "pypi": {
        "package": "databricks-sdk"
      }
    }]
  }],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "UTC"
  }
}
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Verify workspace access permissions
   - Check Unity Catalog volume write permissions
   - Ensure proper authentication

2. **Export Failures**
   - Check notebook path exists
   - Verify format compatibility
   - Review notebook size limits

3. **Upload Failures**
   - Verify volume path format (dbfs:/ prefix)
   - Check volume exists and is accessible
   - Monitor storage quotas

### Debug Commands

```bash
# List workspace contents
databricks workspace list /path/to/notebooks

# Check volume access
databricks fs ls dbfs:/Volumes/catalog/schema/volume/

# Test single file upload
echo "test" > test.txt
databricks fs cp test.txt dbfs:/Volumes/catalog/schema/volume/test.txt
```

## Conclusion

Backing up Databricks notebooks to Unity Catalog Volumes provides a robust solution for disaster recovery and version control. Choose the method that best fits your automation needs and organizational requirements.