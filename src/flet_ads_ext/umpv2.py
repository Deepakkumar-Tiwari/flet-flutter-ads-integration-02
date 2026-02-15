import flet as ft
from typing import Optional, List, Any


class UserMessagingPlatformv2(ft.Control):
    def __init__(
        self,
        test_device_ids: Optional[List[str]] = None,
        on_initialized: Optional[ft.ControlEventHandler] = None,
        on_error: Optional[ft.ControlEventHandler] = None,
    ):
        super().__init__()
        self.test_device_ids = test_device_ids
        self.on_initialized = on_initialized
        self.on_error = on_error

    def _get_control_name(self):
        return "UserMessagingPlatformv2"

    def before_update(self):
        super().before_update()
        # Properties (Configuration) still go through before_update
        if self.test_device_ids:
            self.__setattr__("testDeviceIds", self.test_device_ids)

    # ACTION: Triggered via Method Channel
    def show_privacy_options(self):
        self.invoke_method("show_privacy_options")
