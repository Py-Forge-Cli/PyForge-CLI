"""UCanAccess JAR dependency manager with bundled JAR and auto-download fallback."""

import hashlib
import logging
import urllib.request
from pathlib import Path
from typing import Optional


class UCanAccessJARManager:
    """Manages UCanAccess JAR dependencies with bundled JAR and automatic download fallback."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Bundled JAR location (shipped with package)
        self.bundled_jar_dir = Path(__file__).parent.parent / "data" / "jars"
        self.bundled_jar_name = "ucanaccess-4.0.4.jar"

        # User cache directory for downloaded JARs
        self.cache_jar_dir = Path.home() / ".pyforge" / "jars"
        self.cache_jar_dir.mkdir(parents=True, exist_ok=True)
        self.cache_jar_name = "ucanaccess-4.0.4.jar"

        # Download configuration - Use Java 8 compatible version
        self.jar_url = "https://repo1.maven.org/maven2/net/sf/ucanaccess/ucanaccess/4.0.4/ucanaccess-4.0.4.jar"
        self.expected_size = 390000  # ~390KB for individual JAR
        # Note: In production, you should verify the SHA256 hash for security
        self.expected_sha256 = None  # Would be actual hash in production

    def ensure_jar_available(self) -> bool:
        """Ensure UCanAccess JAR is available, using bundled JAR or downloading if needed.

        Returns:
            True if JAR is available and valid, False otherwise
        """
        # First, try bundled JAR (shipped with package)
        bundled_jar_path = self.bundled_jar_dir / self.bundled_jar_name
        if bundled_jar_path.exists() and self._is_valid_jar(bundled_jar_path):
            self.logger.debug(f"Using bundled UCanAccess JAR: {bundled_jar_path}")
            return True

        # Fallback to cached JAR (downloaded previously)
        cache_jar_path = self.cache_jar_dir / self.cache_jar_name
        if cache_jar_path.exists() and self._is_valid_jar(cache_jar_path):
            self.logger.debug(f"Using cached UCanAccess JAR: {cache_jar_path}")
            return True

        # Last resort: download JAR
        self.logger.info("UCanAccess JAR not found, downloading...")
        return self._download_jar(cache_jar_path)

    def get_jar_path(self) -> str:
        """Get path to UCanAccess JAR (bundled or cached).

        Returns:
            Absolute path to JAR file

        Raises:
            FileNotFoundError: If JAR is not available
        """
        # Check bundled JAR first
        bundled_jar_path = self.bundled_jar_dir / self.bundled_jar_name
        if bundled_jar_path.exists() and self._is_valid_jar(bundled_jar_path):
            return str(bundled_jar_path)

        # Check cached JAR
        cache_jar_path = self.cache_jar_dir / self.cache_jar_name
        if cache_jar_path.exists() and self._is_valid_jar(cache_jar_path):
            return str(cache_jar_path)

        raise FileNotFoundError(
            f"UCanAccess JAR not found. Checked:\n"
            f"  - Bundled: {bundled_jar_path}\n"
            f"  - Cached: {cache_jar_path}\n"
            "Call ensure_jar_available() first."
        )

    def _download_jar(self, jar_path: Path) -> bool:
        """Download UCanAccess JAR with progress reporting.

        Args:
            jar_path: Path where JAR should be saved

        Returns:
            True if download successful and valid, False otherwise
        """
        try:
            # Import click here to avoid circular imports
            import click

            self.logger.info("Downloading UCanAccess JAR (first time setup)...")

            # Create a progress bar for the download
            with click.progressbar(
                length=self.expected_size, label="Downloading UCanAccess"
            ) as bar:

                def progress_hook(block_num: int, block_size: int, total_size: int):
                    """Progress callback for urllib.request.urlretrieve."""
                    if total_size > 0:
                        downloaded = min(block_num * block_size, total_size)
                        bar.update(downloaded - bar.pos)

                urllib.request.urlretrieve(
                    self.jar_url, jar_path, reporthook=progress_hook
                )

            # Validate the downloaded JAR
            if self._is_valid_jar(jar_path):
                self.logger.info("UCanAccess JAR downloaded successfully")
                return True
            else:
                self.logger.error("Downloaded JAR is invalid")
                jar_path.unlink()  # Remove invalid file
                return False

        except Exception as e:
            self.logger.error(f"Failed to download UCanAccess JAR: {e}")
            if jar_path.exists():
                jar_path.unlink()  # Remove incomplete download
            return False

    def _is_valid_jar(self, jar_path: Path) -> bool:
        """Validate JAR file integrity.

        Args:
            jar_path: Path to JAR file to validate

        Returns:
            True if JAR appears valid, False otherwise
        """
        try:
            if not jar_path.exists():
                return False

            # Check file size (should be approximately 390KB for individual JAR or 3.3MB for uber JAR)
            size = jar_path.stat().st_size
            if size < 300_000 or size > 5_000_000:  # 300KB-5MB range for JAR files
                self.logger.warning(f"JAR size {size} outside expected range")
                return False

            # Check if it's a ZIP/JAR file (basic magic number check)
            with open(jar_path, "rb") as f:
                magic = f.read(4)
                if magic != b"PK\x03\x04":  # ZIP file signature
                    self.logger.warning("JAR file doesn't have ZIP signature")
                    return False

            # If we have expected SHA256, verify it
            if self.expected_sha256:
                if not self._verify_sha256(jar_path):
                    self.logger.warning("JAR SHA256 hash verification failed")
                    return False

            return True

        except Exception as e:
            self.logger.warning(f"JAR validation failed: {e}")
            return False

    def _verify_sha256(self, jar_path: Path) -> bool:
        """Verify JAR file SHA256 hash.

        Args:
            jar_path: Path to JAR file

        Returns:
            True if hash matches expected value, False otherwise
        """
        try:
            with open(jar_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash == self.expected_sha256
        except Exception as e:
            self.logger.warning(f"SHA256 verification failed: {e}")
            return False

    def get_jar_info(self) -> Optional[dict]:
        """Get information about the current JAR.

        Returns:
            Dictionary with JAR information or None if not available
        """
        try:
            jar_path = Path(self.get_jar_path())
            stat = jar_path.stat()

            # Determine if it's bundled or cached
            bundled_path = self.bundled_jar_dir / self.bundled_jar_name
            is_bundled = jar_path == bundled_path

            return {
                "path": str(jar_path),
                "size": stat.st_size,
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "modified": stat.st_mtime,
                "exists": True,
                "valid": self._is_valid_jar(jar_path),
                "source": "bundled" if is_bundled else "cached",
            }
        except FileNotFoundError:
            return {
                "bundled_path": str(self.bundled_jar_dir / self.bundled_jar_name),
                "cached_path": str(self.cache_jar_dir / self.cache_jar_name),
                "exists": False,
                "valid": False,
            }
