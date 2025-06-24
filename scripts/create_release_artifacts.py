#!/usr/bin/env python3
"""
Release Artifacts Creation Script for PyForge CLI Test Datasets
Packages collected datasets into organized ZIP archives for GitHub releases
"""

import json
import os
import sys
import time
import argparse
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, List, Any

def load_config():
    """Load the datasets configuration file"""
    config_path = Path(__file__).parent / "datasets-config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def format_size(size_bytes):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"

def collect_dataset_files(base_path):
    """Collect all dataset files organized by format and size"""
    base_path = Path(base_path)
    collected = {}
    
    formats = ["pdf", "excel", "xml", "access", "dbf", "mdf", "csv"]
    size_categories = ["small", "medium", "large"]
    
    for format_name in formats:
        collected[format_name] = {}
        format_path = base_path / format_name
        
        if not format_path.exists():
            continue
            
        for size_category in size_categories:
            size_path = format_path / size_category
            collected[format_name][size_category] = []
            
            if not size_path.exists():
                continue
                
            for file_path in size_path.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    file_info = {
                        "path": str(file_path),
                        "relative_path": str(file_path.relative_to(base_path)),
                        "name": file_path.name,
                        "size_bytes": get_file_size(file_path),
                        "size_formatted": format_size(get_file_size(file_path)),
                        "sha256": calculate_file_hash(file_path)
                    }
                    collected[format_name][size_category].append(file_info)
    
    return collected

def create_format_archive(format_name, files_data, output_dir, include_large=False):
    """Create ZIP archive for a specific format"""
    output_path = Path(output_dir) / f"{format_name}-samples.zip"
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        total_files = 0
        total_size = 0
        
        for size_category, files in files_data.items():
            if not include_large and size_category == "large":
                continue
                
            if not files:
                continue
                
            # Create size category directory in ZIP
            size_dir = f"{format_name}/{size_category}/"
            zf.writestr(size_dir, "")
            
            # Add metadata for size category
            metadata = {
                "size_category": size_category,
                "file_count": len(files),
                "total_size_bytes": sum(f["size_bytes"] for f in files),
                "files": [
                    {
                        "name": f["name"],
                        "size_bytes": f["size_bytes"],
                        "size_formatted": f["size_formatted"],
                        "sha256": f["sha256"]
                    }
                    for f in files
                ]
            }
            
            metadata_path = f"{format_name}/{size_category}/metadata.json"
            zf.writestr(metadata_path, json.dumps(metadata, indent=2))
            
            # Add actual files
            for file_info in files:
                file_path = Path(file_info["path"])
                if file_path.exists():
                    archive_path = f"{format_name}/{size_category}/{file_info['name']}"
                    zf.write(file_path, archive_path)
                    total_files += 1
                    total_size += file_info["size_bytes"]
    
    archive_size = get_file_size(output_path)
    archive_hash = calculate_file_hash(output_path)
    
    return {
        "archive_path": str(output_path),
        "archive_name": output_path.name,
        "archive_size_bytes": archive_size,
        "archive_size_formatted": format_size(archive_size),
        "archive_sha256": archive_hash,
        "content_files": total_files,
        "content_size_bytes": total_size,
        "content_size_formatted": format_size(total_size)
    }

def create_combined_archive(all_files_data, output_dir, include_large=False):
    """Create combined archive with all formats"""
    output_path = Path(output_dir) / "all-formats.zip"
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        total_files = 0
        total_size = 0
        
        for format_name, format_data in all_files_data.items():
            if not any(format_data.values()):
                continue
                
            for size_category, files in format_data.items():
                if not include_large and size_category == "large":
                    continue
                    
                if not files:
                    continue
                
                # Create directory structure
                size_dir = f"{format_name}/{size_category}/"
                zf.writestr(size_dir, "")
                
                # Add files
                for file_info in files:
                    file_path = Path(file_info["path"])
                    if file_path.exists():
                        archive_path = f"{format_name}/{size_category}/{file_info['name']}"
                        zf.write(file_path, archive_path)
                        total_files += 1
                        total_size += file_info["size_bytes"]
        
        # Add overall README
        readme_content = f"""# PyForge CLI Sample Datasets

This archive contains curated test datasets for all PyForge CLI supported formats.

## Directory Structure

```
{format_name}/
├── small/          # Files <100MB
├── medium/         # Files 100MB-1GB
{"└── large/          # Files >1GB" if include_large else ""}
```

## Formats Included

- **PDF**: Government documents and technical reports
- **Excel**: Multi-sheet business and analytical data  
- **XML**: RSS feeds, patents, and bibliographic data
- **Access**: Sample business databases
- **DBF**: Geographic and census data
- **MDF**: SQL Server sample databases
- **CSV**: Classic machine learning and business datasets

## Usage

```bash
# Convert PDF files
pyforge convert pdf/small/*.pdf

# Convert Excel files
pyforge convert excel/small/*.xlsx

# Convert XML files  
pyforge convert xml/small/*.xml

# Convert database files
pyforge convert access/small/*.mdb
pyforge convert dbf/small/*.dbf

# Convert CSV files
pyforge convert csv/small/*.csv
```

## File Integrity

All files include SHA256 checksums in metadata.json files within each size category directory.

## Licensing

All datasets are from public domain or open license sources. See individual metadata for specific licensing information.

Generated: {time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}
"""
        zf.writestr("README.md", readme_content)
    
    archive_size = get_file_size(output_path)
    archive_hash = calculate_file_hash(output_path)
    
    return {
        "archive_path": str(output_path),
        "archive_name": output_path.name,
        "archive_size_bytes": archive_size,
        "archive_size_formatted": format_size(archive_size),
        "archive_sha256": archive_hash,
        "content_files": total_files,
        "content_size_bytes": total_size,
        "content_size_formatted": format_size(total_size)
    }

