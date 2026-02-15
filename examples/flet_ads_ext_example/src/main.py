import flet as ft
import flet_ads_ext as fta
import flet_ads as fta2

from pathlib import Path
import asyncio
from datetime import datetime
from typing import List, Callable
import time
import traceback


class AppLoggerv1:
    def __init__(self):
        self.logs: List[dict] = []
        self.max_memory_logs = 500
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        # Callback to update the UI
        self.on_log_added: Callable[[dict], None] = None

    def logm(self, message: str, level: str = "INFO", checkpoint: str = ""):
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message,
            "checkpoint": checkpoint,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        # 1. Update In-Memory List (Instant)
        self.logs.append(entry)
        if len(self.logs) > self.max_memory_logs:
            self.logs.pop(0)

        # Trigger UI update if callback is set
        if self.on_log_added:
            self.on_log_added(entry)

    async def log(self, message: str, level: str = "INFO", checkpoint: str = ""):
        """
        An async log method that updates memory immediately and
        offloads file I/O to a background thread via asyncio.
        """
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message,
            "checkpoint": checkpoint,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        # 1. Update In-Memory List (Instant)
        self.logs.append(entry)
        if len(self.logs) > self.max_memory_logs:
            self.logs.pop(0)

        # Trigger UI update if callback is set
        if self.on_log_added:
            self.on_log_added(entry)

        # 2. Offload File I/O to a thread without blocking the event loop
        # We don't 'await' this here if we want it to be "fire and forget"
        asyncio.create_task(self._async_file_write(entry))

        return entry

    async def _async_file_write(self, entry: dict):
        """Internal helper to bridge async with blocking file writes."""

        def write_sync():
            filename = f"log_{entry['date'].replace('-', '')}.txt"
            path = self.log_dir / filename
            line = f"{entry['timestamp']} [{entry['level']}] [{entry['checkpoint']}] {entry['message']}\n"
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)

        # This moves the blocking 'write_sync' function to a separate thread
        await asyncio.to_thread(write_sync)


# Instantiate Global Logger
loggerv1 = AppLoggerv1()


