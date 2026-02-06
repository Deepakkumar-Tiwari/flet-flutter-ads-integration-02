import flet as ft
from flet_ads_ext import RewardedAd, RewardEvent, BannerAd, InterstitialAd
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
        border=ft.border.all(1, ft.Colors.GREY_400),
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
    def handle_reward(e: RewardEvent):
        print(f"User earned {e.amount} {e.type}!")
        score_text.value = f"Score: {int(score_text.data + e.amount)}"
        score_text.data += e.amount

        # Disable button until next ad loads
        show_rewardedad_btn.disabled = True
        show_rewardedad_btn.text = "Loading next reward..."
        page.update()

        # Load a new ad
        rewarded_ad.page.add(
            RewardedAd(
                unit_id="ca-app-pub-3940256099942544/5224354917",
                on_load=handle_rewardedad_load,
                on_user_earned_reward=handle_reward,
            )
        )

    # 2. Callback when ad is ready
    def handle_rewardedad_load(e):
        show_rewardedad_btn.disabled = False
        show_rewardedad_btn.text = "Watch Ad for 10 Coins"
        page.update()

    # 3. Define the Control
    rewarded_ad = RewardedAd(
        unit_id="ca-app-pub-3940256099942544/5224354917",  # Android Test ID
        on_load=handle_rewardedad_load,
        on_user_earned_reward=handle_reward,
        on_error=lambda e: print(f"Ad Error: {e.data}"),
    )
    loggerv1.logm(f"rewarded ad type: {type(rewarded_ad)}")
    loggerv1.logm(f"rewarded ad unit_id: {rewarded_ad.unit_id}")

    # Add to page (invisible)
    def append_overlay(control):
        page.overlay.append(control)
        loggerv1.logm(f"rewarded ad initilized.")

    Header_txt = ft.Text("Flet Ads Extension.", size=30, data=0)
    score_text = ft.Text("Score: 0", size=30, data=0)
    load_rewardedad_btn = ft.ElevatedButton(
        "Load RewardAd",
        on_click=lambda _: append_overlay(rewarded_ad),
    )
    show_rewardedad_btn = ft.ElevatedButton(
        "Show Reward...", on_click=lambda _: rewarded_ad.show(), disabled=True
    )
    show_bannerad_btn = ft.ElevatedButton(
        "Show Banner Ad",
        on_click=lambda _: get_new_banner_ad,
    )

    def handle_incoming_banner_ad_custom_logs(e):
        # 'e.data' will contain the string sent from Dart's debugPrint
        print(f"📡 Flutter Log: {e.data}")
        loggerv1.logm(f"BannerAd Flutter Log: {e.data}")

    def get_new_banner_ad() -> ft.Container:
        return ft.Container(
            width=320,
            height=90,
            bgcolor=ft.Colors.TRANSPARENT,
            content=BannerAd(
                unit_id=ids.get(page.platform, {}).get("banner"),
                on_click=lambda e: loggerv1.logm("BannerAd clicked"),
                on_load=lambda e: loggerv1.logm("BannerAd loaded"),
                on_error=lambda e: loggerv1.logm(f"BannerAd error: {e.data}"),
                on_open=lambda e: loggerv1.logm("BannerAd opened"),
                on_close=lambda e: loggerv1.logm("BannerAd closed"),
                on_impression=lambda e: loggerv1.logm("BannerAd impression"),
                on_will_dismiss=lambda e: loggerv1.logm("BannerAd will dismiss"),
                on_log=handle_incoming_banner_ad_custom_logs,
            ),
        )

    page.add(
        ft.Container(
            alignment=ft.Alignment.TOP_RIGHT,
            border=ft.border.all(1, ft.Colors.GREY_400),
            content=ft.Column(
                controls=[
                    score_text,
                    load_rewardedad_btn,
                    show_rewardedad_btn,
                    log_container,
                    show_bannerad_btn,
                    get_new_banner_ad,
                ],
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.END,
            ),
        )
    )


ft.run(main)
