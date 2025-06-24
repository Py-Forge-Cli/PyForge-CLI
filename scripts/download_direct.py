#!/usr/bin/env python3
"""
Direct HTTP Downloads Script for PyForge CLI Test Datasets
Downloads all direct HTTP datasets from the configuration file
"""

import json
import os
import sys
import time
import hashlib
import ssl
import certifi
import zipfile
import shutil
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

def load_config():
    """Load the datasets configuration file"""
    config_path = Path(__file__).parent / "datasets-config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

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

def extract_dbf_from_zip(zip_path, output_dir, dataset):
    """
    Extract DBF files from ZIP archives for Census TIGER data
    
    Args:
        zip_path: Path to downloaded ZIP file
        output_dir: Directory to extract DBF files to
        dataset: Dataset configuration
        
    Returns:
        list: Extracted DBF file paths
    """
    extracted_files = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List all files in ZIP
            zip_contents = zip_ref.namelist()
            
            # Find DBF files
            dbf_files = [f for f in zip_contents if f.lower().endswith('.dbf')]
            
            if not dbf_files:
                print(f"  ⚠️  No DBF files found in {zip_path}")
                return extracted_files
            
            print(f"  📦 Extracting {len(dbf_files)} DBF files from ZIP...")
            
            # Extract each DBF file
            for dbf_file in dbf_files:
                # Extract to output directory
                zip_ref.extract(dbf_file, output_dir)
                extracted_path = output_dir / dbf_file
                
                # Create a better filename for the main DBF
                if len(dbf_files) == 1:
                    # Single DBF file - rename to dataset ID
                    final_path = output_dir / f"{dataset['id']}.dbf"
                    if extracted_path != final_path:
                        extracted_path.rename(final_path)
                        extracted_path = final_path
                
                extracted_files.append(extracted_path)
                print(f"    ✅ {extracted_path.name}")
        
        # Remove the original ZIP file to save space
        zip_path.unlink()
        
    except zipfile.BadZipFile:
        print(f"  ❌ Invalid ZIP file: {zip_path}")
    except Exception as e:
        print(f"  ❌ ZIP extraction error: {e}")
    
    return extracted_files

