import flet as ft
from flet_ads import RewardedAd, RewardEvent


def main(page: ft.Page):
    # 1. Callback when user earns reward
    def handle_reward(e: RewardEvent):
        print(f"User earned {e.amount} {e.type}!")
        score_text.value = f"Score: {int(score_text.data + e.amount)}"
        score_text.data += e.amount

        # Disable button until next ad loads
        show_btn.disabled = True
        show_btn.text = "Loading next reward..."
        page.update()

        # Load a new ad
        rewarded_ad.page.add(
            RewardedAd(
                unit_id="ca-app-pub-3940256099942544/5224354917",
                on_load=handle_load,
                on_user_earned_reward=handle_reward,
            )
        )

    # 2. Callback when ad is ready
    def handle_load(e):
        show_btn.disabled = False
        show_btn.text = "Watch Ad for 10 Coins"
        page.update()

    # 3. Define the Control
    rewarded_ad = RewardedAd(
        unit_id="ca-app-pub-3940256099942544/5224354917",  # Android Test ID
        on_load=handle_load,
        on_user_earned_reward=handle_reward,
        on_error=lambda e: print(f"Ad Error: {e.data}"),
    )

    # Add to page (invisible)
    page.overlay.append(rewarded_ad)

    score_text = ft.Text("Score: 0", size=30, data=0)
    show_btn = ft.ElevatedButton(
        "Loading Reward...", on_click=lambda _: rewarded_ad.show(), disabled=True
    )

    page.add(ft.Column([score_text, show_btn], alignment=ft.MainAxisAlignment.CENTER))


ft.run(main)
