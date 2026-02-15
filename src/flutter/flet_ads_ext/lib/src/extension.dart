import 'package:flet/flet.dart';
import 'package:flutter/cupertino.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'banner.dart';
import 'interstitial.dart';
import 'rewarded.dart';
import 'ump.dart';
// import 'umpv2.dart';

import '../utils/logger.dart'; 

class Extension extends FletExtension {
  @override
  void ensureInitialized() {
    if (isMobilePlatform()) {
      MobileAds.instance.initialize();
    }
  }

  @override
  FletService? createService(Control control) {
    final _type=control.type;
    switch (control.type) {
      case "InterstitialAd":
        LocalLogger.log("InterstitialAd bridge successfull.");
        return InterstitialAdService(control: control);
      case "RewardedAd":
        LocalLogger.log("RewardedAd bridge successfull.");
        return RewardedAdService(control: control);
      default:
        LocalLogger.log("Unknown Type: $_type");
        return null;
    }
  }

  @override
  Widget? createWidget(Key? key, Control control) {
    switch (control.type) {
      case "BannerAd":
        LocalLogger.log("BannerAd bridge successfull.");
        return BannerAdControl(control: control);
      case "UserMessagingPlatform":
        LocalLogger.log("UserMessagingPlatform bridge successfull.");
        return UserMessagingPlatformControl(control: control);
      // case "UserMessagingPlatformv2":
      //   LocalLogger.log("UserMessagingPlatformv2 bridge successfull.");
      //   return UserMessagingPlatformv2Control(control: control);

      default:
        return null;
    }
  }
}
