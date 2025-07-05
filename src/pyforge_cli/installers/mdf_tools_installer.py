"""
MDF Tools Installer - Interactive Docker Desktop and SQL Server Express setup.

This module provides installation and management of Docker containers needed
for MDF file processing via SQL Server Express.
"""

import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class MdfToolsInstaller:
    """
    Interactive installer for MDF processing tools.

    Sets up Docker Desktop and SQL Server Express container with guided workflow.
    """

    def __init__(self):
        self.console = Console()
        self.docker_client: Optional[docker.DockerClient] = None
        self.sql_container_name = "pyforge-sql-server"
        self.sql_port = 1433
        self.sql_password = "PyForge@2024!"
        self.sql_image = "mcr.microsoft.com/mssql/server:2019-latest"
        self.config_path = Path.home() / ".pyforge" / "mdf-config.json"
        self.non_interactive = False

    def interactive_install(
        self, custom_password: Optional[str] = None, custom_port: Optional[int] = None
    ) -> bool:
        """
        Run the interactive installation wizard.

        Args:
            custom_password: Optional custom SQL Server password
            custom_port: Optional custom SQL Server port

        Returns:
            True if installation succeeded, False otherwise
        """
        # Use custom values if provided
        if custom_password:
            self.sql_password = custom_password
        if custom_port:
            self.sql_port = custom_port

        self.console.print(
            Panel.fit(
                "[bold blue]PyForge MDF Tools Setup Wizard[/bold blue]\n"
                "Setting up Docker Desktop and SQL Server Express for MDF file processing",
                border_style="blue",
            )
        )

        try:
            # Stage 1: Check system requirements
            if not self._check_system_requirements():
                return False

            # Stage 2: Handle Docker installation
            if not self._setup_docker():
                return False

            # Stage 3: Install Docker Desktop if needed
            if not self._ensure_docker_running():
                return False

            # Stage 4: Setup SQL Server Express
            if not self._setup_sql_server():
                return False

            # Stage 5: Complete installation
            self._complete_installation()
            return True

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Installation cancelled by user.[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"\n[red]Installation failed: {e}[/red]")
            return False

    def _check_system_requirements(self) -> bool:
        """Stage 1: Check system requirements"""
        self.console.print(
            "\n[bold blue][1/5] Checking system requirements...[/bold blue]"
        )

        # Check operating system
        system = platform.system()
        version = platform.release()

        if system == "Darwin":  # macOS
            self.console.print(f"✓ Operating System: macOS {version} (supported)")
        elif system == "Windows":
            self.console.print(f"✓ Operating System: Windows {version} (supported)")
        elif system == "Linux":
            self.console.print(f"✓ Operating System: Linux {version} (supported)")
        else:
            self.console.print(f"❌ Operating System: {system} (not supported)")
            return False

        # Check Docker Desktop installation (system level)
        docker_installed = self._is_docker_installed()
        if docker_installed:
            self.console.print("✓ Docker Desktop: Installed")
        else:
            self.console.print("❌ Docker Desktop: Not found")

        # Check if Docker SDK is available (Python package)
        global DOCKER_AVAILABLE
        if not DOCKER_AVAILABLE:
            self.console.print("❌ Docker SDK for Python: Not installed")
            if docker_installed:
                # Only install SDK if Docker Desktop exists
                self.console.print(
                    "\n[yellow]Installing Docker SDK for Python...[/yellow]"
                )
                try:
                    subprocess.run(
                        ["pip", "install", "docker"], check=True, capture_output=True
                    )
                    global docker
                    import docker

                    DOCKER_AVAILABLE = True
                    self.console.print("✓ Docker SDK for Python: Installed")
                except Exception as e:
                    self.console.print(f"❌ Failed to install Docker SDK: {e}")
                    return False
            else:
                self.console.print(
                    "⚠️ Docker SDK installation skipped (Docker Desktop required first)"
                )
        else:
            self.console.print("✓ Docker SDK for Python: Available")

        return True

    def _setup_docker(self) -> bool:
        """Stage 2: Handle Docker installation"""
        if self._is_docker_installed():
            return True

        self.console.print(
            "\n[bold blue][2/5] Docker Installation Required[/bold blue]"
        )
        self.console.print("Docker Desktop is required for MDF file conversion.")

        system = platform.system()

        if system == "Darwin":
            choices = [
                "Install automatically using Homebrew (recommended)",
                "Get installation instructions",
                "Skip (I'll install manually)",
                "Continue without Docker (installation will fail)",
            ]
        elif system == "Windows":
            choices = [
                "Install automatically using Winget (recommended)",
                "Get installation instructions",
                "Skip (I'll install manually)",
                "Continue without Docker (installation will fail)",
            ]
        else:
            choices = [
                "Get installation instructions",
                "Skip (I'll install manually)",
                "Continue without Docker (installation will fail)",
            ]

        self.console.print("\nWould you like to:")
        for i, choice in enumerate(choices, 1):
            self.console.print(f"  {i}. {choice}")

        if self.non_interactive:
            choice = "1"  # Default to automatic installation in non-interactive mode
            self.console.print(
                f"\n[yellow]Non-interactive mode: Using option {choice}[/yellow]"
            )
        else:
            try:
                choice = Prompt.ask(
                    "Choice",
                    choices=[str(i) for i in range(1, len(choices) + 1)],
                    default="1",
                )
            except EOFError:
                self.console.print(
                    "\n[red]No interactive input available. Using default option (1).[/red]"
                )
                choice = "1"

        if choice == "1" and len(choices) == 4:  # Automatic installation option
            return self._attempt_automatic_docker_installation()
        elif (choice == "1" and len(choices) == 3) or (
            choice == "2" and len(choices) == 4
        ):
            self._show_docker_installation_instructions()
            return self._wait_for_docker_installation()
        elif (choice == "2" and len(choices) == 3) or (
            choice == "3" and len(choices) == 4
        ):
            self.console.print(
                "\n[yellow]Please install Docker Desktop and re-run this installer.[/yellow]"
            )
            return False
        else:
            self.console.print("\n[red]Cannot proceed without Docker Desktop.[/red]")
            return False

    def _ensure_docker_running(self) -> bool:
        """Stage 3: Ensure Docker is running"""
        self.console.print("\n[bold blue][3/5] Starting Docker Desktop...[/bold blue]")

        # Try to connect to Docker
        max_attempts = 12  # 2 minutes with 10-second intervals
        for attempt in range(max_attempts):
            try:
                self.docker_client = docker.from_env()
                self.docker_client.ping()
                self.console.print("✓ Docker Desktop is running")
                return True
            except Exception:
                if attempt == 0:
                    self.console.print("⏳ Waiting for Docker daemon to start...")

                time.sleep(10)

        self.console.print("❌ Docker daemon is not responding")
        self.console.print("Please ensure Docker Desktop is installed and running.")
        return False

    def _setup_sql_server(self) -> bool:
        """Stage 4: Setup SQL Server Express"""
        self.console.print(
            "\n[bold blue][4/5] Setting up SQL Server Express...[/bold blue]"
        )

        try:
            # Check if container already exists
            existing_container = self._get_existing_container()
            if existing_container:
                if existing_container.status == "running":
                    self.console.print("✓ SQL Server container already running")
                    return self._test_sql_connection()
                else:
                    self.console.print("⚠️ Existing container found, restarting...")
                    existing_container.start()
                    return self._wait_for_sql_server()

            # Pull SQL Server image
            self.console.print(f"📥 Pulling SQL Server image: {self.sql_image}")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Downloading SQL Server image...", total=None)
                self.docker_client.images.pull(self.sql_image)
                progress.update(task, description="✓ SQL Server image downloaded")

            # Create and start container
            self.console.print("🚀 Creating SQL Server container...")
            self._create_sql_container()

            # Wait for SQL Server to be ready
            return self._wait_for_sql_server()

        except Exception as e:
            self.console.print(f"❌ Failed to setup SQL Server: {e}")
            return False

    def _complete_installation(self) -> None:
        """Stage 5: Complete installation"""
        self.console.print("\n[bold blue][5/5] Installation Complete![/bold blue]")

        # Save configuration
        self._save_configuration()

        # Display connection details
        self._display_connection_info()

        # Show next steps
        self._show_next_steps()

    def _is_docker_installed(self) -> bool:
        """Check if Docker is installed"""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _show_docker_installation_instructions(self) -> None:
        """Show platform-specific Docker installation instructions"""
        system = platform.system()

        instructions = {
            "Darwin": {
                "title": "macOS Docker Installation",
                "steps": [
                    "[bold cyan]Option 1: Homebrew (Recommended)[/bold cyan]",
                    "brew install --cask docker",
                    "open -a Docker  # Launch Docker Desktop",
                    "",
                    "[bold cyan]Option 2: Manual Download[/bold cyan]",
                    "1. Visit: https://docs.docker.com/desktop/install/mac-install/",
                    "2. Download Docker Desktop for Mac",
                    "3. Double-click Docker.dmg and drag to Applications",
                    "4. Launch Docker Desktop from Applications",
                    "5. Follow the setup wizard and accept license terms",
                ],
            },
            "Windows": {
                "title": "Windows Docker Installation",
                "steps": [
                    "[bold cyan]Option 1: Winget (Recommended)[/bold cyan]",
                    "winget install Docker.DockerDesktop",
                    "",
                    "[bold cyan]Option 2: Chocolatey[/bold cyan]",
                    "choco install docker-desktop",
                    "",
                    "[bold cyan]Option 3: Manual Download[/bold cyan]",
                    "1. Visit: https://docs.docker.com/desktop/install/windows-install/",
                    "2. Download Docker Desktop for Windows",
                    "3. Run Docker Desktop Installer.exe as Administrator",
                    "4. Follow installation wizard",
                    "5. Restart computer if prompted",
                    "6. Launch Docker Desktop from Start menu",
                ],
            },
            "Linux": {
                "title": "Linux Docker Installation",
                "steps": [
                    "[bold cyan]Option 1: Package Manager (Recommended)[/bold cyan]",
                    "# Ubuntu/Debian:",
                    "sudo apt update && sudo apt install docker.io docker-compose",
                    "sudo systemctl start docker && sudo systemctl enable docker",
                    "sudo usermod -aG docker $USER",
                    "",
                    "# CentOS/RHEL:",
                    "sudo yum install docker docker-compose",
                    "sudo systemctl start docker && sudo systemctl enable docker",
                    "sudo usermod -aG docker $USER",
                    "",
                    "[bold cyan]Option 2: Docker Desktop for Linux[/bold cyan]",
                    "Visit: https://docs.docker.com/desktop/install/linux-install/",
                    "",
                    "[bold yellow]Important:[/bold yellow] Log out and back in after installation",
                ],
            },
        }

        info = instructions.get(system, instructions["Linux"])

        self.console.print(
            Panel("\n".join(info["steps"]), title=info["title"], border_style="cyan")
        )

    def _attempt_automatic_docker_installation(self) -> bool:
        """Attempt automatic Docker Desktop installation using system package managers"""
        system = platform.system()

        if system == "Darwin":
            self.console.print(
                "\n[bold yellow]Attempting to install Docker Desktop using Homebrew...[/bold yellow]"
            )

            # Check if Homebrew is installed
            try:
                subprocess.run(["brew", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.console.print(
                    "❌ Homebrew not found. Please install Homebrew first:"
                )
                self.console.print(
                    '   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                )
                return False

            try:
                # Install Docker Desktop using Homebrew
                self.console.print(
                    "📦 Installing Docker Desktop (this may take several minutes)..."
                )
                subprocess.run(
                    ["brew", "install", "--cask", "docker"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                )

                self.console.print("✅ Docker Desktop installed successfully!")
                self.console.print("🚀 Launching Docker Desktop...")

                # Launch Docker Desktop
                subprocess.run(["open", "-a", "Docker"], check=False)

                return self._wait_for_docker_startup()

            except subprocess.TimeoutExpired:
                self.console.print(
                    "❌ Installation timed out. Please try manual installation."
                )
                return False
            except subprocess.CalledProcessError as e:
                self.console.print(f"❌ Installation failed: {e.stderr}")
                self.console.print(
                    "Falling back to manual installation instructions..."
                )
                self._show_docker_installation_instructions()
                return self._wait_for_docker_installation()

        elif system == "Windows":
            self.console.print(
                "\n[bold yellow]Attempting to install Docker Desktop using Winget...[/bold yellow]"
            )

            try:
                # Check if winget is available
                subprocess.run(["winget", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.console.print(
                    "❌ Winget not found. Please use manual installation."
                )
                self._show_docker_installation_instructions()
                return self._wait_for_docker_installation()

            try:
                # Install Docker Desktop using Winget
                self.console.print(
                    "📦 Installing Docker Desktop (this may take several minutes)..."
                )
                subprocess.run(
                    ["winget", "install", "Docker.DockerDesktop"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                )

                self.console.print("✅ Docker Desktop installed successfully!")
                self.console.print(
                    "⚠️ Please restart your computer and then launch Docker Desktop manually."
                )

                try:
                    if Confirm.ask("Have you restarted and launched Docker Desktop?"):
                        return self._wait_for_docker_startup()
                    else:
                        return False
                except EOFError:
                    self.console.print(
                        "\n[red]No interactive input available. Assuming Docker Desktop is ready.[/red]"
                    )
                    return self._wait_for_docker_startup()

            except subprocess.TimeoutExpired:
                self.console.print(
                    "❌ Installation timed out. Please try manual installation."
                )
                return False
            except subprocess.CalledProcessError as e:
                self.console.print(f"❌ Installation failed: {e.stderr}")
                self.console.print(
                    "Falling back to manual installation instructions..."
                )
                self._show_docker_installation_instructions()
                return self._wait_for_docker_installation()

        return False

    def _wait_for_docker_startup(self) -> bool:
        """Wait for Docker Desktop to start up after installation"""
        self.console.print("\n⏳ Waiting for Docker Desktop to start...")

        max_attempts = 18  # 3 minutes with 10-second intervals
        for attempt in range(max_attempts):
            if self._is_docker_installed():
                try:
                    # Try to connect to Docker daemon
                    subprocess.run(
                        ["docker", "info"], check=True, capture_output=True, timeout=5
                    )
                    self.console.print("✅ Docker Desktop is running!")
                    return True
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    pass

            if attempt < max_attempts - 1:
                time.sleep(10)

        self.console.print(
            "⚠️ Docker Desktop may still be starting. Please ensure it's running and try again."
        )
        return False

    def _wait_for_docker_installation(self) -> bool:
        """Wait for user to install Docker"""
        self.console.print(
            "\n[yellow]Please install Docker Desktop following the instructions above.[/yellow]"
        )

        while True:
            try:
                if Confirm.ask("Have you completed the Docker installation?"):
                    if self._is_docker_installed():
                        self.console.print("✓ Docker installation detected")
                        return True
                    else:
                        self.console.print(
                            "❌ Docker not detected. Please ensure it's properly installed."
                        )
                        try:
                            if not Confirm.ask("Try again?"):
                                return False
                        except EOFError:
                            self.console.print(
                                "\n[red]No interactive input available. Stopping installation.[/red]"
                            )
                            return False
                else:
                    try:
                        if not Confirm.ask("Continue waiting for Docker installation?"):
                            return False
                    except EOFError:
                        self.console.print(
                            "\n[red]No interactive input available. Stopping installation.[/red]"
                        )
                        return False
            except EOFError:
                self.console.print(
                    "\n[red]No interactive input available. Stopping installation.[/red]"
                )
                return False

    def _get_existing_container(self):
        """Get existing SQL Server container if it exists"""
        try:
            return self.docker_client.containers.get(self.sql_container_name)
        except docker.errors.NotFound:
            return None

    def _create_sql_container(self):
        """Create SQL Server Express container"""
        # Create volume for persistent data
        try:
            self.docker_client.volumes.get("pyforge-sql-data")
        except docker.errors.NotFound:
            self.docker_client.volumes.create("pyforge-sql-data")

        # Create MDF files volume
        try:
            self.docker_client.volumes.get("pyforge-mdf-files")
        except docker.errors.NotFound:
            self.docker_client.volumes.create("pyforge-mdf-files")

        # Container configuration
        container_config = {
            "image": self.sql_image,
            "name": self.sql_container_name,
            "environment": {
                "ACCEPT_EULA": "Y",
                "SA_PASSWORD": self.sql_password,
                "MSSQL_PID": "Express",
            },
            "ports": {f"{self.sql_port}/tcp": self.sql_port},
            "volumes": {
                "pyforge-sql-data": {"bind": "/var/opt/mssql", "mode": "rw"},
                "pyforge-mdf-files": {"bind": "/mdf-files", "mode": "rw"},
            },
            "detach": True,
            "restart_policy": {"Name": "unless-stopped"},
        }

        return self.docker_client.containers.run(**container_config)

    def _wait_for_sql_server(self) -> bool:
        """Wait for SQL Server to be ready"""
        self.console.print(
            "⏳ Waiting for SQL Server to start (this may take a minute)..."
        )

        max_attempts = 30  # 5 minutes with 10-second intervals

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Starting SQL Server...", total=max_attempts)

            for _attempt in range(max_attempts):
                if self._test_sql_connection():
                    progress.update(task, description="✓ SQL Server is ready")
                    self.console.print("✓ SQL Server is ready")
                    return True

                progress.advance(task)
                time.sleep(10)

        self.console.print("❌ SQL Server failed to start within timeout")
        return False

    def _test_sql_connection(self) -> bool:
        """Test SQL Server connection"""
        try:
            container = self.docker_client.containers.get(self.sql_container_name)
            if container.status != "running":
                return False

            # Test connection using sqlcmd inside container
            exec_result = container.exec_run(
                [
                    "/opt/mssql-tools18/bin/sqlcmd",
                    "-S",
                    "localhost",
                    "-U",
                    "sa",
                    "-P",
                    self.sql_password,
                    "-Q",
                    "SELECT 1",
                    "-C",  # Trust server certificate
                ]
            )

            return exec_result.exit_code == 0

        except Exception:
            return False

    def _save_configuration(self) -> None:
        """Save configuration to ~/.pyforge/mdf-config.json"""
        config = {
            "sql_server": {
                "container_name": self.sql_container_name,
                "image": self.sql_image,
                "host": "localhost",
                "port": self.sql_port,
                "username": "sa",
                "password": self.sql_password,
                "data_volume": "pyforge-sql-data",
                "mdf_volume": "pyforge-mdf-files",
            },
            "docker": {
                "installed_version": self._get_docker_version(),
                "installation_date": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            "installer_version": "1.0.0",
        }

        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Save configuration
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def _get_docker_version(self) -> str:
        """Get Docker version"""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def _display_connection_info(self) -> None:
        """Display SQL Server connection information"""
        info_table = Table(title="SQL Server Connection Details")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")

        info_table.add_row("Host", "localhost")
        info_table.add_row("Port", str(self.sql_port))
        info_table.add_row("Username", "sa")
        info_table.add_row("Password", self.sql_password)
        info_table.add_row("Container", self.sql_container_name)
        info_table.add_row("Config File", str(self.config_path))

        self.console.print(info_table)

    def _show_next_steps(self) -> None:
        """Show next steps after installation"""
        self.console.print(
            "\n[bold green]🎉 Setup completed successfully![/bold green]"
        )

        next_steps = [
            "You can now process MDF files using:",
            "  [cyan]pyforge install mdf-converter[/cyan]  # Install the MDF converter",
            "",
            "Container management commands:",
            "  [cyan]pyforge mdf-tools status[/cyan]      # Check status",
            "  [cyan]pyforge mdf-tools start[/cyan]       # Start SQL Server",
            "  [cyan]pyforge mdf-tools stop[/cyan]        # Stop SQL Server",
            "  [cyan]pyforge mdf-tools logs[/cyan]        # View logs",
        ]

        self.console.print(
            Panel("\n".join(next_steps), title="Next Steps", border_style="green")
        )

    # Container management methods
    def get_status(self) -> Dict[str, Any]:
        """Get status of Docker and SQL Server"""
        status = {
            "docker_installed": self._is_docker_installed(),
            "docker_running": False,
            "sql_container_exists": False,
            "sql_container_running": False,
            "sql_server_responding": False,
            "config_exists": self.config_path.exists(),
        }

        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            status["docker_running"] = True

            container = self._get_existing_container()
            if container:
                status["sql_container_exists"] = True
                status["sql_container_running"] = container.status == "running"

                if status["sql_container_running"]:
                    status["sql_server_responding"] = self._test_sql_connection()
        except Exception:
            pass

        return status

    def start_container(self) -> bool:
        """Start SQL Server container"""
        try:
            if not DOCKER_AVAILABLE:
                self.console.print(
                    "❌ Docker SDK not available. Run 'pyforge install mdf-tools' first."
                )
                return False

            if not self.docker_client:
                import docker

                self.docker_client = docker.from_env()

            container = self._get_existing_container()
            if not container:
                self.console.print(
                    "❌ SQL Server container not found. Run installation first."
                )
                return False

            if container.status == "running":
                self.console.print("✓ SQL Server container is already running")
                return True

            self.console.print("🚀 Starting SQL Server container...")
            container.start()

            # Wait for SQL Server to be ready
            return self._wait_for_sql_server()

        except Exception as e:
            self.console.print(f"❌ Failed to start container: {e}")
            return False

    def stop_container(self) -> bool:
        """Stop SQL Server container"""
        try:
            if not DOCKER_AVAILABLE:
                self.console.print(
                    "❌ Docker SDK not available. Run 'pyforge install mdf-tools' first."
                )
                return False

            if not self.docker_client:
                import docker

                self.docker_client = docker.from_env()

            container = self._get_existing_container()
            if not container:
                self.console.print("❌ SQL Server container not found")
                return False

            if container.status != "running":
                self.console.print("✓ SQL Server container is already stopped")
                return True

            self.console.print("🛑 Stopping SQL Server container...")
            container.stop()
            self.console.print("✓ SQL Server container stopped")
            return True

        except Exception as e:
            self.console.print(f"❌ Failed to stop container: {e}")
            return False

    def restart_container(self) -> bool:
        """Restart SQL Server container"""
        try:
            if self.stop_container():
                time.sleep(2)  # Brief pause
                return self.start_container()
            return False
        except Exception as e:
            self.console.print(f"❌ Failed to restart container: {e}")
            return False

    def show_logs(self, lines: int = 50) -> None:
        """Show SQL Server container logs"""
        try:
            if not DOCKER_AVAILABLE:
                self.console.print(
                    "❌ Docker SDK not available. Run 'pyforge install mdf-tools' first."
                )
                return

            if not self.docker_client:
                import docker

                self.docker_client = docker.from_env()

            container = self._get_existing_container()
            if not container:
                self.console.print("❌ SQL Server container not found")
                return

            logs = container.logs(tail=lines, timestamps=True).decode("utf-8")
            self.console.print(
                f"[bold]Last {lines} lines from SQL Server container:[/bold]"
            )
            self.console.print(logs)

        except Exception as e:
            self.console.print(f"❌ Failed to get logs: {e}")

    def uninstall(self) -> bool:
        """Uninstall SQL Server container and clean up"""
        try:
            if not DOCKER_AVAILABLE:
                self.console.print(
                    "❌ Docker SDK not available. Run 'pyforge install mdf-tools' first."
                )
                return False

            try:
                if not Confirm.ask(
                    "Are you sure you want to remove SQL Server and all data?"
                ):
                    return False
            except EOFError:
                self.console.print(
                    "\n[red]No interactive input available. Cancelling uninstall for safety.[/red]"
                )
                return False

            if not self.docker_client:
                import docker

                self.docker_client = docker.from_env()

            # Stop and remove container
            container = self._get_existing_container()
            if container:
                self.console.print("🛑 Stopping and removing container...")
                container.stop()
                container.remove()
                self.console.print("✓ Container removed")

            # Remove volumes
            try:
                volume = self.docker_client.volumes.get("pyforge-sql-data")
                volume.remove()
                self.console.print("✓ Data volume removed")
            except (
                Exception
            ):  # Catch all Docker exceptions when module might not be available
                pass

            try:
                mdf_volume = self.docker_client.volumes.get("pyforge-mdf-files")
                mdf_volume.remove()
                self.console.print("✓ MDF files volume removed")
            except (
                Exception
            ):  # Catch all Docker exceptions when module might not be available
                pass

            # Remove config file
            if self.config_path.exists():
                self.config_path.unlink()
                self.console.print("✓ Configuration file removed")

            self.console.print("✅ [green]Uninstall completed successfully[/green]")
            return True

        except Exception as e:
            self.console.print(f"❌ Failed to uninstall: {e}")
            return False
