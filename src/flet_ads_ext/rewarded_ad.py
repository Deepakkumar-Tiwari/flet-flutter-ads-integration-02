from typing import Optional
import flet as ft
from flet_ads_ext.base_ad import BaseAd
from flet_ads_ext.types import RewardEvent


@ft.control("RewardedAd")
class RewardedAd(BaseAd):
    """
    Displays a full-screen rewarded ad.
    """

    on_user_earned_reward: Optional[
        ft.ControlEventHandler[RewardEvent["RewardedAd"]]
    ] = None
    """
    Called when the user earns a reward.
    Contains 'type' and 'amount' of the reward.
    """

    async def show(self):
        """
        Shows the rewarded ad.
        The 'on_user_earned_reward' event will be triggered if the user completes the action.
        """
        await self._invoke_method("show")

    def _get_control_name(self):
        return "RewardedAd"  # Must match what you use in UI

    def _get_control_props(self):
        return self.__dict__
