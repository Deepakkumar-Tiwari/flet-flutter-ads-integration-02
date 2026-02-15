from enum import Enum
from typing import Optional, List
from dataclasses import dataclass
import flet as ft


class DebugGeography(Enum):
    DISABLED = 0
    EEA = 1
    NOT_EEA = 2
    REGULATED_US_STATE = 3
    OTHER = 4


@dataclass
class UMPEvent(ft.Event):
    """Event data sent from UMP."""

    status: Optional[str] = None
    can_request_ads: bool = False
    is_privacy_options_required: bool = False
    error: Optional[str] = None


@ft.control("UserMessagingPlatform")
class UserMessagingPlatform(ft.LayoutControl):
    """
    A logic control to manage Google User Messaging Platform (UMP) SDK.
    This control is invisible and manages the consent lifecycle.
    """

    test_device_ids: Optional[List[str]] = (None,)
    debug_geography: DebugGeography = (DebugGeography.DISABLED,)
    reset_consent_on_launch: bool = (False,)
    on_consent_status_changed: Optional[ft.ControlEventHandler[UMPEvent]] = (None,)
    on_privacy_options_required: Optional[ft.ControlEventHandler[UMPEvent]] = (None,)
    on_error: Optional[ft.ControlEventHandler[UMPEvent]] = (None,)
    ref = (None,)
    data = (None,)

    def _get_control_name(self):
        return "UserMessagingPlatform"

    async def show_privacy_options_form():
        """
        Triggers the display of the Privacy Options form (if required).
        Call this when your 'Privacy Settings' button is clicked.
        """
        await self._invoke_method("show_privacy_options_form")

    def before_update(self):
        if self.test_device_ids:
            self.__setattr__("testDeviceIds", self.test_device_ids)
        self.__setattr__("debugGeography", self.debug_geography.value)
        self.__setattr__("resetConsentOnLaunch", self.reset_consent_on_launch)
