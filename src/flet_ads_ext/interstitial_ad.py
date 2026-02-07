import flet as ft
from flet_ads_ext.base_ad import BaseAd


@ft.control("InterstitialAd")
class InterstitialAd(BaseAd):
    """
    Displays a full-screen interstitial ad.

    Raises:
        FletUnsupportedPlatformException: When using this control on a
            web and/or non-mobile platform.
    """

    async def show(self):
        await self._invoke_method("show")

    async def show(self):
        await self._invoke_method("get_unitid")

    def _get_control_name(self):
        return "InterstitialAd"  # Must match what you use in UI

    def _get_control_props(self):
        return self.__dict__

    @property
    def effective_unit_id(self) -> Optional[str]:
        return self._get_attr("effective_unit_id")
