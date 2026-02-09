import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../utils/ads.dart';
import '../utils/logger.dart';

class RewardedAdService extends FletService {
  RewardedAdService({required super.control});

  static RewardedAd? _rewardedAd;

  @override
  void init() {
    super.init();
    debugPrint("RewardedAd(${control.id}).init: ${control.properties}");
    control.addInvokeMethodListener(_invokeMethod);

    // Test ID for Rewarded Ad (Android)
    // Replace with iOS Test ID if needed: 'ca-app-pub-3940256099942544/1712485313'
    final String unitId = control.getString(
        "unit_id",
        isIOSMobile()
            ? 'ca-app-pub-3940256099942544/1712485313'
            : 'ca-app-pub-3940256099942544/5224354917')!;

    RewardedAd.load(
      adUnitId: unitId,
      request: parseAdRequest(control.get("request"), const AdRequest())!,
      rewardedAdLoadCallback: RewardedAdLoadCallback(
        onAdLoaded: (ad) {
          debugPrint('$ad loaded.');
          LocalLogger.log("RewardedAd onAdLoaded event. Creating fullscreen content.");

          // Setup callbacks for when the ad is actually shown
          ad.fullScreenContentCallback = FullScreenContentCallback(
            onAdShowedFullScreenContent: (ad) => control.triggerEvent("open"),
            onAdDismissedFullScreenContent: (ad) {
              control.triggerEvent("close");
              ad.dispose();
            },
            onAdFailedToShowFullScreenContent: (ad, error) {
              control.triggerEvent("error", error.toString());
              ad.dispose();
            },
            onAdImpression: (ad) => control.triggerEvent("impression"),
            onAdClicked: (ad) => control.triggerEvent("click"),
          );

          // Keep a reference to show it later.
          _rewardedAd = ad;
          control.triggerEvent("load");
        },
        onAdFailedToLoad: (LoadAdError error) {
          debugPrint('RewardedAd failed to load: $error');
          control.triggerEvent("error", error.toString());
          _rewardedAd?.dispose();
        },
      ),
    );
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    debugPrint("RewardedAd.$name($args)");
    switch (name) {
      case "show":
        LocalLogger.log("RewardedAd show method triggered at dart side.");
        if (_rewardedAd == null) {
          debugPrint('Warning: Attempted to show rewarded ad before loading.');
          LocalLogger.log('Warning: Attempted to show rewarded ad before loading.');
          return null;
        }
        _rewardedAd?.show(
          onUserEarnedReward: (AdWithoutView ad, RewardItem reward) {
            // Send the reward details back to Python
            control.triggerEvent("user_earned_reward", {
              "type": reward.type,
              "amount": reward.amount
            });
          },
        );
        _rewardedAd = null; // Prevent showing the same ad twice
        return null;
      default:
        throw Exception("Unknown RewardedAd method: $name");
    }
  }

  @override
  void dispose() {
    _rewardedAd?.dispose();
    super.dispose();
  }
}