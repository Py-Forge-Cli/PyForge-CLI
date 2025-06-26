#!/usr/bin/env python3
"""
Kaggle API Downloads Script for PyForge CLI Test Datasets
Downloads all Kaggle datasets from the configuration file
"""

import json
import os
import sys
import time
import hashlib
import shutil
from pathlib import Path

def load_config():
    """Load the datasets configuration file"""
    config_path = Path(__file__).parent / "datasets-config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def check_kagglehub_installation():
    """Check if kagglehub is installed and available"""
    try:
        import kagglehub
        return True, kagglehub
    except ImportError:
        return False, None

def install_kagglehub():
    """Install kagglehub if not available"""
    import subprocess
    try:
        print("📦 Installing kagglehub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kagglehub"])
        import kagglehub
        return True, kagglehub
    except Exception as e:
        print(f"❌ Failed to install kagglehub: {e}")
        return False, None

def create_output_directory(base_dir="collected-datasets"):
    """Create organized output directory structure"""
    base_path = Path(base_dir)
    
    # Create format-specific directories
    formats = ["pdf", "excel", "xml", "access", "dbf", "mdf", "csv"]
    size_categories = ["small", "medium", "large"]
    
    for format_name in formats:
        format_path = base_path / format_name
        for size in size_categories:
            (format_path / size).mkdir(parents=True, exist_ok=True)
    
    # Create metadata directory
    (base_path / "metadata").mkdir(parents=True, exist_ok=True)
    
    return base_path

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of downloaded file"""
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

def calculate_directory_size(directory):
    """Calculate total size of all files in directory"""
    total_size = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    return total_size

def move_and_organize_files(download_path, target_path, dataset):
    """Move downloaded files to organized structure"""
    if not download_path.exists():
        return [], 0
    
    moved_files = []
    total_size = 0
    
    # Create target directory
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    if download_path.is_file():
        # Single file - move directly
        shutil.move(str(download_path), str(target_path))
        file_size = get_file_size(target_path)
        moved_files.append({
            "original_path": str(download_path),
            "new_path": str(target_path),
            "size": file_size,
            "sha256": calculate_file_hash(target_path)
        })
        total_size = file_size
    else:
        # Directory - find the primary file based on format and move it to target location
        main_file_found = False
        
        for item in download_path.iterdir():
            if item.is_file():
                # Special handling for NYC taxi dataset - only keep 2016-03 file
                if dataset['id'] == 'nyc-taxi' and 'yellow_tripdata_2016-03.csv' not in item.name:
                    print(f"    Skipping {item.name} (keeping only 2016-03 data)")
                    continue
                
                # Check if this is the main file we want based on extension
                is_main_file = False
                if dataset["format"] == "Excel" and item.suffix.lower() in ['.xlsx', '.xls']:
                    is_main_file = True
                elif dataset["format"] == "XML" and item.suffix.lower() == '.xml':
                    is_main_file = True
                elif dataset["format"] == "CSV" and item.suffix.lower() == '.csv':
                    is_main_file = True
                
                if is_main_file and not main_file_found:
                    # Move the main file to the target location
                    shutil.move(str(item), str(target_path))
                    file_size = get_file_size(target_path)
                    moved_files.append({
                        "original_path": str(item),
                        "new_path": str(target_path),
                        "size": file_size,
                        "sha256": calculate_file_hash(target_path)
                    })
                    total_size += file_size
                    main_file_found = True
                    print(f"    📁 Moved main file: {item.name} -> {target_path.name}")
                else:
                    # Move additional files to a subdirectory for reference
                    extra_dir = target_path.parent / f"{dataset['id']}_extra"
                    extra_dir.mkdir(exist_ok=True)
                    target_file = extra_dir / item.name
                    shutil.move(str(item), str(target_file))
                    file_size = get_file_size(target_file)
                    moved_files.append({
                        "original_path": str(item),
                        "new_path": str(target_file),
                        "size": file_size,
                        "sha256": calculate_file_hash(target_file)
                    })
                    total_size += file_size
                    print(f"    📄 Moved extra file: {item.name} -> {target_file}")
        
        # If no main file was found, report an error
        if not main_file_found:
            print(f"    ⚠️  No suitable {dataset['format']} file found in downloaded content")
        
        # Remove empty download directory
        if download_path.exists():
            shutil.rmtree(download_path)
    
    return moved_files, total_size

def download_kaggle_dataset(dataset, kagglehub, base_path):
    """
    Download a single Kaggle dataset
    
    Args:
        dataset: Dataset configuration
        kagglehub: Kaggle hub module
        base_path: Base output directory
        
    Returns:
        dict: Download result with success status and metadata
    """
    try:
        print(f"  Downloading from Kaggle: {dataset['kaggle_id']}")
        start_time = time.time()
        
        # Download using kagglehub
        download_path = kagglehub.dataset_download(dataset['kaggle_id'])
        download_path = Path(download_path)
        
        print(f"  Downloaded to: {download_path}")
        
        # Generate target path
        format_name = dataset["format"].lower()
        size_category = dataset["size_category"].lower()
        target_filename = f"{dataset['id']}"
        
        # Add appropriate extension based on format
        if dataset["format"] == "Excel":
            target_filename += ".xlsx"
        elif dataset["format"] == "XML":
            target_filename += ".xml"
        elif dataset["format"] == "CSV":
            target_filename += ".csv"
        
        target_path = base_path / format_name / size_category / target_filename
        
        # Move and organize files
        moved_files, total_size = move_and_organize_files(download_path, target_path, dataset)
        
        duration = time.time() - start_time
        
        # Check if we successfully moved at least one file
        success = len(moved_files) > 0 and target_path.exists()
        
        if not success:
            return {
                "success": False,
                "error": f"No files were successfully organized for {dataset['id']}",
                "download_path": str(download_path),
                "moved_files": moved_files,
                "duration_seconds": duration
            }
        
        return {
            "success": True,
            "download_path": str(download_path),
            "moved_files": moved_files,
            "total_size_bytes": total_size,
            "total_size_formatted": format_size(total_size),
            "duration_seconds": duration,
            "target_file": str(target_path),
            "error": None
        }
        
    except Exception as e:
        error_msg = f"Kaggle download error: {str(e)}"
        print(f"  ❌ Error: {error_msg}")
        return {"success": False, "error": error_msg}

def get_kaggle_credentials_status():
    """Check Kaggle API credentials status"""
    kaggle_dir = Path.home() / ".kaggle"
    credentials_file = kaggle_dir / "kaggle.json"
    
    if not credentials_file.exists():
        return False, "Kaggle credentials not found"
    
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
            if 'username' in creds and 'key' in creds:
                return True, f"Credentials found for user: {creds['username']}"
            else:
                return False, "Invalid credentials format"
    except Exception as e:
        return False, f"Error reading credentials: {e}"

def download_kaggle_datasets():
    """Main function to download all Kaggle datasets"""
    print("🚀 PyForge CLI Test Datasets - Kaggle Downloads")
    print("=" * 50)
    
    # Check kagglehub installation
    has_kagglehub, kagglehub = check_kagglehub_installation()
    if not has_kagglehub:
        print("📦 kagglehub not found, attempting to install...")
        has_kagglehub, kagglehub = install_kagglehub()
        if not has_kagglehub:
            print("❌ Failed to install kagglehub. Please install manually: pip install kagglehub")
            return False
    
    print("✅ kagglehub is available")
    
    # Check Kaggle credentials
    has_creds, creds_msg = get_kaggle_credentials_status()
    print(f"🔑 Kaggle credentials: {creds_msg}")
    
    if not has_creds:
        print("❌ Kaggle API credentials required. Please set up:")
        print("   1. Go to https://www.kaggle.com/account")
        print("   2. Create new API token")
        print("   3. Place kaggle.json in ~/.kaggle/")
        print("   4. Or set KAGGLE_USERNAME and KAGGLE_KEY environment variables")
        return False
    
    # Load configuration
    config = load_config()
    kaggle_datasets = config["datasets"]["kaggle_datasets"]
    
    print(f"📊 Found {len(kaggle_datasets)} Kaggle datasets")
    
    # Create output directory
    base_path = create_output_directory()
    print(f"📁 Output directory: {base_path.absolute()}")
    print()
    
    # Download results tracking
    results = []
    successful_downloads = 0
    failed_downloads = 0
    
    # Download each dataset
    for i, dataset in enumerate(kaggle_datasets, 1):
        print(f"[{i}/{len(kaggle_datasets)}] {dataset['name']}")
        print(f"  Format: {dataset['format']} | Size: {dataset['size']} | Category: {dataset['size_category']}")
        print(f"  Kaggle ID: {dataset['kaggle_id']}")
        
        # Download the dataset
        result = download_kaggle_dataset(dataset, kagglehub, base_path)
        result["dataset_id"] = dataset["id"]
        
        # Track results
        results.append({
            "dataset": dataset,
            "result": result
        })
        
        if result["success"]:
            successful_downloads += 1
            print(f"  ✅ Downloaded: {result['total_size_formatted']} ({len(result['moved_files'])} files) in {result['duration_seconds']:.1f}s")
        else:
            failed_downloads += 1
        
        print()
        
        # Small delay between downloads to be respectful
        time.sleep(2)
    
    # Generate download report
    print("📋 Download Summary")
    print("=" * 30)
    print(f"✅ Successful: {successful_downloads}")
    print(f"❌ Failed: {failed_downloads}")
    print(f"📊 Total: {len(kaggle_datasets)}")
    print()
    
    # Save detailed results
    results_file = base_path / "metadata" / "kaggle_downloads_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "summary": {
                "total": len(kaggle_datasets),
                "successful": successful_downloads,
                "failed": failed_downloads
            },
            "results": results
        }, f, indent=2)
    
    print(f"📄 Detailed results saved to: {results_file}")
    
    # Generate checksums file for moved files
    checksums_file = base_path / "metadata" / "kaggle_checksums.sha256"
    with open(checksums_file, 'w') as f:
        for result_entry in results:
            if result_entry["result"]["success"]:
                for file_info in result_entry["result"]["moved_files"]:
                    relative_path = Path(file_info["new_path"]).relative_to(base_path)
                    f.write(f"{file_info['sha256']}  {relative_path}\\n")
    
    print(f"🔐 Checksums saved to: {checksums_file}")
    
    return successful_downloads == len(kaggle_datasets)

if __name__ == "__main__":
    try:
        success = download_kaggle_datasets()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n❌ Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)