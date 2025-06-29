"""Sample datasets installer for PyForge CLI."""

import json
import os
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from rich import box
import hashlib
import time

console = Console()

class SampleDatasetsInstaller:
    """Installer for PyForge CLI sample datasets from GitHub releases."""
    
    GITHUB_REPO = "Py-Forge-Cli/PyForge-CLI"
    GITHUB_API_BASE = "https://api.github.com/repos"
    RELEASE_API_URL = f"{GITHUB_API_BASE}/{GITHUB_REPO}/releases"
    
    def __init__(self, target_dir: Optional[Path] = None):
        """Initialize the installer.
        
        Args:
            target_dir: Directory to install datasets to. Defaults to ./sample-datasets
        """
        self.target_dir = target_dir or Path.cwd() / "sample-datasets"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PyForge-CLI-SampleDatasets/1.0',
            'Accept': 'application/vnd.github.v3+json'
        })
    
    def list_available_releases(self) -> List[Dict]:
        """List all available dataset releases."""
        try:
            response = self.session.get(self.RELEASE_API_URL)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            console.print(f"[red]Error fetching releases: {e}[/red]")
            return []
    
    def get_latest_release(self) -> Optional[Dict]:
        """Get the latest dataset release."""
        releases = self.list_available_releases()
        if not releases:
            return None
        return releases[0]
    
    def get_release_by_version(self, version: str) -> Optional[Dict]:
        """Get a specific release by version tag."""
        releases = self.list_available_releases()
        for release in releases:
            if release['tag_name'] == version:
                return release
        return None
    
    def display_available_releases(self) -> None:
        """Display table of available releases."""
        releases = self.list_available_releases()
        
        if not releases:
            console.print("[yellow]No dataset releases found.[/yellow]")
            return
        
        table = Table(title="Available Dataset Releases", box=box.ROUNDED)
        table.add_column("Version", style="cyan", no_wrap=True)
        table.add_column("Published", style="dim")
        table.add_column("Assets", justify="right")
        table.add_column("Size", justify="right")
        
        for release in releases:
            # Calculate total size of assets
            total_size = sum(asset['size'] for asset in release.get('assets', []))
            size_mb = total_size / (1024 * 1024)
            
            # Format published date
            pub_date = release['published_at'][:10] if release.get('published_at') else 'N/A'
            
            table.add_row(
                release['tag_name'],
                pub_date,
                str(len(release.get('assets', []))),
                f"{size_mb:.1f} MB"
            )
        
        console.print(table)
    
    def download_file(self, url: str, filepath: Path, progress: Progress, task_id: TaskID) -> bool:
        """Download a file with progress tracking."""
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            progress.update(task_id, total=total_size)
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress.update(task_id, advance=len(chunk))
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error downloading {url}: {e}[/red]")
            return False
    
    def verify_checksum(self, filepath: Path, expected_hash: str) -> bool:
        """Verify SHA256 checksum of downloaded file."""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_hash = sha256_hash.hexdigest()
            return actual_hash.lower() == expected_hash.lower()
            
        except Exception as e:
            console.print(f"[red]Error verifying checksum for {filepath}: {e}[/red]")
            return False
    
    def extract_zip_file(self, zip_path: Path, extract_to: Path) -> bool:
        """Extract ZIP file to target directory."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return True
        except Exception as e:
            console.print(f"[red]Error extracting {zip_path}: {e}[/red]")
            return False
    
    def _create_minimal_datasets(self) -> bool:
        """Create minimal sample datasets when none are available from releases."""
        try:
            console.print("[yellow]Creating minimal sample datasets locally...[/yellow]")
            
            # Create directory structure
            csv_dir = self.target_dir / "csv" / "small"
            csv_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a simple CSV sample
            sample_csv = csv_dir / "sample_data.csv"
            csv_content = """id,name,category,value,date
