"""Tests for sample datasets installer."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import tempfile
import shutil

from pyforge_cli.installers.sample_datasets_installer import SampleDatasetsInstaller


class TestSampleDatasetsInstaller:
    """Test cases for SampleDatasetsInstaller."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def installer(self, temp_dir):
        """Create installer instance with temp directory."""
        return SampleDatasetsInstaller(target_dir=temp_dir)
    
    @pytest.fixture
    def mock_release_data(self):
        """Mock GitHub release API response."""
        return [
            {
                "tag_name": "v1.0.0",
                "name": "Test Release",
                "published_at": "2025-06-24T00:00:00Z",
                "assets": [
                    {
                        "name": "manifest.json",
                        "size": 1024,
                        "browser_download_url": "https://github.com/test/releases/download/v1.0.0/manifest.json"
                    },
                    {
                        "name": "checksums.sha256", 
                        "size": 512,
                        "browser_download_url": "https://github.com/test/releases/download/v1.0.0/checksums.sha256"
                    },
                    {
                        "name": "all-formats.zip",
                        "size": 10485760,  # 10MB
                        "browser_download_url": "https://github.com/test/releases/download/v1.0.0/all-formats.zip"
                    }
                ]
            }
        ]
    
    @pytest.fixture
    def mock_manifest_data(self):
        """Mock manifest.json content."""
        return {
            "version": "v1.0.0",
            "summary": {
                "total_files": 5,
                "total_size_bytes": 52428800,
                "total_size_formatted": "50.0MB"
            },
            "formats": {
                "pdf": {
                    "file_count": 2,
                    "total_size_bytes": 10485760,
                    "total_size_formatted": "10.0MB"
                },
                "excel": {
                    "file_count": 3,
                    "total_size_bytes": 41943040,
                    "total_size_formatted": "40.0MB"
                }
            }
        }
    
    def test_init_default_target_dir(self):
        """Test installer initialization with default target directory."""
        installer = SampleDatasetsInstaller()
        expected_path = Path.cwd() / "sample-datasets"
        assert installer.target_dir == expected_path
    
    def test_init_custom_target_dir(self, temp_dir):
        """Test installer initialization with custom target directory."""
        installer = SampleDatasetsInstaller(target_dir=temp_dir)
        assert installer.target_dir == temp_dir
    
    @patch('requests.Session.get')
    def test_list_available_releases_success(self, mock_get, installer, mock_release_data):
        """Test successful listing of available releases."""
        mock_response = Mock()
        mock_response.json.return_value = mock_release_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        releases = installer.list_available_releases()
        
        assert len(releases) == 1
        assert releases[0]["tag_name"] == "v1.0.0"
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_list_available_releases_error(self, mock_get, installer):
        """Test error handling when listing releases fails."""
        mock_get.side_effect = Exception("Network error")
        
        releases = installer.list_available_releases()
        
        assert releases == []
    
    @patch('requests.Session.get')
    def test_get_latest_release(self, mock_get, installer, mock_release_data):
        """Test getting the latest release."""
        mock_response = Mock()
        mock_response.json.return_value = mock_release_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        latest = installer.get_latest_release()
        
        assert latest is not None
        assert latest["tag_name"] == "v1.0.0"
    
    @patch('requests.Session.get')
    def test_get_release_by_version(self, mock_get, installer, mock_release_data):
        """Test getting a specific release by version."""
        mock_response = Mock()
        mock_response.json.return_value = mock_release_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        release = installer.get_release_by_version("v1.0.0")
        
        assert release is not None
        assert release["tag_name"] == "v1.0.0"
        
        # Test non-existent version
        release = installer.get_release_by_version("v2.0.0")
        assert release is None
    
    @patch('builtins.open', new_callable=mock_open)
    def test_verify_checksum_success(self, mock_file, installer, temp_dir):
        """Test successful checksum verification."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_content = b"hello world"
        test_file.write_bytes(test_content)
        
        # Expected SHA256 for "hello world"
        expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        
        # Mock file reading to return our test content
        mock_file.return_value.__enter__.return_value.read.return_value = test_content
        
        result = installer.verify_checksum(test_file, expected_hash)
        assert result is True
    
    def test_verify_checksum_mismatch(self, installer, temp_dir):
        """Test checksum verification with hash mismatch."""
        test_file = temp_dir / "test.txt"
        test_file.write_bytes(b"hello world")
        
        # Wrong hash
        wrong_hash = "abc123"
        
        result = installer.verify_checksum(test_file, wrong_hash)
        assert result is False
    
    def test_extract_zip_file(self, installer, temp_dir):
        """Test ZIP file extraction."""
        # This would require creating an actual ZIP file
        # For now, we'll test the error handling
        non_existent_zip = temp_dir / "nonexistent.zip"
        extract_dir = temp_dir / "extracted"
        
        result = installer.extract_zip_file(non_existent_zip, extract_dir)
        assert result is False
    
    @patch('requests.Session.get')
    def test_download_file_success(self, mock_get, installer, temp_dir):
        """Test successful file download."""
        from rich.progress import Progress
        
        # Mock response
        mock_response = Mock()
        mock_response.headers = {'content-length': '100'}
        mock_response.iter_content.return_value = [b'data'] * 25  # 4 bytes * 25 = 100 bytes
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with Progress() as progress:
            task_id = progress.add_task("test", total=100)
            
            test_file = temp_dir / "downloaded.txt"
            result = installer.download_file("https://example.com/file.txt", test_file, progress, task_id)
        
        assert result is True
        assert test_file.exists()
    
    @patch('requests.Session.get')
    def test_download_file_error(self, mock_get, installer, temp_dir):
        """Test file download error handling."""
        from rich.progress import Progress
        
        mock_get.side_effect = Exception("Download failed")
        
        with Progress() as progress:
            task_id = progress.add_task("test", total=100)
            
            test_file = temp_dir / "failed.txt"
            result = installer.download_file("https://example.com/file.txt", test_file, progress, task_id)
        
        assert result is False
    
    def test_list_installed_datasets_no_directory(self, installer):
        """Test listing installed datasets when no directory exists."""
        # This should not raise an exception, just show no datasets
        installer.list_installed_datasets()  # Should print "No datasets installed"
    
    def test_list_installed_datasets_with_manifest(self, installer, mock_manifest_data):
        """Test listing installed datasets with manifest file."""
        # Create manifest file
        manifest_path = installer.target_dir / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(manifest_path, 'w') as f:
            json.dump(mock_manifest_data, f)
        
        # This should read and display the manifest
        installer.list_installed_datasets()
    
    def test_uninstall_datasets_no_directory(self, installer):
        """Test uninstalling when no datasets are installed."""
        result = installer.uninstall_datasets(force=False)
        assert result is True
    
    def test_uninstall_datasets_without_force(self, installer, temp_dir):
        """Test uninstalling without force flag."""
        # Create some files in target directory
        installer.target_dir.mkdir(parents=True, exist_ok=True)
        (installer.target_dir / "test.txt").write_text("test")
        
        result = installer.uninstall_datasets(force=False)
        assert result is False
        assert installer.target_dir.exists()
    
    def test_uninstall_datasets_with_force(self, installer, temp_dir):
        """Test uninstalling with force flag."""
        # Create some files in target directory
        installer.target_dir.mkdir(parents=True, exist_ok=True)
        (installer.target_dir / "test.txt").write_text("test")
        
        result = installer.uninstall_datasets(force=True)
        assert result is True
        assert not installer.target_dir.exists()
    
    @patch('requests.Session.get')
    def test_install_datasets_no_releases(self, mock_get, installer):
        """Test installation when no releases are available."""
        mock_get.return_value.json.return_value = []
        mock_get.return_value.raise_for_status.return_value = None
        
        result = installer.install_datasets()
        assert result is False
    
    @patch('requests.Session.get')
    def test_install_datasets_version_not_found(self, mock_get, installer, mock_release_data):
        """Test installation with non-existent version."""
        mock_response = Mock()
        mock_response.json.return_value = mock_release_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = installer.install_datasets(version="v2.0.0")
        assert result is False
    
    def test_install_datasets_existing_directory_no_force(self, installer):
        """Test installation when target directory exists without force."""
        installer.target_dir.mkdir(parents=True, exist_ok=True)
        
        with patch.object(installer, 'get_latest_release') as mock_get_latest:
            mock_get_latest.return_value = {"tag_name": "v1.0.0", "assets": []}
            
            result = installer.install_datasets(force=False)
            assert result is False