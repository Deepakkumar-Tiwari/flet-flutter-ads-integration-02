# debug_control.py
import flet as ft
import flet_ads_ext as fta


def test_control_registration():
    print("=== Testing Control Registration ===")

    # Test 1: Check if control is registered
    try:
        # Try to create instance
        iad = fta.InterstitialAd(
            unit_id="test-unit-id",
            on_load=lambda e: print("on_load"),
            on_error=lambda e: print(f"on_error: {e.data}"),
        )
        print(f"✓ Created InterstitialAd instance")

        # Check instance attributes
        print(f"  Instance ID: {getattr(iad, '_i', 'Unknown')}")
        print(f"  Instance class: {getattr(iad, '_c', 'Unknown')}")
        print(f"  Instance type: {getattr(iad, '_type', 'Unknown')}")
        print(f"  Unit ID: {getattr(iad, 'unit_id', 'Unknown')}")

    except Exception as e:
        print(f"✗ Error creating instance: {e}")
        import traceback

        traceback.print_exc()

    # Test 2: Check control registry
    print("\n=== Checking Control Registry ===")
    try:
        # Try to access Flet's control registry (if available)
        if hasattr(ft, "ControlRegistry"):
            print("✓ ControlRegistry found")
            # Try to get registered controls
            if hasattr(ft.ControlRegistry, "get_controls"):
                controls = ft.ControlRegistry.get_controls()
                print(f"Registered controls: {list(controls.keys())}")
                if "InterstitialAd" in controls:
                    print("✓ InterstitialAd is registered!")
                else:
                    print("✗ InterstitialAd is NOT registered")
        else:
            print("✗ ControlRegistry not found")

    except Exception as e:
        print(f"✗ Error checking registry: {e}")

    # Test 3: Try to add to a test page
    print("\n=== Testing Page Addition ===")
    try:
        # Create a dummy page
        class DummyPage:
            def __init__(self):
                self.overlay = []
                self.controls = []

            def add(self, control):
                self.controls.append(control)
                print(f"✓ Added control to page: {control}")

            def update(self):
                print("✓ Page updated")

        dummy_page = DummyPage()

        # Try to add to overlay
        iad = fta.InterstitialAd(
            unit_id="test-unit-id",
            on_load=lambda e: print("on_load"),
        )

        dummy_page.overlay.append(iad)
        print("✓ Added to overlay successfully")

    except Exception as e:
        print(f"✗ Error adding to overlay: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_control_registration()