1,Sample Item 1,Category A,100.50,2023-01-01
2,Sample Item 2,Category B,250.75,2023-01-02
3,Sample Item 3,Category A,175.25,2023-01-03
4,Sample Item 4,Category C,90.00,2023-01-04
5,Sample Item 5,Category B,320.80,2023-01-05"""
            
            with open(sample_csv, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            # Create XML directory and sample
            xml_dir = self.target_dir / "xml" / "small"
            xml_dir.mkdir(parents=True, exist_ok=True)
            
            sample_xml = xml_dir / "sample_data.xml"
            xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<data>
    <items>
        <item id="1">
            <name>Sample Item 1</name>
            <category>Category A</category>
            <value>100.50</value>
            <date>2023-01-01</date>
        </item>
        <item id="2">
            <name>Sample Item 2</name>
            <category>Category B</category>
            <value>250.75</value>
            <date>2023-01-02</date>
        </item>
    </items>
</data>"""
            
            with open(sample_xml, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            # Create README
            readme_path = self.target_dir / "README.md"
            readme_content = """# PyForge CLI Sample Datasets

## Overview
These are minimal sample datasets created locally for testing PyForge CLI.

## Available Datasets

### CSV Files
- `csv/small/sample_data.csv` - Simple tabular data with mixed types

### XML Files  
- `xml/small/sample_data.xml` - Structured XML data

## Notes
- These are basic samples created when full sample datasets are not available
- For complete sample datasets, check the PyForge CLI releases on GitHub
- Use `pyforge install sample-datasets --list-releases` to see available dataset releases
"""
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            console.print(f"[green]✓ Created minimal sample datasets in {self.target_dir}[/green]")
            console.print("[dim]Basic CSV and XML samples are now available for testing.[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error creating minimal datasets: {e}[/red]")
            return False
    
    def install_datasets(self, 
                        version: Optional[str] = None,
                        formats: Optional[List[str]] = None,
                        sizes: Optional[List[str]] = None,
                        force: bool = False) -> bool:
        """Install sample datasets.
        
        Args:
            version: Specific version to install (defaults to latest)
            formats: List of formats to install (e.g., ['pdf', 'excel'])
            sizes: List of sizes to install (e.g., ['small', 'medium'])
            force: Force overwrite existing files
            
        Returns:
            True if installation succeeded, False otherwise
        """
        
        # Get release info
        if version:
            release = self.get_release_by_version(version)
            if not release:
                console.print(f"[red]Release version '{version}' not found.[/red]")
                return False
        else:
            release = self.get_latest_release()
            if not release:
                console.print("[red]No releases found.[/red]")
                return False
        
        console.print(f"[bold]Installing datasets from release: {release['tag_name']}[/bold]")
        
        # Check if target directory exists
        if self.target_dir.exists() and not force:
            console.print(f"[yellow]Target directory {self.target_dir} already exists.[/yellow]")
            console.print("[yellow]Use --force to overwrite or choose a different path.[/yellow]")
            return False
        
        # Create target directory
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # Get assets to download
        assets = release.get('assets', [])
        if not assets:
            console.print(f"[yellow]No assets found in release {release['tag_name']}.[/yellow]")
            
            # Try to find a release with assets if this one is empty
            console.print("[dim]Looking for releases with sample datasets...[/dim]")
            all_releases = self.list_available_releases()
            for alt_release in all_releases:
                alt_assets = alt_release.get('assets', [])
                if alt_assets and any(a['name'].endswith('.zip') for a in alt_assets):
                    console.print(f"[green]Found datasets in release {alt_release['tag_name']}[/green]")
                    release = alt_release
                    assets = alt_assets
                    break
            
            if not assets:
                console.print("[red]No sample datasets found in any release.[/red]")
                console.print("[dim]Sample datasets may not be available yet. Check back later.[/dim]")
                return self._create_minimal_datasets()  # Create some basic sample files
        
        # Filter assets based on user preferences
        download_assets = []
        
        # Always download manifest and checksums
        for asset in assets:
            name = asset['name'].lower()
            if name in ['manifest.json', 'checksums.sha256']:
                download_assets.append(asset)
        
        # Add format-specific archives
        if not formats:
            # Download all formats if none specified
            download_assets.extend([a for a in assets if a['name'].endswith('.zip')])
        else:
            for fmt in formats:
                format_assets = [a for a in assets if fmt.lower() in a['name'].lower() and a['name'].endswith('.zip')]
                download_assets.extend(format_assets)
        
        if not download_assets:
            console.print("[yellow]No matching assets found to download.[/yellow]")
            console.print("[dim]Creating minimal sample datasets instead...[/dim]")
            return self._create_minimal_datasets()  # Create some basic sample files
        
        # Download assets with progress tracking
        with Progress() as progress:
            
            overall_task = progress.add_task(
                "[bold blue]Downloading datasets...", 
                total=len(download_assets)
            )
            
            downloaded_files = []
            
            for asset in download_assets:
                # Create download task
                file_task = progress.add_task(
                    f"[cyan]Downloading {asset['name']}...",
                    total=asset['size']
                )
                
                # Download file
                filepath = self.target_dir / asset['name']
                success = self.download_file(asset['browser_download_url'], filepath, progress, file_task)
                
                if success:
                    downloaded_files.append(filepath)
                    progress.update(overall_task, advance=1)
                else:
                    console.print(f"[red]Failed to download {asset['name']}[/red]")
                    return False
                
                progress.remove_task(file_task)
        
        console.print(f"[green]✅ Downloaded {len(downloaded_files)} files[/green]")
        
        # Extract ZIP files
        zip_files = [f for f in downloaded_files if f.suffix == '.zip']
        if zip_files:
            console.print("[bold]Extracting archives...[/bold]")
            
            for zip_file in zip_files:
                console.print(f"[dim]Extracting {zip_file.name}...[/dim]")
                extract_success = self.extract_zip_file(zip_file, self.target_dir)
                
                if extract_success:
                    # Remove ZIP file after extraction unless it's the main archive
                    if zip_file.name != 'all-formats.zip':
                        zip_file.unlink()
                else:
                    console.print(f"[red]Failed to extract {zip_file.name}[/red]")
                    return False
        
        # Load and display manifest if available
        manifest_path = self.target_dir / 'manifest.json'
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                self._display_installation_summary(manifest)
                
            except Exception as e:
                console.print(f"[yellow]Could not read manifest: {e}[/yellow]")
        
        console.print(f"[bold green]🎉 Installation complete![/bold green]")
        console.print(f"[dim]Datasets installed to: {self.target_dir}[/dim]")
        
        return True
    
    def _display_installation_summary(self, manifest: Dict) -> None:
        """Display installation summary from manifest."""
        
        console.print("\n[bold]📊 Installation Summary[/bold]")
        
        # Overall stats
        summary = manifest.get('summary', {})
        console.print(f"[dim]Total files: {summary.get('total_files', 0)}[/dim]")
        console.print(f"[dim]Total size: {summary.get('total_size_formatted', 'Unknown')}[/dim]")
        
        # Format breakdown
        formats = manifest.get('formats', {})
        if formats:
            format_table = Table(title="Datasets by Format", box=box.SIMPLE)
            format_table.add_column("Format", style="cyan")
            format_table.add_column("Files", justify="right")
            format_table.add_column("Size", justify="right")
            
            for fmt, info in formats.items():
                if info.get('file_count', 0) > 0:
                    format_table.add_row(
                        fmt.upper(),
                        str(info.get('file_count', 0)),
                        info.get('total_size_formatted', '0B')
                    )
            
            console.print(format_table)
        
        # Quick start examples
        console.print("\n[bold]🚀 Quick Start Examples[/bold]")
        console.print("[dim]Try converting some datasets:[/dim]")
        
        if formats.get('pdf', {}).get('file_count', 0) > 0:
            console.print("  [cyan]pyforge convert sample-datasets/pdf/small/*.pdf[/cyan]")
        
        if formats.get('excel', {}).get('file_count', 0) > 0:
            console.print("  [cyan]pyforge convert sample-datasets/excel/small/*.xlsx[/cyan]")
        
        if formats.get('xml', {}).get('file_count', 0) > 0:
            console.print("  [cyan]pyforge convert sample-datasets/xml/small/*.xml[/cyan]")
    
    def list_installed_datasets(self) -> None:
        """List currently installed datasets."""
        if not self.target_dir.exists():
            console.print("[yellow]No datasets installed.[/yellow]")
            console.print(f"[dim]Run 'pyforge install sample-datasets' to install datasets[/dim]")
            return
        
        # Look for manifest
        manifest_path = self.target_dir / 'manifest.json'
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                console.print(f"[bold]Installed Datasets: {manifest.get('version', 'Unknown')}[/bold]")
                console.print(f"[dim]Location: {self.target_dir}[/dim]")
                
                self._display_installation_summary(manifest)
                return
                
            except Exception as e:
                console.print(f"[yellow]Could not read manifest: {e}[/yellow]")
        
        # Fallback: scan directory structure
        console.print(f"[bold]Installed Datasets[/bold]")
        console.print(f"[dim]Location: {self.target_dir}[/dim]")
        
        total_files = 0
        for item in self.target_dir.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                total_files += 1
        
        console.print(f"[dim]Total files: {total_files}[/dim]")
    
    def uninstall_datasets(self, force: bool = False) -> bool:
        """Remove installed datasets."""
        if not self.target_dir.exists():
            console.print("[yellow]No datasets found to uninstall.[/yellow]")
            return True
        
        if not force:
            console.print(f"[yellow]This will remove all datasets from {self.target_dir}[/yellow]")
            console.print("[yellow]Use --force to confirm removal.[/yellow]")
            return False
        
        try:
            import shutil
            shutil.rmtree(self.target_dir)
            console.print(f"[green]✅ Datasets removed from {self.target_dir}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error removing datasets: {e}[/red]")
            return False