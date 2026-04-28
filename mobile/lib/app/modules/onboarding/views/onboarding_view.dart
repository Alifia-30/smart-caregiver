import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../../../routes/app_pages.dart';

class OnboardingView extends StatefulWidget {
  const OnboardingView({super.key});

  @override
  State<OnboardingView> createState() => _OnboardingViewState();
}

class _OnboardingViewState extends State<OnboardingView>
    with TickerProviderStateMixin {
  late final AnimationController _scaleCtrl;
  late final AnimationController _fadeCtrl;
  late final Animation<double> _scaleAnim;
  late final Animation<double> _fadeAnim;

  String get patientName =>
      Get.arguments is String ? Get.arguments as String : 'Opa Hasan';

  @override
  void initState() {
    super.initState();
    _scaleCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _fadeCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    _scaleAnim = CurvedAnimation(parent: _scaleCtrl, curve: Curves.elasticOut);
    _fadeAnim = CurvedAnimation(parent: _fadeCtrl, curve: Curves.easeIn);

    Future.delayed(const Duration(milliseconds: 200), () {
      _scaleCtrl.forward();
    });
    Future.delayed(const Duration(milliseconds: 400), () {
      _fadeCtrl.forward();
    });
  }

  @override
  void dispose() {
    _scaleCtrl.dispose();
    _fadeCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const Spacer(flex: 2),
              // Animated check icon
              ScaleTransition(
                scale: _scaleAnim,
                child: Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    color: AppColors.accent.withValues(alpha: 0.15),
                    shape: BoxShape.circle,
                  ),
                  child: const Center(
                    child: Icon(Icons.check_circle_rounded,
                        size: 56, color: AppColors.accent),
                  ),
                ),
              ),
              const SizedBox(height: 32),
              FadeTransition(
                opacity: _fadeAnim,
                child: Column(
                  children: [
                    Text(
                      patientName,
                      style: AppTextStyles.display,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Profile berhasil dibuat!\nMau langsung catat kondisi kesehatan $patientName sekarang?',
                      style: AppTextStyles.bodyLg.copyWith(
                          color: AppColors.onSurfaceVariant),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              const Spacer(flex: 2),
              // Confetti-like decorative dots
              FadeTransition(
                opacity: _fadeAnim,
                child: _buildDecorative(),
              ),
              const Spacer(),
              // Actions
              FadeTransition(
                opacity: _fadeAnim,
                child: Column(
                  children: [
                    ElevatedButton(
                      onPressed: () => Get.offAllNamed(
                        Routes.INPUT_HEALTH,
                        arguments: {
                          'elderlyId': 'new-patient-id', // Placeholder for actual ID
                          'elderlyName': patientName,
                        },
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.accent,
                        foregroundColor: AppColors.onBackground,
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.edit_note_rounded, size: 20),
                          SizedBox(width: 8),
                          Text('Record Health Now'),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    OutlinedButton(
                      onPressed: () => Get.offAllNamed(Routes.home),
                      child: const Text('Go to Patient List'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDecorative() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(5, (i) {
        final sizes = [8.0, 12.0, 16.0, 12.0, 8.0];
        final opacities = [0.3, 0.5, 1.0, 0.5, 0.3];
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: Container(
            width: sizes[i],
            height: sizes[i],
            decoration: BoxDecoration(
              color: AppColors.accent.withValues(alpha: opacities[i]),
              shape: BoxShape.circle,
            ),
          ),
        );
      }),
    );
  }
}
