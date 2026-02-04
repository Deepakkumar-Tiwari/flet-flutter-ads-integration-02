import flet as ft
from flet_ads_ext import RewardedAd, RewardEvent, BannerAd, InterstitialAd


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
        alignment=ft.alignment.top_right,
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

    # Add to page (invisible)
    page.overlay.append(rewarded_ad)

    score_text = ft.Text("Score: 0", size=30, data=0)
    show_rewardedad_btn = ft.ElevatedButton(
        "Loading Reward...", on_click=lambda _: rewarded_ad.show(), disabled=True
    )

    page.add(
        ft.Column(
            controls=[score_text, show_rewardedad_btn],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )


ft.run(main)
