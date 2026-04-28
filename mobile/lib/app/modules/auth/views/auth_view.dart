import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../controllers/auth_controller.dart';

class AuthView extends GetView<AuthController> {
  const AuthView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 48),
              _buildHeader(),
              const SizedBox(height: 40),
              _buildToggleTabs(),
              const SizedBox(height: 32),
              _buildForm(),
              const SizedBox(height: 24),
              _buildSubmitButton(),
              const SizedBox(height: 16),
              _buildForgotPassword(),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // App logo / wordmark
        Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.favorite_rounded,
                  color: AppColors.onPrimary, size: 22),
            ),
            const SizedBox(width: 10),
            Text('CareTrack',
                style: AppTextStyles.headlineMd
                    .copyWith(fontWeight: FontWeight.w700)),
          ],
        ),
        const SizedBox(height: 32),
        Obx(() => Text(
              controller.isLogin
                  ? "Let's get started"
                  : 'Create account',
              style: AppTextStyles.display,
            )),
        const SizedBox(height: 8),
        Obx(() => Text(
              controller.isLogin
                  ? 'Sign in to continue your caregiving journey.'
                  : 'Join CareTrack and start caring better.',
              style:
                  AppTextStyles.bodyLg.copyWith(color: AppColors.onSurfaceVariant),
            )),
      ],
    );
  }

  Widget _buildToggleTabs() {
    return Obx(() {
      final login = controller.isLogin;
      return Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
        ),
        padding: const EdgeInsets.all(4),
        child: Row(
          children: [
            _tab('Sign In', login, () {
              if (!login) controller.toggleMode();
            }),
            _tab('Sign Up', !login, () {
              if (login) controller.toggleMode();
            }),
          ],
        ),
      );
    });
  }

  Widget _tab(String label, bool active, VoidCallback onTap) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: active ? AppColors.surfaceLowest : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
            boxShadow: active
                ? [
                    BoxShadow(
                      color: AppColors.primary.withValues(alpha: 0.06),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    )
                  ]
                : null,
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: AppTextStyles.labelMd.copyWith(
              fontWeight: FontWeight.w600,
              color: active ? AppColors.onBackground : AppColors.outline,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildForm() {
    return Obx(() {
      final login = controller.isLogin;
      return Column(
        children: [
          if (!login) ...[
            _inputField(
              label: 'Full Name',
              controller: controller.nameController,
              icon: Icons.person_outline_rounded,
              hint: 'e.g. Sari Indah',
            ),
            const SizedBox(height: 16),
          ],
          _inputField(
            label: 'Email',
            controller: controller.emailController,
            icon: Icons.email_outlined,
            hint: 'you@example.com',
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 16),
          Obx(() => _inputField(
                label: 'Password',
                controller: controller.passwordController,
                icon: Icons.lock_outline_rounded,
                hint: '••••••••',
                obscure: controller.obscurePassword,
                suffixIcon: IconButton(
                  icon: Icon(
                    controller.obscurePassword
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                    color: AppColors.outline,
                    size: 20,
                  ),
                  onPressed: controller.toggleObscurePassword,
                ),
              )),
          if (!login) ...[
            const SizedBox(height: 16),
            Obx(() => _inputField(
                  label: 'Confirm Password',
                  controller: controller.confirmPasswordController,
                  icon: Icons.lock_outline_rounded,
                  hint: '••••••••',
                  obscure: controller.obscureConfirm,
                  suffixIcon: IconButton(
                    icon: Icon(
                      controller.obscureConfirm
                          ? Icons.visibility_outlined
                          : Icons.visibility_off_outlined,
                      color: AppColors.outline,
                      size: 20,
                    ),
                    onPressed: controller.toggleObscureConfirm,
                  ),
                )),
          ],
        ],
      );
    });
  }

  Widget _inputField({
    required String label,
    required TextEditingController controller,
    required IconData icon,
    String? hint,
    bool obscure = false,
    TextInputType? keyboardType,
    Widget? suffixIcon,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: obscure,
      keyboardType: keyboardType,
      style: AppTextStyles.bodyMd,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: Icon(icon, size: 20, color: AppColors.outline),
        suffixIcon: suffixIcon,
      ),
    );
  }

  Widget _buildSubmitButton() {
    return Obx(() => ElevatedButton(
          onPressed:
              controller.isLoading ? null : controller.submit,
          child: controller.isLoading
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation(Colors.white)),
                )
              : Obx(() => Text(
                    controller.isLogin ? 'Sign In' : 'Create Account',
                  )),
        ));
  }

  Widget _buildForgotPassword() {
    return Obx(() => controller.isLogin
        ? Center(
            child: TextButton(
              onPressed: () {},
              child: Text(
                'Forgot password?',
                style: AppTextStyles.labelMd.copyWith(color: AppColors.primary),
              ),
            ),
          )
        : const SizedBox.shrink());
  }
}
