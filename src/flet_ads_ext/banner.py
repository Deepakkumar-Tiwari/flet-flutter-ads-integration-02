from typing import Optional

import flet as ft
from flet_ads_ext.base import BaseAd
from flet_ads_ext.types import PaidAdEvent


@ft.control("banner")
class BannerAd(BaseAd):
    """
    Decorator: Registers this Python class with the Flet engine.
               The string "BannerAd" must match the name used on the Flutter/Dart side
               so the bridge knows which visual component to render.

    Python  Class: Displays a banner ad.
            Raises:
                FletUnsupportedPlatformException: When this control is used on a web
                    and/or non-mobile platform.
    """

    # 1. Define the handler property
    #   Type Hinting (Optional[ft.ControlEventHandler[...]):
    #       These lines define specific events that this control can "listen" to.
    #       Flet uses these to map the events coming across the bridge (like "paid")
    #       to a Python function you write.
    #   on_will_dismiss: Specifically for iOS, triggered right before an ad overlay disappears.
    #   on_paid: This captures the onPaidEvent from the Dart code, allowing you to track ad revenue in real-time.

    on_will_dismiss: Optional[ft.ControlEventHandler["BannerAd"]] = None
    """
    Called before dismissing a full screen view.

    Note:
        Only available on iOS.
    """

    on_paid: Optional[ft.ControlEventHandler[PaidAdEvent["BannerAd"]]] = None
    """
    Called when this ad is estimated to have earned money.

    Available for allowlisted accounts only.
    """

    on_log: Optional[ft.ControlEventHandler[any]] = None
    """
    Called when a debug message is sent from the Flutter side.
    """

    # Register the event name in the control's internal event map
    def _get_control_name(self):
        return "BannerAd"

    def _before_build_command(self):
        super()._before_build_command()
        # This tells the Flet bridge to watch for the "log" event string
        self._add_event_handler("log", self.on_log)

    @property
    def ad_size(self) -> Optional[str]:
        return self._get_attr("adSize")

    @ad_size.setter
    def ad_size(self, value: Optional[str]):
        self._set_attr("adSize", value)

    @property
    def effective_unit_id(self) -> Optional[str]:
        return self._get_attr("effective_unit_id")