def load_download_results(base_path):
    """Load download results from metadata files"""
    metadata_dir = Path(base_path) / "metadata"
    results = {
        "direct_downloads": {},
        "kaggle_downloads": {},
        "errors": []
    }
    
    # Load direct download results
    direct_results_file = metadata_dir / "direct_downloads_results.json"
    if direct_results_file.exists():
        try:
            with open(direct_results_file, 'r') as f:
                data = json.load(f)
                results["direct_downloads"] = data
        except Exception as e:
            results["errors"].append(f"Failed to load direct download results: {e}")
    
    # Load Kaggle download results
    kaggle_results_file = metadata_dir / "kaggle_downloads_results.json"
    if kaggle_results_file.exists():
        try:
            with open(kaggle_results_file, 'r') as f:
                data = json.load(f)
                results["kaggle_downloads"] = data
        except Exception as e:
            results["errors"].append(f"Failed to load Kaggle download results: {e}")
    
    return results

def create_manifest(config, all_files_data, download_results, archives_info, version, include_large):
    """Create comprehensive manifest file"""
    
    # Calculate totals
    total_files = 0
    total_size_bytes = 0
    format_summary = {}
    
    for format_name, format_data in all_files_data.items():
        format_files = 0
        format_size_bytes = 0
        
        for size_category, files in format_data.items():
            if not include_large and size_category == "large":
                continue
            format_files += len(files)
            format_size_bytes += sum(f["size_bytes"] for f in files)
        
        format_summary[format_name] = {
            "file_count": format_files,
            "total_size_bytes": format_size_bytes,
            "total_size_formatted": format_size(format_size_bytes)
        }
        
        total_files += format_files
        total_size_bytes += format_size_bytes
    
    manifest = {
        "version": version,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "include_large_datasets": include_large,
        "summary": {
            "total_files": total_files,
            "total_size_bytes": total_size_bytes,
            "total_size_formatted": format_size(total_size_bytes),
            "format_count": len([f for f in format_summary.values() if f["file_count"] > 0])
        },
        "formats": format_summary,
        "archives": archives_info,
        "download_results": {
            "direct_downloads": download_results.get("direct_downloads", {}).get("summary", {}),
            "kaggle_downloads": download_results.get("kaggle_downloads", {}).get("summary", {}),
            "errors": download_results.get("errors", [])
        },
        "dataset_sources": {
            "configuration_version": config["version"],
            "total_configured": len(config["datasets"]["direct_downloads"]) + len(config["datasets"]["kaggle_datasets"]),
            "direct_downloads": len(config["datasets"]["direct_downloads"]),
            "kaggle_datasets": len(config["datasets"]["kaggle_datasets"])
        },
        "size_categories": config["size_categories"],
        "supported_formats": config["formats_supported"]
    }
    
    return manifest

def create_release_artifacts(version="v1.0.0", include_large=False):
    """Main function to create all release artifacts"""
    print(f"🚀 PyForge CLI Dataset Release Artifacts Creator")
    print(f"Version: {version}")
    print(f"Include Large Datasets: {include_large}")
    print("=" * 60)
    
    # Setup paths
    base_path = Path("collected-datasets")
    output_dir = base_path
    
    if not base_path.exists():
        print(f"❌ Dataset directory not found: {base_path}")
        return False
    
    # Load configuration
    config = load_config()
    print(f"📋 Loaded configuration: {config['version']}")
    
    # Collect all files
    print("🔍 Collecting dataset files...")
    all_files_data = collect_dataset_files(base_path)
    
    # Load download results
    print("📊 Loading download results...")
    download_results = load_download_results(base_path)
    
    # Create format-specific archives
    print("📦 Creating format-specific archives...")
    archives_info = {}
    
    for format_name, format_data in all_files_data.items():
        if any(any(size_files) for size_files in format_data.values()):
            print(f"  Creating {format_name}-samples.zip...")
            archive_info = create_format_archive(format_name, format_data, output_dir, include_large)
            archives_info[format_name] = archive_info
            print(f"    ✅ {archive_info['content_files']} files, {archive_info['archive_size_formatted']}")
    
    # Create combined archive
    print("📦 Creating combined archive...")
    combined_info = create_combined_archive(all_files_data, output_dir, include_large)
    archives_info["all_formats"] = combined_info
    print(f"    ✅ {combined_info['content_files']} files, {combined_info['archive_size_formatted']}")
    
    # Create manifest
    print("📄 Creating manifest...")
    manifest = create_manifest(config, all_files_data, download_results, archives_info, version, include_large)
    
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"    ✅ Manifest saved: {manifest_path}")
    
    # Summary
    print("\n📋 Release Summary")
    print("=" * 30)
    print(f"Version: {version}")
    print(f"Total Files: {manifest['summary']['total_files']}")
    print(f"Total Size: {manifest['summary']['total_size_formatted']}")
    print(f"Archives Created: {len(archives_info)}")
    print()
    
    print("📦 Archive Details:")
    for name, info in archives_info.items():
        print(f"  {info['archive_name']}: {info['archive_size_formatted']} ({info['content_files']} files)")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Create PyForge CLI dataset release artifacts")
    parser.add_argument("--version", default="v1.0.0", help="Release version")
    parser.add_argument("--include-large", type=str, default="false", 
                        help="Include large datasets (true/false)")
    
    args = parser.parse_args()
    
    # Convert string to boolean
    include_large = args.include_large.lower() in ('true', '1', 'yes', 'on')
    
    try:
        success = create_release_artifacts(args.version, include_large)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Creation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()