def download_file(url, output_path, chunk_size=8192, timeout=30, max_retries=3):
    """
    Download a file from URL with progress indication and error handling
    
    Args:
        url: URL to download from
        output_path: Path to save the file
        chunk_size: Size of chunks to download (default 8KB)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        
    Returns:
        dict: Download result with success status and metadata
    """
    last_error = None
    
    print(f"  🌐 Downloading from: {url}")
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"  Retry attempt {attempt + 1}/{max_retries}")
                time.sleep(2 ** attempt)  # Exponential backoff
            
            # Create SSL context with proper certificate verification
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            
            # Create request with user agent and additional headers for better compatibility
            req = Request(url, headers={
                'User-Agent': 'PyForge-CLI-Dataset-Collector/1.0 (Python urllib)',
                'Accept': '*/*',
                'Accept-Encoding': 'identity',
                'Connection': 'close'
            })
            
            if attempt == 0:  # Only print on first attempt
                print(f"  Downloading: {url}")
            start_time = time.time()
            
            with urlopen(req, timeout=timeout, context=ssl_context) as response:
                total_size = response.headers.get('Content-Length')
                if total_size:
                    total_size = int(total_size)
                    if attempt == 0:  # Only print size on first attempt
                        print(f"  Size: {format_size(total_size)}")
                
                downloaded = 0
                with open(output_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress indication
                        if total_size:
                            progress = (downloaded / total_size) * 100
                            print(f"\r  Progress: {progress:.1f}% ({format_size(downloaded)}/{format_size(total_size)})", end="", flush=True)
                        else:
                            print(f"\r  Downloaded: {format_size(downloaded)}", end="", flush=True)
            
            print()  # New line after progress
            duration = time.time() - start_time
            final_size = get_file_size(output_path)
            file_hash = calculate_file_hash(output_path)
            
            return {
                "success": True,
                "size_bytes": final_size,
                "size_formatted": format_size(final_size),
                "duration_seconds": duration,
                "sha256": file_hash,
                "error": None
            }
            
        except (HTTPError, URLError, Exception) as e:
            last_error = e
            if isinstance(e, HTTPError):
                error_msg = f"HTTP Error {e.code}: {e.reason}"
            elif isinstance(e, URLError):
                error_msg = f"URL Error: {e.reason}"
            else:
                error_msg = f"Unexpected error: {str(e)}"
            
            if attempt < max_retries - 1:
                print(f"  ⚠️  {error_msg} - retrying...")
            else:
                print(f"  ❌ Error: {error_msg}")
                
            # Clean up partial download on failure
            if output_path.exists():
                output_path.unlink()
    
    # If we get here, all retries failed
    return {"success": False, "error": str(last_error)}

def get_output_path(dataset, base_path):
    """Generate output path for dataset based on format and size"""
    format_name = dataset["format"].lower()
    size_category = dataset["size_category"].lower()
    filename = dataset["filename"]
    
    return base_path / format_name / size_category / filename

def download_direct_datasets():
    """Main function to download all direct HTTP datasets"""
    print("🚀 PyForge CLI Test Datasets - Direct Downloads")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    direct_datasets = config["datasets"]["direct_downloads"]
    
    print(f"📊 Found {len(direct_datasets)} direct download datasets")
    
    # Create output directory
    base_path = create_output_directory()
    print(f"📁 Output directory: {base_path.absolute()}")
    print()
    
    # Download results tracking
    results = []
    successful_downloads = 0
    failed_downloads = 0
    
    # Download each dataset
    for i, dataset in enumerate(direct_datasets, 1):
        print(f"[{i}/{len(direct_datasets)}] {dataset['name']}")
        print(f"  Format: {dataset['format']} | Size: {dataset['size']} | Category: {dataset['size_category']}")
        
        # Generate output path
        output_path = get_output_path(dataset, base_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # For ZIP URLs, we download to a temporary ZIP file first
        if dataset.get("zip_url", False):
            # Download to temporary ZIP file
            zip_filename = dataset["url"].split("/")[-1]
            temp_zip_path = output_path.parent / zip_filename
            download_path = temp_zip_path
        else:
            download_path = output_path
        
        # Skip if final file already exists
        if output_path.exists():
            print(f"  ⏭️  File already exists: {output_path}")
            existing_size = get_file_size(output_path)
            results.append({
                "dataset": dataset,
                "result": {
                    "success": True,
                    "size_bytes": existing_size,
                    "size_formatted": format_size(existing_size),
                    "sha256": calculate_file_hash(output_path),
                    "skipped": True
                }
            })
            successful_downloads += 1
            print()
            continue
        
        # Download the file
        result = download_file(dataset["url"], download_path)
        result["dataset_id"] = dataset["id"]
        result["output_path"] = str(output_path)
        
        # Track results
        results.append({
            "dataset": dataset,
            "result": result
        })
        
        if result["success"]:
            # Handle ZIP extraction for zip_url datasets
            if dataset.get("zip_url", False):
                print(f"  ✅ Downloaded ZIP: {result['size_formatted']} in {result['duration_seconds']:.1f}s")
                
                # Extract DBF files from ZIP
                extracted_files = extract_dbf_from_zip(download_path, output_path.parent, dataset)
                
                if extracted_files:
                    # Find the main DBF file that matches our expected filename
                    main_dbf = None
                    for extracted_file in extracted_files:
                        if extracted_file.name == output_path.name:
                            main_dbf = extracted_file
                            break
                    
                    # If we can't find exact match, rename the first DBF file
                    if main_dbf is None:
                        main_dbf = extracted_files[0]
                        if main_dbf != output_path:
                            main_dbf.rename(output_path)
                            main_dbf = output_path
                    
                    # Update result to reflect the extracted DBF files
                    total_extracted_size = sum(get_file_size(f) for f in extracted_files if f.exists())
                    result["extracted_files"] = [str(f) for f in extracted_files]
                    result["extracted_count"] = len(extracted_files)
                    result["total_extracted_size"] = total_extracted_size
                    result["total_extracted_formatted"] = format_size(total_extracted_size)
                    
                    # Update the primary file info to point to the main DBF
                    result["size_bytes"] = get_file_size(main_dbf)
                    result["size_formatted"] = format_size(result["size_bytes"])
                    result["sha256"] = calculate_file_hash(main_dbf)
                    result["output_path"] = str(main_dbf)
                    
                    print(f"  📦 Extracted {len(extracted_files)} DBF files ({format_size(total_extracted_size)})")
                    print(f"  📄 Main file: {main_dbf.name}")
                else:
                    print(f"  ⚠️  No DBF files found in ZIP archive")
                    result["success"] = False
                    result["error"] = "No DBF files found in ZIP archive"
            else:
                print(f"  ✅ Downloaded: {result['size_formatted']} in {result['duration_seconds']:.1f}s")
            
            successful_downloads += 1
        else:
            failed_downloads += 1
            # Clean up failed download
            if download_path.exists():
                download_path.unlink()
            if output_path.exists():
                output_path.unlink()
        
        print()
        
        # Small delay between downloads to be respectful
        time.sleep(1)
    
    # Generate download report
    print("📋 Download Summary")
    print("=" * 30)
    print(f"✅ Successful: {successful_downloads}")
    print(f"❌ Failed: {failed_downloads}")
    print(f"📊 Total: {len(direct_datasets)}")
    print()
    
    # Save detailed results
    results_file = base_path / "metadata" / "direct_downloads_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "summary": {
                "total": len(direct_datasets),
                "successful": successful_downloads,
                "failed": failed_downloads
            },
            "results": results
        }, f, indent=2)
    
    print(f"📄 Detailed results saved to: {results_file}")
    
    # Generate checksums file
    checksums_file = base_path / "metadata" / "checksums.sha256"
    with open(checksums_file, 'w') as f:
        for result_entry in results:
            if result_entry["result"]["success"]:
                dataset = result_entry["dataset"]
                result = result_entry["result"]
                output_path = get_output_path(dataset, base_path)
                relative_path = output_path.relative_to(base_path)
                f.write(f"{result['sha256']}  {relative_path}\\n")
    
    print(f"🔐 Checksums saved to: {checksums_file}")
    
    return successful_downloads == len(direct_datasets)

if __name__ == "__main__":
    try:
        success = download_direct_datasets()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n❌ Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)