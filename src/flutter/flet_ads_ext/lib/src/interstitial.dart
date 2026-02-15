import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../utils/ads.dart';
import '../utils/logger.dart';

class InterstitialAdService extends FletService {

  // FletService Constructor Implementation: FletService({required this.control});
  InterstitialAdService({required super.control});

  static InterstitialAd? _interstitialAd;

  // @override
  // void init() {
  @override
  Widget build(BuildContext context) {
    super.init();
    debugPrint("InterstitialAd(${control.id}).init: ${control.properties}");
    control.addInvokeMethodListener(_invokeMethod);

    final testAdUnitId = isIOSMobile()
        ? 'ca-app-pub-3940256099942544/4411468910'
        : 'ca-app-pub-3940256099942544/1033173712';

    InterstitialAd.load(
      adUnitId: control.getString("unit_id",testAdUnitId)!,
      request: parseAdRequest(control.get("request"), const AdRequest())!,
      adLoadCallback: InterstitialAdLoadCallback(
        onAdLoaded: (ad) {
          LocalLogger.log("InterstitialAd onAdLoaded event from dart. Creating fullscreen content."); 
          
          ad.fullScreenContentCallback = FullScreenContentCallback(
            onAdShowedFullScreenContent: (ad) {
              control.triggerEvent("log", "InterstitialAd onAdShowedFullScreenContent event from dart.");
              control.triggerEvent("open");
            },
            onAdImpression: (ad) => control.triggerEvent("impression"),
            onAdFailedToShowFullScreenContent: (ad, error) {
              LocalLogger.log("InterstitialAd onAdFailedToShow event from dart. ERROR: $error"); 
              control.triggerEvent("error", error.toString());
              ad.dispose(); // free resources
            },
            onAdDismissedFullScreenContent: (ad) {
              // Called when the ad dismissed full screen content.
              LocalLogger.log("InterstitialAd onAddismissed event from dart."); 
              control.triggerEvent("close");
              // Dispose the ad here to free resources.
              ad.dispose();
            },
            onAdClicked: (ad) => control.triggerEvent("click"),
          );

          // Keep a reference to show it later.
          _interstitialAd = ad;
          LocalLogger.log("InterstitialAd onLoad event from dart."); 
          control.triggerEvent("load");
        },
        onAdFailedToLoad: (LoadAdError error) {
          LocalLogger.log("InterstitialAd onError event from dart: $error"); 
          control.triggerEvent("error", error.toString());
          _interstitialAd?.dispose();
        },
      )
    );
    return ConstrainedControl(
        control: control, child: SizedBox.shrink()); 
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    debugPrint("InterstitialAd.$name($args)");
    switch (name) {
      case "show":
        control.triggerEvent("log", "InterstitialAd onAdShow method triggered in dart.");
        _interstitialAd?.show();
        return null;
      default:
        throw Exception("Unknown InterstitialAd method: $name");
    }
  }

  @override
  void dispose() {
    _interstitialAd?.dispose();
    super.dispose();
  }
}
