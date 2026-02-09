import 'package:google_mobile_ads/google_mobile_ads.dart';

AdRequest? parseAdRequest(dynamic value, [AdRequest? defaultValue]) {
  // Safety guard. If the input value is empty (null), the function immediately exits and returns whatever defaultValue was provided.
  if (value == null) return defaultValue;

  return AdRequest(
    keywords: value["keywords"],
    contentUrl: value["content_url"],
    nonPersonalizedAds: value["non_personalized_ads"],
    neighboringContentUrls: value["neighboring_content_urls"],
    httpTimeoutMillis: value["http_timeout"],
    extras: value["extras"],
  );
}
