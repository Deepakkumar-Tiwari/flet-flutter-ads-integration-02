import flet as ft
from ump import UserMessagingPlatform, DebugGeography
import json

# Best Practice: Use a "Splash/Loading" state. Do not initialize your BannerAd control
# until you receive the can_request_ads=True event. If you initialize it too early, you might violate GDPR/CCPA.


def main(page: ft.Page):
    # Production: Leave params empty or use minimal config
    # Only use test_device_ids during development!
    ump = UserMessagingPlatform(
        on_consent_status_changed=lambda e: handle_consent(e),
        on_privacy_options_required=lambda e: handle_privacy(e),
        on_error=lambda e: print(f"UMP Error: {e.data}"),
    )

    # Define your Ad/Main Content (Initially Hidden or Not Added)
    #
    main_content = ft.Column(
        visible=False,
        controls=[
            ft.Text("Welcome to the App!"),
            # BannerAd(unit_id="...") <--- Add this ONLY after consent
        ],
    )

    privacy_button = ft.ElevatedButton(
        "Privacy Settings",
        visible=False,
        on_click=lambda _: ump.show_privacy_options_form(),
    )

    def handle_consent(e):
        data = json.loads(e.data)
        can_request = data.get("can_request_ads", False)

        if can_request:
            # Safe to show ads and main content now
            main_content.visible = True
            # main_content.controls.append(BannerAd(...))
            page.update()
        else:
            # Handle "Consent Denied" or "Freemium" flow
            print("Consent denied or ads not allowed")

    def handle_privacy(e):
        data = json.loads(e.data)
        # Only show the button if UMP says it's required (e.g. GDPR/CCPA regions)
        privacy_button.visible = data.get("is_privacy_options_required", False)
        page.update()

    page.overlay.append(ump)
    page.add(main_content, privacy_button)


ft.run(main)
