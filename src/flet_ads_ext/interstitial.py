import traceback
import logging
import os
import glob
from datetime import datetime
from typing import List, Dict, Optional, Union
import flet as ft
from flet_ads_ext.types import AdRequest
from dataclasses import field
from flet.controls.context import _context_page, context


# Set up file logger for InterstitialAd class
def setup_interstitial_logger():
    """Setup dedicated logger for InterstitialAd with file output"""

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create unique log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"interstitial_ad_{timestamp}.log")

    # Create logger
    logger = logging.getLogger("InterstitialAd")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Create console handler (optional)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger, log_file


# Global logger instance
_interstitial_logger, _log_file_path = setup_interstitial_logger()


@ft.control("InterstitialAd")
class InterstitialAd(ft.Service):
    # class InterstitialAd(ft.Control):
    """
    Displays a full-screen interstitial ad.

    Raises:
        FletUnsupportedPlatformException: When using this control on a
            web and/or non-mobile platform.
    """

    unit_id: str
    """
    Ad unit ID for this ad.
    """

    request: AdRequest = field(default_factory=lambda: AdRequest())
    """
    Targeting information used to fetch an Ad.
    """

    on_load: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when this ad is loaded successfully.
    """

    on_error: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when an ad request failed.

    Event handler argument [`data`][flet.Event.data] property
    contains information about the error.
    """

    on_open: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when this ad opens up.

    A full screen view/overlay is presented in response to the user clicking
    on an ad. You may want to pause animations and time sensitive
    interactions.
    """

    on_close: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when the full screen view has been closed. You should restart
    anything paused while handling [`on_open`][flet_ads.BaseAd.on_open].
    """

    on_impression: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when an impression occurs on this ad.
    """

    on_click: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when this ad is clicked.
    """

    on_log: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when this ad emits log.

    Event handler argument [`data`][flet.Event.data] property
    contains information about the log.
    """

    # def before_update(self):
    #     if self.page.web or not self.page.platform.is_mobile():
    #         raise ft.FletUnsupportedPlatformException(
    #             f"{self.__class__.__name__} is only supported on "
    #             f"Mobile (Android and iOS)"
    #         )
    def __init__(self, *args, **kwargs):
        """Initialize with all expected parameters"""
        # Setup logging
        self.logger = _interstitial_logger
        self.log_file = _log_file_path

        # Log the initialization attempt
        self.logger.info(f"InterstitialAd instance creation started")

        # List of all parameters that InterstitialAd accepts but parent doesn't
        interstitial_params = [
            "unit_id",
            "request",
            "on_load",
            "on_error",
            "on_open",
            "on_close",
            "on_impression",
            "on_click",
            "on_log",
        ]

        # # Log what parameters we received
        # if kwargs:
        #     self.logger.debug(f"Received kwargs: {list(kwargs.keys())}")

        # Extract and store all InterstitialAd-specific parameters
        for param in interstitial_params:
            if param in kwargs:
                value = kwargs.pop(param)
                setattr(self, param, value)
                # self.logger.debug(f"Set {param} = {value}")
            else:
                # Set default values for missing parameters
                if param == "request":
                    setattr(self, param, AdRequest())
                else:
                    setattr(self, param, None)

        # Log remaining kwargs (should be parent class parameters)
        if kwargs:
            self.logger.debug(f"Passing to parent: {list(kwargs.keys())}")

        try:
            # Call parent constructor with remaining kwargs
            super().__init__(*args, **kwargs)
            # Post_INIT__ gets triggered
            self.logger.info(f"InterstitialAd instance created successfully")

            # Log the instance details
            self.logger.debug(f"Service ID: {getattr(self, '_i', 'Unknown')}")
            self.logger.debug(f"Service Class: {getattr(self, '_c', 'Unknown')}")
            if hasattr(self, "unit_id"):
                self.logger.debug(f"Unit ID: {self.unit_id}")

        except Exception as e:
            error_msg = f"ERROR in InterstitialAd.__init__: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise

    def __post_init__(self, *args, **kwargs):
        """Override post_init to add error handling with file logging"""
        try:
            self.logger.debug(
                f"Calling __post_init__ for service ID: {getattr(self, '_i', 'Unknown')}"
            )

            # Check if there are unexpected kwargs in __post_init__
            if kwargs:
                self.logger.warning(
                    f"Unexpected kwargs in __post_init__: {list(kwargs.keys())}"
                )

            # Call parent's __post_init__ if it exists
            super().__post_init__(*args, **kwargs)

        except Exception as e:
            error_msg = f"ERROR in InterstitialAd.__post_init__: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise

    def init(self):
        """Override init to add error handling around registration"""
        service_id = getattr(self, "_i", "Unknown")
        service_class = getattr(self, "_c", "Unknown")

        self.logger.info(f"Initializing service {service_class} (ID: {service_id})")

        # Log all event handlers status
        event_handlers = [
            "on_load",
            "on_error",
            "on_open",
            "on_close",
            "on_impression",
            "on_click",
            "on_log",
        ]
        for handler in event_handlers:
            if hasattr(self, handler) and getattr(self, handler) is not None:
                self.logger.debug(f"{handler} handler is set")
            else:
                self.logger.debug(f"{handler} handler is not set")

        try:
            # Call parent's init
            super().init()

            # Check if registration worked
            self._debug_registration_status()

            self.logger.info(
                f"Service {service_class} (ID: {service_id}) initialization completed"
            )

        except Exception as e:
            error_msg = (
                f"Failed to register service {service_class} (ID: {service_id}): {e}"
            )
            self.logger.error(error_msg, exc_info=True)

    def _debug_registration_status(self):
        """Check and log registration status to file"""
        service_id = getattr(self, "_i", "Unknown")

        try:
            _context_page.set(self.page)
            # Try to access the service registry
            if hasattr(context, "page") and context.page:
                if hasattr(context.page, "_services"):
                    registry = context.page._services
                    registry_id = getattr(registry, "_i", "Unknown")

                    self.logger.debug(f"Found registry {registry_id} on page")

                    # Check if this service is in the registry
                    if hasattr(registry, "_lock"):
                        with registry._lock:
                            if hasattr(registry, "_services"):
                                is_registered = any(
                                    getattr(s, "_i", None) == getattr(self, "_i", None)
                                    for s in registry._services
                                )
                                if is_registered:
                                    self.logger.info(
                                        f"Service {service_id} successfully registered in registry {registry_id}"
                                    )
                                else:
                                    self.logger.warning(
                                        f"Service {service_id} NOT found in registry {registry_id}"
                                    )

                                # Log all services in registry for debugging
                                service_count = len(registry._services)
                                self.logger.debug(
                                    f"Registry {registry_id} contains {service_count} services"
                                )

                                for i, service in enumerate(registry._services):
                                    self.logger.debug(
                                        f"  [{i}] {getattr(service, '_c', 'Unknown')} (ID: {getattr(service, '_i', 'Unknown')})"
                                    )
                    else:
                        self.logger.warning(
                            f"Registry {registry_id} has no _lock attribute"
                        )
                else:
                    self.logger.error(f"No _services attribute on page")
            else:
                self.logger.error(f"No page in context")
        except Exception as e:
            self.logger.error(
                f"Could not check registration status: {e}", exc_info=True
            )

    async def show(self):
        service_id = getattr(self, "_i", "Unknown")
        self.logger.info(f"show() method called for service {service_id}")

        try:
            await self._invoke_method("show")
            self.logger.info(f"show() method completed for service {service_id}")
        except Exception as e:
            error_msg = f"ERROR in InterstitialAd.show() for service {service_id}: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise

    # ===== LOG FILE READING METHODS =====

    def get_log_file_path(self) -> str:
        """Get the path to the current log file"""
        return self.log_file

    def read_current_log_file(self, max_lines: Optional[int] = None) -> str:
        """
        Read the current log file

        Args:
            max_lines: Optional limit on number of lines to return (from end of file)

        Returns:
            String containing log file contents
        """
        try:
            if not os.path.exists(self.log_file):
                return "Log file does not exist."

            with open(self.log_file, "r", encoding="utf-8") as f:
                if max_lines is None:
                    return f.read()
                else:
                    lines = f.readlines()
                    return "".join(lines[-max_lines:])

        except Exception as e:
            return f"Error reading log file: {e}"

    def read_log_file(self, file_path: str, max_lines: Optional[int] = None) -> str:
        """
        Read a specific log file

        Args:
            file_path: Path to the log file to read
            max_lines: Optional limit on number of lines

        Returns:
            String containing log file contents
        """
        try:
            if not os.path.exists(file_path):
                return f"Log file does not exist: {file_path}"

            with open(file_path, "r", encoding="utf-8") as f:
                if max_lines is None:
                    return f.read()
                else:
                    lines = f.readlines()
                    return "".join(lines[-max_lines:])

        except Exception as e:
            return f"Error reading log file {file_path}: {e}"

    def get_all_log_files(self) -> List[Dict[str, str]]:
        """
        Get a list of all interstitial log files

        Returns:
            List of dictionaries with file info: path, filename, size, modified_time
        """
        log_dir = "interstitial_logs"
        if not os.path.exists(log_dir):
            return []

        log_files = []
        for file_path in glob.glob(os.path.join(log_dir, "interstitial_ad_*.log")):
            try:
                file_stats = os.stat(file_path)
                log_files.append(
                    {
                        "path": file_path,
                        "filename": os.path.basename(file_path),
                        "size_bytes": file_stats.st_size,
                        "size_kb": file_stats.st_size / 1024,
                        "modified_time": datetime.fromtimestamp(file_stats.st_mtime),
                        "created_time": datetime.fromtimestamp(file_stats.st_ctime),
                    }
                )
            except Exception as e:
                self.logger.error(f"Error getting info for log file {file_path}: {e}")

        # Sort by modified time (newest first)
        log_files.sort(key=lambda x: x["modified_time"], reverse=True)
        return log_files

    def search_logs(
        self,
        search_term: str,
        case_sensitive: bool = False,
        file_path: Optional[str] = None,
    ) -> List[Dict[str, Union[str, int]]]:
        """
        Search for a term in log files

        Args:
            search_term: Term to search for
            case_sensitive: Whether search should be case sensitive
            file_path: Specific file to search (None searches all files)

        Returns:
            List of matches with file info and line numbers
        """
        matches = []
        search_term_lower = search_term if case_sensitive else search_term.lower()

        files_to_search = []
        if file_path:
            if os.path.exists(file_path):
                files_to_search = [file_path]
            else:
                return []
        else:
            # Search all log files
            log_dir = "interstitial_logs"
            if not os.path.exists(log_dir):
                return []
            files_to_search = glob.glob(os.path.join(log_dir, "interstitial_ad_*.log"))

        for file_path in files_to_search:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        search_line = line if case_sensitive else line.lower()
                        if search_term_lower in search_line:
                            matches.append(
                                {
                                    "file": file_path,
                                    "filename": os.path.basename(file_path),
                                    "line_number": line_num,
                                    "line": line.strip(),
                                    "highlighted_line": (
                                        line.replace(
                                            search_term, f"\033[91m{search_term}\033[0m"
                                        )
                                        if case_sensitive
                                        else self._highlight_text(line, search_term)
                                    ),
                                }
                            )
            except Exception as e:
                self.logger.error(f"Error searching file {file_path}: {e}")

        return matches

    def _highlight_text(self, text: str, search_term: str) -> str:
        """Helper method to highlight search term in text (case-insensitive)"""
        import re

        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        return pattern.sub(f"\033[91m{search_term}\033[0m", text)

    def get_log_statistics(self) -> Dict[str, Union[int, Dict[str, int]]]:
        """
        Get statistics about log files

        Returns:
            Dictionary with log statistics
        """
        log_dir = "interstitial_logs"
        if not os.path.exists(log_dir):
            return {"total_files": 0, "total_size_bytes": 0}

        log_files = glob.glob(os.path.join(log_dir, "interstitial_ad_*.log"))

        total_size = 0
        level_counts = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}

        for file_path in log_files:
            try:
                total_size += os.path.getsize(file_path)

                # Count log levels in current file
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if " - DEBUG - " in line:
                            level_counts["DEBUG"] += 1
                        elif " - INFO - " in line:
                            level_counts["INFO"] += 1
                        elif " - WARNING - " in line:
                            level_counts["WARNING"] += 1
                        elif " - ERROR - " in line:
                            level_counts["ERROR"] += 1
                        elif " - CRITICAL - " in line:
                            level_counts["CRITICAL"] += 1

            except Exception as e:
                self.logger.error(
                    f"Error processing file {file_path} for statistics: {e}"
                )

        return {
            "total_files": len(log_files),
            "total_size_bytes": total_size,
            "total_size_kb": total_size / 1024,
            "total_size_mb": total_size / (1024 * 1024),
            "level_counts": level_counts,
            "current_log_file": self.log_file,
            "current_log_size_bytes": (
                os.path.getsize(self.log_file) if os.path.exists(self.log_file) else 0
            ),
        }

    def cleanup_old_logs(
        self, days_to_keep: int = 7
    ) -> Dict[str, Union[int, List[str]]]:
        """
        Clean up log files older than specified days

        Args:
            days_to_keep: Number of days to keep logs

        Returns:
            Dictionary with cleanup results
        """
        from datetime import timedelta

        log_dir = "interstitial_logs"
        if not os.path.exists(log_dir):
            return {"deleted": 0, "kept": 0, "deleted_files": []}

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        log_files = glob.glob(os.path.join(log_dir, "interstitial_ad_*.log"))

        deleted_files = []
        kept_files = []

        for file_path in log_files:
            try:
                # Get file modification time
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                if mtime < cutoff_date:
                    os.remove(file_path)
                    deleted_files.append(os.path.basename(file_path))
                    self.logger.info(f"Removed old log file: {file_path}")
                else:
                    kept_files.append(os.path.basename(file_path))

            except Exception as e:
                self.logger.error(f"Error removing file {file_path}: {e}")

        return {
            "deleted": len(deleted_files),
            "kept": len(kept_files),
            "deleted_files": deleted_files,
            "kept_files": kept_files,
        }

    def get_recent_errors(self, count: int = 10) -> List[Dict[str, str]]:
        """
        Get recent error entries from all log files

        Args:
            count: Maximum number of error entries to return

        Returns:
            List of error entries with details
        """
        errors = []
        log_dir = "interstitial_logs"

        if not os.path.exists(log_dir):
            return errors

        # Get all log files sorted by modification time (newest first)
        log_files = sorted(
            glob.glob(os.path.join(log_dir, "interstitial_ad_*.log")),
            key=os.path.getmtime,
            reverse=True,
        )

        for file_path in log_files:
            if len(errors) >= count:
                break

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if " - ERROR - " in line:
                            errors.append(
                                {
                                    "file": os.path.basename(file_path),
                                    "timestamp": (
                                        line.split(" - ")[0]
                                        if " - " in line
                                        else "Unknown"
                                    ),
                                    "message": (
                                        " - ".join(line.split(" - ")[3:]).strip()
                                        if len(line.split(" - ")) > 3
                                        else line.strip()
                                    ),
                                }
                            )
                            if len(errors) >= count:
                                break
            except Exception as e:
                self.logger.error(f"Error reading file {file_path} for errors: {e}")

        return errors[:count]
