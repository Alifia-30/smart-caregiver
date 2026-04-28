import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/services/auth_service.dart';
import '../../../routes/app_pages.dart';

class AuthController extends GetxController {
  final AuthService _authService = Get.find<AuthService>();

  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final nameController = TextEditingController();
  final confirmPasswordController = TextEditingController();

  // ── Reactive State ─────────────────────────────────────
  final _isLogin = true.obs;
  bool get isLogin => _isLogin.value;

  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final _obscurePassword = true.obs;
  bool get obscurePassword => _obscurePassword.value;

  final _obscureConfirm = true.obs;
  bool get obscureConfirm => _obscureConfirm.value;

  void toggleMode() {
    _isLogin.value = !_isLogin.value;
    clearFields();
  }

  void toggleObscurePassword() => _obscurePassword.value = !_obscurePassword.value;
  void toggleObscureConfirm() => _obscureConfirm.value = !_obscureConfirm.value;

  void clearFields() {
    emailController.clear();
    passwordController.clear();
    nameController.clear();
    confirmPasswordController.clear();
  }

  Future<void> submit() async {
    if (!_validate()) return;

    _isLoading.value = true;
    try {
      // ── Demo login flow ──
      await Future.delayed(const Duration(milliseconds: 800));

      final name = _isLogin.value ? 'Sari' : nameController.text.trim();
      final email = emailController.text.trim();
      
      _authService.login(name, email);

      if (_isLogin.value) {
        Get.offAllNamed(Routes.home);
      } else {
        Get.offAllNamed(Routes.onboarding);
      }
    } catch (e) {
      Get.snackbar(
        'Error',
        e.toString(),
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: AppColors.errorContainer,
        colorText: AppColors.error,
      );
    } finally {
      _isLoading.value = false;
    }
  }

  bool _validate() {
    if (emailController.text.trim().isEmpty) {
      _showError('Please enter your email');
      return false;
    }
    if (passwordController.text.isEmpty) {
      _showError('Please enter your password');
      return false;
    }
    if (!_isLogin.value) {
      if (nameController.text.trim().isEmpty) {
        _showError('Please enter your name');
        return false;
      }
      if (passwordController.text != confirmPasswordController.text) {
        _showError('Passwords do not match');
        return false;
      }
    }
    return true;
  }

  void _showError(String message) {
    Get.snackbar(
      'Validation',
      message,
      snackPosition: SnackPosition.BOTTOM,
      backgroundColor: AppColors.errorContainer,
      colorText: AppColors.error,
    );
  }

  void logout() {
    _authService.logout();
    Get.offAllNamed(Routes.login);
  }

  @override
  void onClose() {
    emailController.dispose();
    passwordController.dispose();
    nameController.dispose();
    confirmPasswordController.dispose();
    super.onClose();
  }
}
