import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../utils/ads.dart';

// 1. Flet Integration (StatefulWidget & FletStoreMixin)
// The class BannerAdControl extends StatefulWidget. This is necessary because ads have a "lifecycle"—they load, they fail, 
//     or they get clicked—and the UI needs to update when those things happen.
//     widget.control: This holds the data passed from your Flet code (like the unit_id).
//     widget.control.triggerEvent: This is how the Flutter side tells the Python/Flet side that something happened (e.g., on_click).
class BannerAdControl extends StatefulWidget {
  final Control control;

  const BannerAdControl({super.key, required this.control});

  @override
  State<BannerAdControl> createState() => _BannerAdControlState();
}

class _BannerAdControlState extends State<BannerAdControl> with FletStoreMixin {
  bool _isLoaded = false;

  // NEW METHOD: Converts a string from Flet (e.g., "largeBanner") to a Google AdSize
  AdSize _getAdSize(String? sizeName) {
    switch (sizeName) {
      case "largeBanner":
        return AdSize.largeBanner;
      case "mediumRectangle":
        return AdSize.mediumRectangle;
      case "fullBanner":
        return AdSize.fullBanner;
      case "leaderboard":
        return AdSize.leaderboard;
      default:
        return AdSize.banner; // Default standard banner
    }
  }

  @override
  Widget build(BuildContext context) {
    debugPrint(
        "BannerAd build (*********): ${widget.control.id} (${widget.control.hashCode})");
    widget.control.triggerEvent("log", "BannerAd build: ${widget.control.id}");

    final testAdUnitId = isIOSMobile()
        ? 'ca-app-pub-3940256099942544/4411468910'
        : 'ca-app-pub-3940256099942544/1033173712';

    // Use updateProperties to sync the ID back to the Flet state
    widget.control.updateProperties(
      {"effective_unit_id": testAdUnitId},
      dart: true,    // Update the local Dart state
      python: true,  // Send the update across the bridge to Python
      notify: false, // Don't trigger a UI rebuild for this background change
    );

    BannerAd bannerAd = BannerAd(
      adUnitId: widget.control.getString("unit_id", testAdUnitId)!,
      request:
          parseAdRequest(widget.control.get("request"), const AdRequest())!, // Using the parseAdRequest Helper
      size: AdSize.banner,
      listener: BannerAdListener(
        // Called when an ad is successfully received.
        onAdLoaded: (ad) {
          widget.control.triggerEvent("load");
          setState(() {
            _isLoaded = true;
          });
        },
        // Called when an ad request failed.
        onAdFailedToLoad: (ad, error) {
          widget.control.triggerEvent("error", error.toString());
          // Dispose the ad to free resources.
          ad.dispose();
          setState(() {
            _isLoaded = false;
          });
        },
        // Called when an ad opens an overlay that covers the screen.
        onAdOpened: (Ad ad) {
          widget.control.triggerEvent("open");
        },
        // Called when an ad removes an overlay that covers the screen.
        onAdClosed: (Ad ad) {
          widget.control.triggerEvent("close");
        },
        onAdClicked: (Ad ad) {
          widget.control.triggerEvent("click");
        },
        onAdWillDismissScreen: (Ad ad) {
          widget.control.triggerEvent("will_dismiss");
        },
        onPaidEvent: (ad, double valueMicros, PrecisionType precision,
            String currencyCode) {
          widget.control.triggerEvent("paid", {
            "value": valueMicros,
            "precision": precision.name,
            "currency_code": currencyCode
          });
        },
        // Called when an impression occurs on the ad.
        onAdImpression: (Ad ad) {
          widget.control.triggerEvent("impression");
        },
      ),
    );

    if (!_isLoaded) {
      bannerAd.load();
    }

    return ConstrainedControl(
        control: widget.control, child: AdWidget(ad: bannerAd));
  }
}
