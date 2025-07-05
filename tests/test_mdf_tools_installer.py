"""
Tests for MDF Tools Installer functionality.
"""

import pytest
import subprocess
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from pyforge_cli.installers.mdf_tools_installer import MdfToolsInstaller


class TestMdfToolsInstaller:
    """Test cases for MdfToolsInstaller class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.installer = MdfToolsInstaller()
    
    def test_init(self):
        """Test installer initialization."""
        assert self.installer.sql_container_name == "pyforge-sql-server"
        assert self.installer.sql_port == 1433
        assert self.installer.sql_password == "PyForge@2024!"
        assert self.installer.sql_image == "mcr.microsoft.com/mssql/server:2019-latest"
        assert isinstance(self.installer.config_path, Path)
    
    @patch('subprocess.run')
    def test_is_docker_installed_true(self, mock_run):
        """Test Docker installation detection when Docker is installed."""
        mock_run.return_value = Mock(returncode=0)
        assert self.installer._is_docker_installed() is True
    
    @patch('subprocess.run')
    def test_is_docker_installed_false(self, mock_run):
        """Test Docker installation detection when Docker is not installed."""
        mock_run.side_effect = FileNotFoundError()
        assert self.installer._is_docker_installed() is False
    
    @patch('subprocess.run')
    def test_is_docker_installed_timeout(self, mock_run):
        """Test Docker installation detection with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("docker", 5)
        assert self.installer._is_docker_installed() is False
    
    @patch('platform.system')
    def test_check_system_requirements_macos(self, mock_system):
        """Test system requirements check on macOS."""
        mock_system.return_value = "Darwin"
        
        with patch.object(self.installer, '_is_docker_installed', return_value=True):
            result = self.installer._check_system_requirements()
            assert result is True
    
    @patch('platform.system')
    def test_check_system_requirements_unsupported(self, mock_system):
        """Test system requirements check on unsupported OS."""
        mock_system.return_value = "Unsupported"
        
        result = self.installer._check_system_requirements()
        assert result is False
    
    def test_get_docker_version(self):
        """Test Docker version retrieval."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Docker version 20.10.17, build 100c701"
            )
            
            version = self.installer._get_docker_version()
            assert "Docker version" in version
    
    def test_get_docker_version_error(self):
        """Test Docker version retrieval with error."""
        with patch('subprocess.run', side_effect=Exception()):
            version = self.installer._get_docker_version()
            assert version == "unknown"
    
    @patch('docker.from_env')
    def test_get_existing_container_found(self, mock_docker):
        """Test getting existing container when it exists."""
        mock_client = Mock()
        mock_container = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_docker.return_value = mock_client
        
        self.installer.docker_client = mock_client
        result = self.installer._get_existing_container()
        assert result == mock_container
    
    @patch('docker.from_env')
    def test_get_existing_container_not_found(self, mock_docker):
        """Test getting existing container when it doesn't exist."""
        import docker
        mock_client = Mock()
        mock_client.containers.get.side_effect = docker.errors.NotFound("not found")
        mock_docker.return_value = mock_client
        
        self.installer.docker_client = mock_client
        result = self.installer._get_existing_container()
        assert result is None
    
    @patch('builtins.open', new_callable=MagicMock)
    @patch('json.dump')
    @patch('pathlib.Path.mkdir')
    def test_save_configuration(self, mock_mkdir, mock_json_dump, mock_open):
        """Test configuration saving."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        self.installer._save_configuration()
        
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_open.assert_called_once()
        mock_json_dump.assert_called_once()
    
    def test_get_status_no_docker(self):
        """Test status when Docker is not installed."""
        with patch.object(self.installer, '_is_docker_installed', return_value=False):
            status = self.installer.get_status()
            
            assert status['docker_installed'] is False
            assert status['docker_running'] is False
            assert status['sql_container_exists'] is False
            assert status['sql_container_running'] is False
            assert status['sql_server_responding'] is False
    
    @patch('docker.from_env')
    def test_get_status_docker_running(self, mock_docker):
        """Test status when Docker is running."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_docker.return_value = mock_client
        
        with patch.object(self.installer, '_is_docker_installed', return_value=True):
            with patch.object(self.installer, '_get_existing_container', return_value=None):
                status = self.installer.get_status()
                
                assert status['docker_installed'] is True
                assert status['docker_running'] is True
                assert status['sql_container_exists'] is False
    
    def test_custom_password_and_port(self):
        """Test installer with custom password and port."""
        custom_password = "MyCustomPass123!"
        custom_port = 1434
        
        installer = MdfToolsInstaller()
        
        # This would normally be called in interactive_install
        installer.sql_password = custom_password
        installer.sql_port = custom_port
        
        assert installer.sql_password == custom_password
        assert installer.sql_port == custom_port


class TestMdfToolsInstallerIntegration:
    """Integration tests for MDF Tools Installer."""
    
    def test_config_path_structure(self):
        """Test that config path is correctly structured."""
        installer = MdfToolsInstaller()
        
        expected_path = Path.home() / ".pyforge" / "mdf-config.json"
        assert installer.config_path == expected_path
    
    def test_container_configuration(self):
        """Test container configuration parameters."""
        installer = MdfToolsInstaller()
        
        assert installer.sql_container_name == "pyforge-sql-server"
        assert installer.sql_image == "mcr.microsoft.com/mssql/server:2019-latest"
        assert installer.sql_port == 1433
        assert len(installer.sql_password) >= 8  # Minimum password length