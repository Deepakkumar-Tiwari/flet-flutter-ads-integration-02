from typing import Optional

import flet as ft
from flet_ads_ext.base_ad import BaseAd
from flet_ads_ext.types import PaidAdEvent


@ft.control("BannerAd")
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
    Typecasting ["BannerAd"] Meaning: This event belongs to a BannerAd. When the handler runs, the event object (e) 
                                      should be linked back to the BannerAd instance.
    Use case: Best when your logging function needs to access properties of the ad itself (like e.control.unit_id).
    Python example: 
        def handle_dismiss(e):
            # The IDE knows e.control is a BannerAd!
            # You can access ad-specific properties easily:
            print(f"Log from {e.control.unit_id}: {e.data}")
        on_will_dismiss=handle_dismiss

    Note:
        Only available on iOS.
    """

    on_paid: Optional[ft.ControlEventHandler[PaidAdEvent["BannerAd"]]] = None
    """
    Called when this ad is estimated to have earned money.
    Typecast PaidAdEvent["BannerAd"]: a Custom Type or a specialized class

    Available for allowlisted accounts only.
    """

    on_log: Optional[ft.ControlEventHandler[any]] = None
    """
    Called when a debug message is sent from the Flutter side.
    Typecast [any]: Any type like string, int etc.
    Python example: 
        def handle_log(e):
            # The IDE knows e.control is a BannerAd!
            # You can access ad-specific properties easily:
            print(f"Log message: {e.data}")
        on_will_dismiss=handle_log
    """

    # Register the event name in the control's internal event map
    def _get_control_name(self):
        return "BannerAd"

    def _before_build_command(self):
        super()._before_build_command()
        # This tells the Flet bridge to watch for the "log" event string
        self._add_event_handler("log", self.on_log)
