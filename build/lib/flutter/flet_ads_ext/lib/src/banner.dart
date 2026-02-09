import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../utils/ads.dart';
import '../utils/logger.dart';

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

  @override
  Widget build(BuildContext context) {
    debugPrint(
        "BannerAd build: ${widget.control.id} (${widget.control.hashCode})");
    final testAdUnitId = isIOSMobile()
        ? 'ca-app-pub-3940256099942544/4411468910'
        : 'ca-app-pub-3940256099942544/1033173712';
    BannerAd bannerAd = BannerAd(
      adUnitId: widget.control.getString("unit_id", testAdUnitId)!,
      request:
          parseAdRequest(widget.control.get("request"), const AdRequest())!,
      size: AdSize.banner,
      listener: BannerAdListener(
        // Called when an ad is successfully received.
        onAdLoaded: (ad) {
          LocalLogger.log("BannerAd onAdLoaded event from dart. fetching ad content."); 
          widget.control.triggerEvent("load");
          setState(() {
            _isLoaded = true;
          });
        },
        // Called when an ad request failed.
        onAdFailedToLoad: (ad, error) {
          LocalLogger.log("BannerAd onAdFailedToLoad event from dart. {$error}."); 
          widget.control.triggerEvent("error", error.toString());
          // Dispose the ad to free resources.
          ad.dispose();
          setState(() {
            _isLoaded = false;
          });
        },
        // Called when an ad opens an overlay that covers the screen.
        onAdOpened: (Ad ad) {
          LocalLogger.log("BannerAd onAdOpened event from dart."); 
          widget.control.triggerEvent("open");
        },
        // Called when an ad removes an overlay that covers the screen.
        onAdClosed: (Ad ad) {
          LocalLogger.log("BannerAd onAdClosed event from dart."); 
          widget.control.triggerEvent("close");
        },
        onAdClicked: (Ad ad) {
          LocalLogger.log("BannerAd onAdClicked event from dart."); 
          widget.control.triggerEvent("click");
        },
        onAdWillDismissScreen: (Ad ad) {
          LocalLogger.log("BannerAd onWillDissmissed event from dart."); 
          widget.control.triggerEvent("will_dismiss");
        },
        onPaidEvent: (ad, double valueMicros, PrecisionType precision,
            String currencyCode) {
          LocalLogger.log("BannerAd onPaidEvent event from dart."); 
          widget.control.triggerEvent("paid", {
            "value": valueMicros,
            "precision": precision.name,
            "currency_code": currencyCode
          });
        },
        // Called when an impression occurs on the ad.
        onAdImpression: (Ad ad) {
          LocalLogger.log("BannerAd onimpression event from dart."); 
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
