import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';
import '../utils/consent_manager.dart';

class UserMessagingPlatformv2Control extends StatefulWidget {
  final Control control;

  const UserMessagingPlatformv2Control({super.key, required this.control});

  @override
  State<UserMessagingPlatformv2Control> createState() => _UserMessagingPlatformv2ControlState();
}

class _UserMessagingPlatformv2ControlState extends State<UserMessagingPlatformv2Control> with FletStoreMixin {
  final _consentManager = ConsentManager();
  bool _isUserMessagingPlatformv2InitializeCalled = false;

  @override
  void initState() {
    super.initState();
    _initialize();
  }

  void _initialize() {
    // 1. Gather Consent
    _consentManager.gatherConsent((consentGatheringError) {
      if (consentGatheringError != null) {
        widget.control.triggerEvent("error", 
            "${consentGatheringError.errorCode}: ${consentGatheringError.message}");
      }
      
      // 2. Initialize SDK if consent permits
      _initializeUserMessagingPlatformv2SDK();
    });

    // Attempt to initialize immediately (for returning users)
    _initializeUserMessagingPlatformv2SDK();
  }

  Future<void> _initializeUserMessagingPlatformv2SDK() async {
    if (_isUserMessagingPlatformv2InitializeCalled) {
      return;
    }

    if (await _consentManager.canRequestAds()) {
      _isUserMessagingPlatformv2InitializeCalled = true;
      
      // Initialize the SDK
      await MobileAds.instance.initialize();
      
      // Update Test Device IDs if provided
      var testDeviceIds = widget.control.attrList("testDeviceIds")?.cast<String>();
      if (testDeviceIds != null) {
        RequestConfiguration configuration =
            RequestConfiguration(testDeviceIds: testDeviceIds);
        MobileAds.instance.updateRequestConfiguration(configuration);
      }

      // Notify Python that we are ready
      widget.control.triggerEvent("initialized");
    }
  }

  @override
  Widget build(BuildContext context) {
    debugPrint("UserMessagingPlatformv2 build: ${widget.control.id}");

    // Handle "method calls" from Python via property changes
    widget.control.onRemove.clear(); // Cleanup previous handlers
    
    // Check if Python requested privacy options
    var showPrivacyTimestamp = widget.control.attrString("showPrivacyOptions");
    if (showPrivacyTimestamp != null) {
       // We use a timestamp logic or similar to detect "new" requests, 
       // but for simplicity, we just trigger if the prop exists and isn't handled.
       // In a real app, you might compare against a stored timestamp.
       _consentManager.showPrivacyOptionsForm((formError) {
        if (formError != null) {
          widget.control.triggerEvent("error", formError.message);
        }
      });
    }

    // This is a non-visual control, so we return a 0-sized widget
    // return const SizedBox.shrink();
    return ConstrainedControl(
        control: widget.control, child: SizedBox.shrink());
  }
}