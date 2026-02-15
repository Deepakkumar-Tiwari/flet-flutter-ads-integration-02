import 'dart:convert';
import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';
import '../utils/logger.dart';
import '../utils/consent_manager.dart';

class UserMessagingPlatformControl extends StatefulWidget {
  final Control control;

  const UserMessagingPlatformControl({super.key, required this.control});

  @override
  State<UserMessagingPlatformControl> createState() => _UserMessagingPlatformControlState();
}

class _UserMessagingPlatformControlState extends State<UserMessagingPlatformControl> with FletStoreMixin {


  // STATIC: Persists across widget rebuilds to track session state
  static bool _sessionInitialized = false;

  // STATE: Tracks the last values sent to Python to prevent duplicates
  bool? _lastReportedConsentStatus;
  bool? _lastReportedPrivacyRequired;
  double _lastShowTrigger = 0;

  @override
  void initState() {
    super.initState();
    //Register the Method Channel Listener
    widget.control.addInvokeMethodListener(_invokeMethod);

    _initializeUMP();

  }

  // Handle methods called from Python  
  Future<dynamic> _invokeMethod(String methodName, dynamic args) async {
    debugPrint("UserMessagingPlatform.$methodName($args)");
    switch (methodName) {
      case "show_privacy_options_form":
        debugPrint("UMP: Method call received -> show_privacy_options_form");
        _showPrivacyOptionsForm();
        break;
      case "reset":
         // Example: You could expose a reset method too
         // You can remove the 'shouldReset' property check from the _initializeUMP if you prefer
         // to handle resets purely via the "reset" method.
         ConsentInformation.instance.reset();
         _sessionInitialized = false;
         _initializeUMP();
         break;
      default:
        throw Exception("Unknown InterstitialAd method: $methodName");
    }
    return null;
  }

  void _initializeUMP() {

    LocalLogger.log("UMP Initialization.");

    // Check if we need to force a reset (e.g., for testing)
    bool shouldReset = widget.control.getBool("resetConsentOnLaunch") ?? false;
    
    if (shouldReset) {
      ConsentInformation.instance.reset();
      _sessionInitialized = false; // Force re-initialization
    }

    // SESSION CHECK: If already initialized, skip Consent Info Update 
    if (_sessionInitialized && !shouldReset) {
      debugPrint("UMP: Session already initialized. Skipping update request.");
      _checkPrivacyOptionsRequirement();
      _checkAdStatus();
      return;
    }

    // --- Prepare Debug Settings ---
    // Only apply debug settings if strictly necessary
    ConsentDebugSettings? debugSettings;
    
    // Check if testDeviceIds string exists and is not empty JSON array
    String? testIdsString = widget.control.getString("testDeviceIds");
    List<dynamic>? testIds = testIdsString != null ? jsonDecode(testIdsString) : null;
    int geoValue = widget.control.getInt("debugGeography") ?? 0;

    if ((testIds != null && testIds.isNotEmpty) || geoValue != 0) {
       DebugGeography debugGeography = DebugGeography.debugGeographyDisabled; // google_mobile_ads.dartDebugGeography enum
       if (geoValue == 1) debugGeography = DebugGeography.debugGeographyEea;
       if (geoValue == 2) debugGeography = DebugGeography.debugGeographyNotEea;
       if (geoValue == 3) debugGeography = DebugGeography.debugGeographyRegulatedUsState;
       if (geoValue == 4) debugGeography = DebugGeography.debugGeographyOther;

       debugSettings = ConsentDebugSettings(
         debugGeography: debugGeography,
         testIdentifiers: testIds?.cast<String>(),
       );
    }

    // Create Params (pass null debugSettings or remove consentDebugSettings for production)
    final params = ConsentRequestParameters(consentDebugSettings: debugSettings,);

    // 1. Request Consent Info Update at every app launch
    debugPrint("UMP: Requesting Consent Info Update...");
    
    // Only happens once per session (or after reset)
    ConsentInformation.instance.requestConsentInfoUpdate(
      params,
      () async { // async: Called when consent information is successfully updated.

        _sessionInitialized = true; // Mark session as initialized
        _loadAndShowConsentForm(); // Called on Success only: Checks if form is required and loads form
      },
      (FormError error) { // Called when there's an error updating consent information.

        widget.control.triggerEvent("error", jsonEncode({"error": "Consent Info Update Error: ${error.message}"}));
        // Even if update fails, check if we can request ads based on previous state
        _checkAdStatus();
      },
    );
  }

  void _loadAndShowConsentForm() {
    // At app launch, you checked Consent status to evaluate if consent needs to be updated.
    // After you have received the most up-to-date consent status, call loadAndShowConsentFormIfRequired() to 
    // load forms required to collect user consent. After loading, the forms present immediately.

    ConsentForm.loadAndShowConsentFormIfRequired((FormError? error) {
      if (error != null) {
        widget.control.triggerEvent("error", jsonEncode({"error": "Failed to retrieve Google UMP Consent Form. Error: ${error.message}"}));
      }

      // Form dismissed or not required: Check Privacy Options & Ad Status
      _checkPrivacyOptionsRequirement(); 
      _checkAdStatus();
    });
  }


  /// Helper variable to determine if the privacy options entry point is required for app.
  // if yes, presents the privacy options form using a visible and interactable UI element
  // if not, configure your UI element to be not visible and interactable.
  Future<void> _checkPrivacyOptionsRequirement() async {
    var status =
        await ConsentInformation.instance.getPrivacyOptionsRequirementStatus();
    
    bool isRequired = status == PrivacyOptionsRequirementStatus.required; // notRequired, required, unknown

    // Send event back to Python to show/hide "Privacy Settings" button. 
    // OPTIMIZATION: Only trigger event if status changed
    if (_lastReportedPrivacyRequired != isRequired) {
      _lastReportedPrivacyRequired = isRequired;
      widget.control.triggerEvent(
          "privacy_options_required",
          jsonEncode({
            "is_privacy_options_required": isRequired,
          }));
    }
  }
  
  // Before requesting ads, check if you've obtained consent from the user.
  // Perform this checks at:
  //  1. After the UMP SDK gathers consent in the current session.
  //  2. Immediately after calling requestConsentInfoUpdate() on both success, error output.
  Future<void> _checkAdStatus() async {
    // Check if we can legally request ads
    bool canRequest = await ConsentInformation.instance.canRequestAds();
    
    // OPTIMIZATION: Only trigger event if status changed
    // This prevents Python from receiving multiple "True" events and loading ads twice
    if (_lastReportedConsentStatus != canRequest) {
      _lastReportedConsentStatus = canRequest;
      widget.control.triggerEvent(
          "consent_status_changed",
          jsonEncode({
            "can_request_ads": canRequest,
          }));
    }
  }

  /// present the privacy options form
  void _showPrivacyOptionsForm() {
    ConsentForm.showPrivacyOptionsForm((FormError? error) {
      if (error != null) {
        widget.control.triggerEvent("error", jsonEncode({"error": "Failed to Show Privacy Options Form. Error: ${error.message}"}));
      } else {
        // User updates the privacy options. They might revoke previous consents, so re-check ads status.
        _checkAdStatus();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    debugPrint("UMP Build");
    LocalLogger.log("UMP Build.");
    
    // This control is strictly logic, so it returns an empty sized box.
    // return const SizedBox.shrink();
    Widget myControl = SizedBox.shrink();
    return ConstrainedControl(
        control: widget.control, child: myControl);

  }



}