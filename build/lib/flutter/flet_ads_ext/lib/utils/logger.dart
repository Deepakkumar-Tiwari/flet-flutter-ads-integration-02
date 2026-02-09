import 'dart:io';
import 'package:path_provider/path_provider.dart';

class LocalLogger {
  // Private helper to avoid repeating directory/file logic
  static Future<File> _getFile() async {
    final directory = await getApplicationDocumentsDirectory();
    return File('${directory.path}/ad_logs.txt');
  }

  // Write logs
  static Future<void> log(String message) async {
    try {
      final file = await _getFile();
      final timestamp = DateTime.now().toString();
      final logEntry = "[$timestamp] $message\n";
      
      await file.writeAsString(logEntry, mode: FileMode.append);
      print("FILE LOG: $logEntry");
    } catch (e) {
      print("Error writing to log file: $e");
    }
  }

  // Read logs (The logic you wanted to move)
  static Future<String> readLogs() async {
    try {
      final file = await _getFile();
      if (await file.exists()) {
        return await file.readAsString();
      }
      return "No logs found yet.";
    } catch (e) {
      return "Error reading logs: $e";
    }
  }
}

// Usage:
// void _loadAd() {
//     _bannerAd = BannerAd(
//       adUnitId: adUnitId,
//       request: const AdRequest(),
//       size: AdSize.banner,
//       listener: BannerAdListener(
//         onAdLoaded: (ad) {
//           LocalLogger.log("SUCCESS: Ad loaded successfully."); // Log to file
//           setState(() => _isLoaded = true);
//         },
//         onAdFailedToLoad: (ad, err) {
//           LocalLogger.log("ERROR: Ad failed to load. Reason: ${err.message}"); // Log to file
//           ad.dispose();
//         },
//         onAdOpened: (ad) => LocalLogger.log("EVENT: User clicked the ad."),
//       ),
//     )..load();
//   }

// void _showLogs() async {
//   // Call the static method from our helper class
//   String content = await LocalLogger.readLogs();
  
//   // Print to console
//   print(content);

//   // Show a popup (SnackBar) with the last bit of the log
//   if (!mounted) return;
//   ScaffoldMessenger.of(context).showSnackBar(
//     SnackBar(
//       content: Text(
//         content.length > 100 ? content.substring(content.length - 100) : content,
//         style: const TextStyle(fontSize: 12),
//       ),
//       duration: const Duration(seconds: 3),
//     ),
//   );
// }