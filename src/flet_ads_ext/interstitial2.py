import flet as ft
from typing import Any, Optional, Union

from flet import AnimationValue

# from flet.controls import OptionalNumber
from flet import Ref
from flet import ConstrainedControl
from flet import OffsetValue

# from flet.control import OptionalControlEventCallable
from flet.controls.page import PagePlatform
from flet import ResponsiveNumber
from flet import RotateValue
from flet import ScaleValue
from flet_ads_ext.types import AdRequest
from dataclasses import field


class BaseAd(ConstrainedControl):
    def __init__(
        self,
        unit_id: str,
        on_load=None,
        on_error=None,
        on_open=None,
        on_close=None,
        on_impression=None,
        on_click=None,
        on_will_dismiss=None,
        #
        # ConstrainedControl
        #
        ref: Optional[Ref] = None,
        key: Optional[str] = None,
        width=None,
        height=None,
        left=None,
        top=None,
        right=None,
        bottom=None,
        expand: Union[None, bool, int] = None,
        expand_loose: Optional[bool] = None,
        col: Optional[ResponsiveNumber] = None,
        opacity=None,
        rotate: RotateValue = None,
        scale: ScaleValue = None,
        offset: OffsetValue = None,
        aspect_ratio=None,
        animate_opacity: AnimationValue = None,
        animate_size: AnimationValue = None,
        animate_position: AnimationValue = None,
        animate_rotation: AnimationValue = None,
        animate_scale: AnimationValue = None,
        animate_offset: AnimationValue = None,
        on_animation_end=None,
        tooltip: Optional[str] = None,
        visible: Optional[bool] = None,
        disabled: Optional[bool] = None,
        data: Any = None,
    ):
        ConstrainedControl.__init__(
            self,
            ref=ref,
            key=key,
            width=width,
            height=height,
            left=left,
            top=top,
            right=right,
            bottom=bottom,
            expand=expand,
            expand_loose=expand_loose,
            col=col,
            opacity=opacity,
            rotate=rotate,
            scale=scale,
            offset=offset,
            aspect_ratio=aspect_ratio,
            animate_opacity=animate_opacity,
            animate_size=animate_size,
            animate_position=animate_position,
            animate_rotation=animate_rotation,
            animate_scale=animate_scale,
            animate_offset=animate_offset,
            on_animation_end=on_animation_end,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            data=data,
        )

        self.on_load = on_load
        self.on_error = on_error
        self.on_open = on_open
        self.on_close = on_close
        self.on_impression = on_impression
        self.on_click = on_click
        self.on_will_dismiss = on_will_dismiss
        self.unit_id = unit_id

    def before_update(self):
        assert self.page.platform in [
            PagePlatform.ANDROID,
            PagePlatform.IOS,
        ], f"{self.__class__.__name__} is only supported on Mobile (Android and iOS). "

    # # on_load
    on_load: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when this ad is loaded successfully.
    """

    # # on_error
    on_error: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when an ad request failed.

    Event handler argument [`data`][flet.Event.data] property
    contains information about the error.
    """
    # # on_open
    on_open: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when this ad opens up.

    A full screen view/overlay is presented in response to the user clicking
    on an ad. You may want to pause animations and time sensitive
    interactions.
    """
    # # on_close
    on_close: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when the full screen view has been closed. You should restart
    anything paused while handling [`on_open`][flet_ads.BaseAd.on_open].
    """
    # # on_click
    on_click: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when this ad is clicked.
    """
    # # on_impression
    on_impression: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when an impression occurs on this ad.
    """
    # # on_will_dismiss
    on_will_dismiss: Optional[ft.ControlEventHandler["BaseAd"]] = None
    """
    Called when an on_will_dismiss occurs on this ad.
    """


@ft.control("InterstitialAd")
class InterstitialAd(BaseAd):
    """
    Displays a full screen interstitial ad.

    -----

    Online docs: https://flet.dev/docs/controls/interstitialad
    """

    def __init__(
        self,
        unit_id: str,
        on_load=None,
        on_error=None,
        on_open=None,
        on_close=None,
        on_impression=None,
        on_click=None,
        #
        # ConstrainedControl
        #
        ref: Optional[Ref] = None,
        key: Optional[str] = None,
        width=None,
        height=None,
        left=None,
        top=None,
        right=None,
        bottom=None,
        expand: Union[None, bool, int] = None,
        expand_loose: Optional[bool] = None,
        col: Optional[ResponsiveNumber] = None,
        opacity=None,
        rotate: RotateValue = None,
        scale: ScaleValue = None,
        offset: OffsetValue = None,
        aspect_ratio=None,
        animate_opacity: AnimationValue = None,
        animate_size: AnimationValue = None,
        animate_position: AnimationValue = None,
        animate_rotation: AnimationValue = None,
        animate_scale: AnimationValue = None,
        animate_offset: AnimationValue = None,
        on_animation_end=None,
        tooltip: Optional[str] = None,
        visible: Optional[bool] = None,
        disabled: Optional[bool] = None,
        data: Any = None,
    ):
        BaseAd.__init__(
            self,
            unit_id=unit_id,
            on_load=on_load,
            on_error=on_error,
            on_open=on_open,
            on_close=on_close,
            on_impression=on_impression,
            on_click=on_click,
            #
            # ConstrainedControl
            #
            ref=ref,
            key=key,
            width=width,
            height=height,
            left=left,
            top=top,
            right=right,
            bottom=bottom,
            expand=expand,
            expand_loose=expand_loose,
            col=col,
            opacity=opacity,
            rotate=rotate,
            scale=scale,
            offset=offset,
            aspect_ratio=aspect_ratio,
            animate_opacity=animate_opacity,
            animate_size=animate_size,
            animate_position=animate_position,
            animate_rotation=animate_rotation,
            animate_scale=animate_scale,
            animate_offset=animate_offset,
            on_animation_end=on_animation_end,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            data=data,
        )

    unit_id: str
    """
    Ad unit ID for this ad.
    """

    request: AdRequest = field(default_factory=lambda: AdRequest())
    """
    Targeting information used to fetch an Ad.
    """

    def _get_control_name(self):
        return "interstitial_ad"

    def show(self):
        self.invoke_method("show")