def main(page: ft.Page):

    # --- UI LOGGING SETUP ---
    log_view = ft.ListView(
        expand=True,
        spacing=5,
        padding=10,
        auto_scroll=True,  # Automatically scrolls to bottom on new log
    )

    log_container = ft.Container(
        alignment=ft.Alignment.TOP_RIGHT,
        content=log_view,
        height=300,  # Fixed height for the log area
        width=200,
        border=ft.Border.all(1, ft.Colors.GREY_400),
        border_radius=10,
        bgcolor=ft.Colors.GREY_50,
    )

    def add_log_to_ui(entry):
        log_view.controls.append(
            ft.Text(
                f"[{entry['timestamp']}] {entry['level']}: {entry['message']}",
                size=12,
                font_family="monospace",
                color=(
                    ft.Colors.BLUE_GREY_800
                    if entry["level"] == "INFO"
                    else ft.Colors.RED_400
                ),
            )
        )
        page.update()

    # Link the logger to our UI function
    loggerv1.on_log_added = add_log_to_ui
    loggerv1.logm("Logger loaded.")

    # 1. Callback when user earns reward
    def handle_reward(e: fta.RewardEvent):
        print(f"User earned {e.amount} {e.type}!")
        score_text.value = f"Score: {int(score_text.data + e.amount)}"
        score_text.data += e.amount

        # Disable button until next ad loads
        show_rewardedad_btn.disabled = True
        show_rewardedad_btn.text = "Loading next reward..."
        page.update()

        # Load a new ad
        rewarded_ad.page.add(
            fta.RewardedAd(
                unit_id="ca-app-pub-3940256099942544/5224354917",
                on_load=handle_rewardedad_load,
                on_user_earned_reward=handle_reward,
            )
        )

    # 2. Callback when ad is ready
    def handle_rewardedad_load(e):
        show_rewardedad_btn.disabled = False
        show_rewardedad_btn.text = "Watch Ad for 10 Coins"
        loggerv1.logm("RewardedAd loaded event received from dart.")
        page.update()

    # 3. Define the RewardedAd Control
    rewarded_ad = fta.RewardedAd(
        unit_id="ca-app-pub-3940256099942544/5224354917",  # Android Test ID
        on_load=handle_rewardedad_load,
        on_user_earned_reward=handle_reward,
        on_error=lambda e: print(f"Ad Error: {e.data}"),
    )
    loggerv1.logm("TYPE OF rewarded_ad", type(rewarded_ad))

    try:

        iad = fta2.InterstitialAd(
            unit_id="ca-app-pub-3940256099942544/1033173712",
            on_click=lambda e: loggerv1.logm(
                "InterstitialAd clicked event received from dart."
            ),
            on_load=lambda e: loggerv1.logm(
                "InterstitialAd loaded event received from dart."
            ),
            on_error=lambda e: loggerv1.logm(
                f"InterstitialAd error event received from dart: {e.data}"
            ),
            on_open=lambda e: loggerv1.logm(
                "InterstitialAd opened event received from dart."
            ),
            on_close=lambda e: loggerv1.logm(
                "InterstitialAd closed event received from dart."
            ),
            on_impression=lambda e: loggerv1.logm(
                "InterstitialAd impression event received from dart."
            ),
        )

        # Log creation success
        loggerv1.logm(f"InterstitialAd created successfully")
        loggerv1.logm(f"Instance ID: {getattr(iad, '_i', 'Unknown')}")
        loggerv1.logm(f"Instance class: {getattr(iad, '_c', 'Unknown')}")

        # Try to read logs immediately
        try:
            # logs = iad.read_current_log_file(max_lines=20)
            loggerv1.logm(f"Initial logs:\n{logs}")
        except Exception as e:
            loggerv1.logm(f"Could not read logs: {e}")

    except Exception as ex:
        loggerv1.logm(f"Error creating InterstitialAd: {ex}")
        import traceback

        traceback_str = traceback.format_exc()
        loggerv1.logm(f"Traceback: {traceback_str}")
        # Also print to console
        loggerv1.logm(f"ERROR creating InterstitialAd: {ex}")
        traceback.print_exc()

    # Add to page (invisible)
    def append_overlay(e, control):
        try:
            loggerv1.logm(f"Attempting to add {type(control).__name__} to overlay")
            loggerv1.logm(f"Control type: {getattr(control, '_type', 'Unknown')}")
            loggerv1.logm(f"Control ID: {getattr(control, '_i', 'Unknown')}")

            # Check if it's a valid Flet control
            if not isinstance(control, ft.Control):
                loggerv1.logm(f"ERROR: Not a ft.Control instance")
                return

            e.page.overlay.append(control)
            loggerv1.logm(f"Successfully added to overlay")

            # Verify it was added
            loggerv1.logm(f"Overlay now has {len(e.page.overlay)} controls")

            page.update()

        except Exception as ex:
            loggerv1.logm(f"ERROR adding to overlay: {ex}")
            import traceback

            traceback_str = traceback.format_exc()
            loggerv1.logm(f"Traceback: {traceback_str}")
            # Also print to console
            loggerv1.logm(f"ERROR adding to overlay: {ex}")
            traceback.print_exc()

    def clear_overlay():
        page.overlay.clear()
        page.update()

    def show_interstitial_ad():
        # checklist
        loggerv1.logm(
            f"Is it a Control? {isinstance(fta.InterstitialAd, type) and issubclass(fta.InterstitialAd, ft.Control)}"
        )
        # Add this right after creating the instance
        loggerv1.logm(f"iad._type: {getattr(iad, '_type', 'NOT SET')}")
        loggerv1.logm(f"iad.__class__.__name__: {iad.__class__.__name__}")
        loggerv1.logm(f"iad.__class__.__module__: {iad.__class__.__module__}")
        # Add this debug code in your main() function before creating the instance:
        loggerv1.logm(f"ft.Service type: {type(ft.Service)}")
        loggerv1.logm(f"Is ft.Service a class? {isinstance(ft.Service, type)}")
        loggerv1.logm(
            f"Is ft.Service a subclass of ft.Control? {issubclass(ft.Service, ft.Control)}"
        )
        # Also check what fta.InterstitialAd really is:
        loggerv1.logm(f"fta.InterstitialAd: {fta.InterstitialAd}")
        loggerv1.logm(f"fta.InterstitialAd.__bases__: {fta.InterstitialAd.__bases__}")
        loggerv1.logm(f"fta.InterstitialAd.__mro__: {fta.InterstitialAd.__mro__}")

        iad.show()
        # loggerv1.logm(iad.read_current_log_file())

    Header_txt = ft.Text("Flet Ads Extension.", size=30, data=0)
    score_text = ft.Text("Score: 0", size=30, data=0)
    load_rewardedad_btn = ft.Button(
        "Load RewardAd",
        on_click=lambda e: append_overlay(e, rewarded_ad),
    )
    show_rewardedad_btn = ft.Button(
        "Show Reward...", on_click=lambda _: rewarded_ad.show()
    )
    load_interstitial_btn = ft.Button(
        "Load Interstitial Ad",
        on_click=lambda e: append_overlay(e, iad),
    )
    show_interstitial_btn = ft.Button(
        "Show Interstitial...", on_click=show_interstitial_ad
    )
    clear_overlay_btn = ft.Button(
        "Clear Overlay...", on_click=lambda _: clear_overlay()
    )

    def get_new_banner_ad() -> ft.Container:
        return ft.Container(
            width=320,
            height=50,
            bgcolor=ft.Colors.TRANSPARENT,
            content=fta.BannerAd(
                unit_id="ca-app-pub-3940256099942544/6300978111",
                on_click=lambda e: print("BannerAd clicked"),
                on_load=lambda e: print("BannerAd loaded"),
                on_error=lambda e: print("BannerAd error", e.data),
                on_open=lambda e: print("BannerAd opened"),
                on_close=lambda e: print("BannerAd closed"),
                on_impression=lambda e: print("BannerAd impression"),
                on_will_dismiss=lambda e: print("BannerAd will dismiss"),
            ),
        )

    # loggerv1.logm(f"Creating ump instance.")
    # print(f"Creating ump instance.")
    # Production: Leave params empty or use minimal config
    # Only use test_device_ids during development!
    try:
        state = {"privacy_required": False}

        def check_consent_on_startup():
            print("Initializing Startup UMP check...")

            # Create a TEMPORARY instance just for startup
            startup_ump = fta.UserMessagingPlatform(
                debug_geography=fta.DebugGeography.DISABLED,
                on_consent_status_changed=on_startup_consent,
                on_privacy_options_required=on_startup_privacy_check,
                on_error=lambda e: print(f"Startup Error: {e.data}"),
            )

            # Add to overlay temporarily to receive events
            page.overlay.append(startup_ump)
            page.update()

        def on_startup_privacy_check(e):
            data = json.loads(e.data)
            state["privacy_required"] = data.get("is_privacy_options_required", False)
            print(f"Privacy Required: {state['privacy_required']}")

        def on_startup_consent(e):
            data = json.loads(e.data)
            can_request_ads = data.get("can_request_ads", False)
            print(f"can_request_ads: {can_request_ads}")

            # CRITICAL: We are done with startup. REMOVE the UMP control.
            # This keeps your overlay clean.
            page.overlay.clear()

            # Route to Home
            load_home_page(can_request_ads)

        def open_privacy_settings(e):
            print("User clicked Privacy Settings. Creating new UMP instance...")

            # Create a NEW temporary instance just for this action
            settings_ump = fta.UserMessagingPlatform(
                # We don't need start-up checks here, just the method channel
                on_error=lambda e: print(f"Settings Error: {e.data}")
            )

            # Add to overlay so it attaches to Flutter
            page.overlay.append(settings_ump)
            page.update()

            # Call the method
            settings_ump.show_privacy_options_form()

            # Optional: You could remove this instance after a timeout,
            # or listen for a 'form_closed' event to clean it up.
            # For now, keeping one 'settings' instance in overlay is low cost.

        def load_home_page(ads_enabled):
            page.clean()  # Clears the Splash Screen

            status_msg = "Ads Enabled" if ads_enabled else "Ads Disabled"
            status_color = ft.Colors.GREEN if ads_enabled else ft.Colors.RED

            page.add(
                ft.Column(
                    [
                        ft.Text("Home Page", size=30),
                        ft.Text(status_msg, color=status_color, size=20),
                        ft.Container(height=20),
                        # The Button Logic
                        ft.ElevatedButton(
                            "Privacy Settings",
                            icon=ft.Icons.SECURITY,
                            # Use the PYTHON STATE we saved earlier
                            visible=state["privacy_required"],
                            on_click=open_privacy_settings,
                        ),
                    ]
                )
            )

    except Exception as ex:
        loggerv1.logm(f"Creating ump instance failed. {ex}")
        print(f"Creating ump instance failed. {ex}")

    # Start the App with the Splash Loader
    page.add(ft.Text("Loading App...", size=20))
    page.update()
    check_consent_on_startup()

    # page.add(
    #     ft.Container(
    #         alignment=ft.Alignment.TOP_RIGHT,
    #         border=ft.Border.all(1, ft.Colors.RED_100),
    #         padding=5,
    #         height=600,
    #         content=ft.Container(
    #             expand=True,
    #             content=ft.Column(
    #                 expand=True,
    #                 controls=[
    #                     ft.Column(
    #                         alignment=ft.MainAxisAlignment.END,
    #                         horizontal_alignment=ft.CrossAxisAlignment.END,
    #                         expand=True,
    #                         scroll=ft.ScrollMode.ALWAYS,
    #                         controls=[
    #                             score_text,
    #                             load_rewardedad_btn,
    #                             show_rewardedad_btn,
    #                             load_interstitial_btn,
    #                             show_interstitial_btn,
    #                             log_container,
    #                             ft.OutlinedButton(
    #                                 content="Show BannerAd",
    #                                 on_click=lambda e: page.add(get_new_banner_ad()),
    #                             ),
    #                         ],
    #                     )
    #                 ],
    #             ),
    #         ),
    #     ),
    # )


ft.run(main)
