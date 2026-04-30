import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../controllers/splash_controller.dart';

class SplashView extends GetView<SplashController> {
  const SplashView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 216, 248, 207), // plain background color as requested
      body: SizedBox.expand(
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Main Branding Container
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Logo Icon
                const Icon(
                  Icons.eco,
                  size: 64,
                  color: Color(0xFF000000), // primary
                ),
                const SizedBox(height: 16),
                // Brand Name
                const Text(
                  'CareTrack',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 32,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.64, // -0.02em
                    color: Color(0xFF000000), // primary
                  ),
                ),
                const SizedBox(height: 8),
                // Tagline
                Text(
                  'Calmly tracking your wellness journey',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.14, // 0.01em
                    color: const Color(
                      0xFF4C4546,
                    ).withValues(alpha: 0.6), // on-surface-variant/60
                  ),
                ),
              ],
            ),

            // Loading / Progress Indicator
            Positioned(
              bottom: 96,
              child: SizedBox(
                width: 48,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: const LinearProgressIndicator(
                    minHeight: 2,
                    backgroundColor: Color(
                      0xFFE2E2E2,
                    ), // surface-container-highest
                    valueColor: AlwaysStoppedAnimation<Color>(
                      Color(0xFF000000),
                    ), // primary
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
