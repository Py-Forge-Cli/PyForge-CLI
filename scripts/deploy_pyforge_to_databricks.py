#!/usr/bin/env python3
"""
PyForge CLI Deployment Script

This script builds the PyForge CLI wheel package and deploys it to Databricks
using the Databricks CLI, following the proven CortexPy deployment pattern.

Usage:
    python scripts/deploy_pyforge_to_databricks.py [options]

Options:
    -u, --username <username>   Override Databricks username detection
    -p, --profile <profile>     Use specific Databricks CLI profile (default: DEFAULT)
    -v, --verbose               Enable verbose output
    -h, --help                  Show this help message
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class PyForgeDeployer:
    """Handles deployment of PyForge CLI wheel to Databricks following CortexPy pattern."""
    
    def __init__(self, profile: str = "DEFAULT", verbose: bool = False):
        self.profile = profile
        self.verbose = verbose
        # Get project root (parent of scripts directory)
        self.script_dir = Path(__file__).parent.absolute()
        self.project_root = self.script_dir.parent.absolute()
        self.dist_dir = self.project_root / "dist"
        
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Build metadata
        self.build_info = {
            "timestamp": datetime.now().isoformat(),
            "git_commit": self._get_git_commit(),
            "version": self._get_package_version(),
            "profile": self.profile
        }
        
    def _get_git_commit(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()[:8]  # Short hash
        except:
            pass
        return "unknown"
    
    def _get_package_version(self) -> str:
        """Get package version from pyproject.toml."""
        try:
            with open(self.project_root / "pyproject.toml", "r") as f:
                for line in f:
                    if line.strip().startswith('version = '):
                        # Extract version from 'version = "0.5.8"'
                        return line.split('"')[1]
        except:
            pass
        return "unknown"
        
    def run_command(self, cmd: list, capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command with proper error handling."""
        cmd_str = ' '.join(cmd)
        self.logger.debug(f"Running command: {cmd_str}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=check,
                cwd=self.project_root
            )
            
            if self.verbose and result.stdout:
                self.logger.debug(f"Command output: {result.stdout}")
                
            return result
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {cmd_str}")
            self.logger.error(f"Exit code: {e.returncode}")
            if e.stdout:
                self.logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                self.logger.error(f"STDERR: {e.stderr}")
            raise
    
    def check_prerequisites(self) -> None:
        """Check if required tools and files are available."""
        self.logger.info("Checking prerequisites...")
        
        # Check if databricks CLI is available
        try:
            result = self.run_command(["databricks", "--version"])
            self.logger.info(f"Databricks CLI version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Databricks CLI not found. Install with: pip install databricks-cli"
            )
        
        # Check if python build tools are available
        try:
            self.run_command([sys.executable, "-m", "build", "--help"])
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Python build tools not found. Install with: pip install build"
            )
        
        # Check if required files exist
        required_files = ["pyproject.toml"]
        for file in required_files:
            if not (self.project_root / file).exists():
                raise RuntimeError(f"Required file not found: {file}")
            
        self.logger.info("✓ Prerequisites check passed")
    
    def get_databricks_username(self, override_username: Optional[str] = None) -> str:
        """Get the Databricks username, with fallback strategies."""
        if override_username:
            self.logger.info(f"Using provided username: {override_username}")
            return override_username
        
        try:
            # Try to get current Databricks user
            result = self.run_command([
                "databricks", "current-user", "me", 
                "--profile", self.profile, "--output", "json"
            ])
            
            user_info = json.loads(result.stdout)
            username = user_info.get("userName", "")
            
            if username:
                self.logger.info(f"Detected Databricks username: {username}")
                return username
            
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Failed to get Databricks username: {e}")
        
        # Fallback to git username
        try:
            result = self.run_command(["git", "config", "user.name"])
            git_username = result.stdout.strip()
            if git_username:
                self.logger.info(f"Using git username as fallback: {git_username}")
                return git_username
        except subprocess.CalledProcessError:
            self.logger.warning("Failed to get git username")
        
        raise RuntimeError(
            "Could not determine username. Please provide one with --username option"
        )
    
    def build_wheel(self) -> Path:
        """Build the PyForge CLI wheel package."""
        self.logger.info("Building PyForge CLI wheel package...")
        
        # Clean dist directory
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            self.logger.debug("Cleaned dist directory")
        
        # Build wheel
        self.run_command([sys.executable, "-m", "build", "--wheel"])
        
        # Find the built wheel
        wheel_files = list(self.dist_dir.glob("*.whl"))
        if not wheel_files:
            raise RuntimeError("No wheel file found after build")
        
        wheel_path = wheel_files[0]
        self.logger.info(f"✓ Built wheel: {wheel_path.name}")
        return wheel_path
    
    def upload_wheel(self, wheel_path: Path, username: str) -> str:
        """Upload wheel to Databricks Unity Catalog volume."""
        volume_path = f"dbfs:/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/"
        
        self.logger.info(f"Uploading wheel to: {volume_path}")
        
        # Create directory if it doesn't exist (databricks fs mkdirs creates parent dirs)
        try:
            self.run_command([
                "databricks", "fs", "mkdirs", volume_path,
                "--profile", self.profile
            ])
        except subprocess.CalledProcessError:
            # Directory might already exist, that's okay
            pass
        
        # Upload wheel (this will overwrite if exists)
        wheel_dest = f"{volume_path}{wheel_path.name}"
        self.run_command([
            "databricks", "fs", "cp", str(wheel_path), wheel_dest,
            "--profile", self.profile, "--overwrite"
        ])
        
        self.logger.info(f"✓ Uploaded wheel to: {wheel_dest}")
        return wheel_dest
    
    def upload_test_notebooks(self, username: str) -> str:
        """Upload test notebooks to Databricks workspace."""
        workspace_path = f"/Workspace/CoreDataEngineers/{username}/pyforge_notebooks/"
        
        self.logger.info(f"Uploading test notebooks to: {workspace_path}")
        
        # Get list of test notebook files from organized notebooks directory
        notebooks_dir = self.project_root / "notebooks" / "testing"
        notebook_files = []
        
        # Collect all notebook files from testing subdirectories (excluding test environments)
        for subdir in ["unit", "integration", "functional", "exploratory"]:
            subdir_path = notebooks_dir / subdir
            if subdir_path.exists():
                # Find .py and .ipynb files directly in subdir (not recursive to avoid test_env)
                for pattern in ["*.py", "*.ipynb"]:
                    for file_path in subdir_path.glob(pattern):
                        # Skip files in test environments or hidden directories
                        if not any(part.startswith('.') or 'test_env' in part or '__pycache__' in part 
                                 for part in file_path.parts):
                            notebook_files.append(file_path)
        
        uploaded_count = 0
        for notebook_file in notebook_files:
            if notebook_file.exists():
                # Preserve directory structure in workspace
                relative_path = notebook_file.relative_to(notebooks_dir)
                notebook_dest = f"{workspace_path}{relative_path}"
                
                # Determine format and language based on file extension
                if notebook_file.suffix == ".ipynb":
                    format_type = "JUPYTER"
                    language = "PYTHON"
                elif notebook_file.suffix == ".py":
                    format_type = "SOURCE"
                    language = "PYTHON"
                else:
                    self.logger.warning(f"Skipping unsupported file type: {notebook_file.name}")
                    continue
                
                try:
                    # Create parent directories first
                    parent_dir = "/".join(notebook_dest.split("/")[:-1])
                    try:
                        self.run_command([
                            "databricks", "workspace", "mkdirs", parent_dir,
                            "--profile", self.profile
                        ])
                    except subprocess.CalledProcessError:
                        # Directory might already exist, that's okay
                        pass
                    
                    # Upload the notebook
                    self.run_command([
                        "databricks", "workspace", "import", notebook_dest,
                        "--file", str(notebook_file), "--profile", self.profile, 
                        "--overwrite", "--format", format_type, "--language", language
                    ])
                    self.logger.info(f"✓ Uploaded notebook: {relative_path}")
                    uploaded_count += 1
                    
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to upload {relative_path}: {e}")
                    # Continue with other notebooks
        
        if uploaded_count == 0:
            self.logger.warning("No test notebooks were uploaded")
        else:
            self.logger.info(f"✓ Uploaded {uploaded_count} test notebooks")
            
        return workspace_path
    
    def save_build_metadata(self, wheel_dest: str, workspace_path: str, username: str) -> None:
        """Save build and deployment metadata."""
        metadata = {
            **self.build_info,
            "deployment": {
                "username": username,
                "wheel_path": wheel_dest,
                "workspace_path": workspace_path,
                "deployed_at": datetime.now().isoformat(),
                "install_command": f"%pip install {wheel_dest.replace('dbfs:/', '/')}"
            }
        }
        
        # Save to local file
        metadata_file = self.script_dir / "last_deployment.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"✓ Build metadata saved: {metadata_file}")
    
    def verify_deployment(self, wheel_dest: str, workspace_path: str) -> None:
        """Verify that files were uploaded successfully."""
        self.logger.info("Verifying deployment...")
        
        # Check wheel exists by listing the directory and looking for the file
        try:
            wheel_dir = "/".join(wheel_dest.split("/")[:-1]) + "/"
            result = self.run_command([
                "databricks", "fs", "ls", wheel_dir,
                "--profile", self.profile
            ])
            wheel_filename = wheel_dest.split("/")[-1]
            if wheel_filename in result.stdout:
                self.logger.info("✓ Wheel file verified")
            else:
                self.logger.error("✗ Wheel file not found in directory")
        except subprocess.CalledProcessError:
            self.logger.error("✗ Wheel directory verification failed")
        
        # Check notebooks exist
        try:
            result = self.run_command([
                "databricks", "workspace", "list", workspace_path,
                "--profile", self.profile
            ])
            if result.stdout.strip():
                self.logger.info("✓ Test notebooks verified")
            else:
                self.logger.warning("No test notebooks found in workspace")
        except subprocess.CalledProcessError:
            self.logger.error("✗ Test notebook verification failed")
    
    def print_summary(self, username: str, wheel_dest: str, workspace_path: str) -> None:
        """Print deployment summary."""
        print("\n" + "="*60)
        print("PYFORGE CLI DEPLOYMENT SUMMARY")
        print("="*60)
        print(f"Username: {username}")
        print(f"Profile: {self.profile}")
        print(f"Version: {self.build_info['version']}")
        print(f"Git Commit: {self.build_info['git_commit']}")
        print(f"Wheel Location: {wheel_dest}")
        print(f"Test Notebooks: {workspace_path}")
        print("\nNext Steps for V1 Testing:")
        print("1. In your Databricks Serverless V1 notebook, run:")
        # Convert dbfs: path to /Volumes/ path for pip install
        pip_path = wheel_dest.replace("dbfs:/", "/")
        print(f"   %pip install {pip_path}")
        print("2. Restart Python kernel:")
        print("   dbutils.library.restartPython()")
        print("3. Test imports:")
        print("   import pyforge_cli")
        print("   from pyforge_cli.backends.ucanaccess_backend import UCanAccessBackend")
        print("4. Run integration tests from:")
        print(f"   {workspace_path}")
        print("5. Test MDB files from:")
        print("   /Volumes/cortex_dev_catalog/sandbox_testing/sample-datasets/access/")
        print("="*60)
    
    def deploy(self, override_username: Optional[str] = None) -> Dict[str, Any]:
        """Execute the full deployment process."""
        try:
            self.logger.info("🚀 Starting PyForge CLI deployment...")
            
            # Step 1: Check prerequisites
            self.check_prerequisites()
            
            # Step 2: Get username
            username = self.get_databricks_username(override_username)
            
            # Step 3: Build wheel
            wheel_path = self.build_wheel()
            
            # Step 4: Upload wheel
            wheel_dest = self.upload_wheel(wheel_path, username)
            
            # Step 5: Upload test notebooks
            workspace_path = self.upload_test_notebooks(username)
            
            # Step 6: Save metadata
            self.save_build_metadata(wheel_dest, workspace_path, username)
            
            # Step 7: Verify deployment
            self.verify_deployment(wheel_dest, workspace_path)
            
            # Step 8: Print summary
            self.print_summary(username, wheel_dest, workspace_path)
            
            self.logger.info("🎉 PyForge CLI deployment completed successfully!")
            
            return {
                "success": True,
                "username": username,
                "wheel_dest": wheel_dest,
                "workspace_path": workspace_path,
                "version": self.build_info['version'],
                "metadata": self.build_info
            }
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy PyForge CLI wheel and test notebooks to Databricks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "-u", "--username",
        help="Override Databricks username detection"
    )
    
    parser.add_argument(
        "-p", "--profile",
        default="DEFAULT",
        help="Databricks CLI profile to use (default: DEFAULT)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Create deployer and run
    deployer = PyForgeDeployer(
        profile=args.profile,
        verbose=args.verbose
    )
    
    result = deployer.deploy(override_username=args.username)
    
    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()