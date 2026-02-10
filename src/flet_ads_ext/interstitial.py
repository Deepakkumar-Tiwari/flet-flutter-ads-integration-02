import traceback
import logging
import os
import glob
from datetime import datetime
from typing import List, Dict, Optional, Union

import os
from datetime import datetime


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

    # Create console handler (optional - can be removed if you don't want terminal output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(
        logging.WARNING
    )  # Only show warnings and errors in console

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - DEEPAK - %(message)s",
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
        """Initialize with logger"""
        self.logger = _interstitial_logger
        self.log_file = _log_file_path
        self.logger.info(f"InterstitialAd instance created")
        # Extract unit_id before calling parent
        self.unit_id = kwargs.pop("unit_id", None)
        super().__init__(*args, **kwargs)

    def __post_init__(self, *args, **kwargs):
        """Override post_init to add error handling with file logging"""
        try:
            self.logger.debug(
                f"Calling __post_init__ for service ID: {getattr(self, '_i', 'Unknown')}"
            )
            # Call parent's __post_init__ if it exists
            super().__post_init__(*args, **kwargs)
        except Exception as e:
            error_msg = f"ERROR in InterstitialAd.__post_init__: {e}"
            self.logger.error(error_msg, exc_info=True)  # exc_info=True adds traceback
            raise

    def init(self):
        """Override init to add error handling around registration"""
        service_id = getattr(self, "_i", "Unknown")
        service_class = getattr(self, "_c", "Unknown")

        self.logger.info(f"Initializing service {service_class} (ID: {service_id})")

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

    def get_log_file_path(self):
        """Get the path to the log file (useful for debugging)"""
        return self.log_file

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
