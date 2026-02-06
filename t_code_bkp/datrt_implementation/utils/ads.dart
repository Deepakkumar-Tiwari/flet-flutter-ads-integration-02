import 'package:google_mobile_ads/google_mobile_ads.dart';

// FUNCTION parseAdRequest
// Function SIGNATURE:
// AdRequest?:                Question mark means the function can return either a valid AdRequest object or null.
// dynamic value:             Input data (usually a Dart Map {Python Dict} from an API or a local database).
// [AdRequest? defaultValue]: The square brackets indicate an optional positional parameter. If you don't provide a second argument, it defaults to null.

AdRequest? parseAdRequest(dynamic value, [AdRequest? defaultValue]) {

  if (value == null) return defaultValue; // Safety guard. If the input value is empty (null), the function immediately exits and returns whatever defaultValue was provided.

  // maps keys from the value map to the specific parameters required by the AdRequest constructor
  return AdRequest(
    keywords: value["keywords"],
    contentUrl: value["content_url"],
    nonPersonalizedAds: value["non_personalized_ads"],
    neighboringContentUrls: value["neighboring_content_urls"],
    httpTimeoutMillis: value["http_timeout"],
    extras: value["extras"],
  );
}
