from typing import Optional

import flet as ft
from flet_ads_ext.base import BaseAd
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

    Note:
        Only available on iOS.
    """

    on_paid: Optional[ft.ControlEventHandler[PaidAdEvent["BannerAd"]]] = None
    """
    Called when this ad is estimated to have earned money.

    Available for allowlisted accounts only.
    """
