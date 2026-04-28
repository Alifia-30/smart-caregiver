import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';

import '../../../core/theme/app_theme.dart';
import '../../../data/models/health_record_model.dart';
import '../controllers/input_health_controller.dart';

class InputHealthView extends GetView<InputHealthController> {
  const InputHealthView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            // ── Top Bar ──────────────────────────────────────────────
            _buildTopBar(),

            // ── Scrollable Content ───────────────────────────────────
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header
                    Text('Log Health Data', style: AppTextStyles.headlineLg),
                    const SizedBox(height: 4),
                    Text(
                      'Catat tanda vital dan kondisi hari ini.',
                      style: AppTextStyles.bodyMd.copyWith(
                        color: AppColors.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 24),

                    // ── Condition Selector ────────────────────────────
                    _buildConditionSelector(),
                    const SizedBox(height: 24),

                    // ── Vital Parameters Card ────────────────────────
                    _buildVitalsCard(),
                    const SizedBox(height: 24),

                    // ── Additional Parameters (Expandable) ───────────
                    _buildAdditionalVitalsCard(),
                    const SizedBox(height: 24),

                    // ── Notes Section ────────────────────────────────
                    _buildNotesSection(),
                    const SizedBox(height: 24),

                    // ── Complaints Section ───────────────────────────
                    _buildComplaintsSection(),
                    const SizedBox(height: 32),

                    // ── Submit Button ────────────────────────────────
                    _buildSubmitButton(),
                    const SizedBox(height: 16),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Top Bar
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildTopBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Get.back(),
            icon: const Icon(
              Icons.arrow_back_rounded,
              color: AppColors.onBackground,
            ),
            style: IconButton.styleFrom(
              backgroundColor: AppColors.surfaceLow,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'CareTrack',
                  style: AppTextStyles.headlineMd.copyWith(
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.3,
                  ),
                ),
                Text(
                  controller.elderlyName,
                  style: AppTextStyles.labelSm.copyWith(
                    color: AppColors.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: () {},
            icon: const Icon(
              Icons.notifications_outlined,
              color: AppColors.onBackground,
            ),
          ),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Condition Selector
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildConditionSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'OVERALL CONDITION',
          style: AppTextStyles.labelSm.copyWith(
            color: AppColors.onSurfaceVariant,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 12),
        Obx(() => Row(
              children: [
                _conditionChip(
                  status: HealthStatus.normal,
                  icon: Icons.sentiment_satisfied_alt_rounded,
                  color: AppColors.statusGood,
                  bgColor: const Color(0xFFDCFCE7),
                ),
                const SizedBox(width: 8),
                _conditionChip(
                  status: HealthStatus.needsAttention,
                  icon: Icons.sentiment_neutral_rounded,
                  color: AppColors.statusWarning,
                  bgColor: const Color(0xFFFEF3C7),
                ),
                const SizedBox(width: 8),
                _conditionChip(
                  status: HealthStatus.critical,
                  icon: Icons.sentiment_dissatisfied_rounded,
                  color: AppColors.statusDanger,
                  bgColor: const Color(0xFFFEE2E2),
                ),
              ],
            )),
      ],
    );
  }

  Widget _conditionChip({
    required HealthStatus status,
    required IconData icon,
    required Color color,
    required Color bgColor,
  }) {
    final isSelected = controller.selectedStatus.value == status;
    return Expanded(
      child: GestureDetector(
        onTap: () => controller.selectStatus(status),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOutCubic,
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: isSelected ? bgColor : AppColors.surfaceLow,
            borderRadius: BorderRadius.circular(50),
            border: Border.all(
              color: isSelected ? color.withValues(alpha: 0.4) : Colors.transparent,
              width: 1.5,
            ),
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: color.withValues(alpha: 0.15),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : [],
          ),
          child: Column(
            children: [
              Icon(
                icon,
                color: isSelected ? color : AppColors.outline,
                size: 24,
              ),
              const SizedBox(height: 4),
              Text(
                status.label,
                style: AppTextStyles.labelSm.copyWith(
                  color: isSelected ? color : AppColors.outline,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Vital Parameters Card
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildVitalsCard() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceLowest,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          _vitalRow(
            icon: Icons.favorite_rounded,
            label: 'Tekanan Darah',
            unit: 'mmHg',
            controller1: controller.systolicCtrl,
            controller2: controller.diastolicCtrl,
            hint1: '120',
            hint2: '80',
            isBP: true,
          ),
          _divider(),
          _vitalRow(
            icon: Icons.water_drop_rounded,
            label: 'Gula Darah',
            unit: 'mg/dL',
            controller1: controller.bloodSugarCtrl,
            hint1: '95',
          ),
          _divider(),
          _vitalRow(
            icon: Icons.monitor_heart_rounded,
            label: 'Detak Jantung',
            unit: 'bpm',
            controller1: controller.heartRateCtrl,
            hint1: '72',
          ),
          _divider(),
          _vitalRow(
            icon: Icons.thermostat_rounded,
            label: 'Suhu Tubuh',
            unit: '°C',
            controller1: controller.temperatureCtrl,
            hint1: '36.5',
            isDecimal: true,
          ),
          _divider(),
          _vitalRow(
            icon: Icons.scale_rounded,
            label: 'Berat Badan',
            unit: 'kg',
            controller1: controller.weightCtrl,
            hint1: '65.0',
            isDecimal: true,
          ),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Additional Vitals (Cholesterol, Uric Acid, SpO2)
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildAdditionalVitalsCard() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceLowest,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Theme(
        data: Theme.of(Get.context!).copyWith(
          dividerColor: Colors.transparent,
        ),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          childrenPadding: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          collapsedShape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          leading: Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(50),
            ),
            child: const Icon(
              Icons.science_rounded,
              size: 16,
              color: AppColors.onSurfaceVariant,
            ),
          ),
          title: Text(
            'Parameter Tambahan',
            style: AppTextStyles.labelMd.copyWith(
              color: AppColors.onSurface,
            ),
          ),
          subtitle: Text(
            'Kolesterol, Asam Urat, SpO2',
            style: AppTextStyles.labelSm.copyWith(
              color: AppColors.outline,
              fontWeight: FontWeight.w400,
            ),
          ),
          children: [
            _divider(),
            _vitalRow(
              icon: Icons.biotech_rounded,
              label: 'Kolesterol',
              unit: 'mg/dL',
              controller1: controller.cholesterolCtrl,
              hint1: '200',
            ),
            _divider(),
            _vitalRow(
              icon: Icons.science_outlined,
              label: 'Asam Urat',
              unit: 'mg/dL',
              controller1: controller.uricAcidCtrl,
              hint1: '5.0',
              isDecimal: true,
            ),
            _divider(),
            _vitalRow(
              icon: Icons.air_rounded,
              label: 'SpO2',
              unit: '%',
              controller1: controller.spo2Ctrl,
              hint1: '98',
            ),
          ],
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Shared Vital Row Widget
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _vitalRow({
    required IconData icon,
    required String label,
    required String unit,
    required TextEditingController controller1,
    TextEditingController? controller2,
    required String hint1,
    String? hint2,
    bool isBP = false,
    bool isDecimal = false,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Row(
        children: [
          // Icon
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(50),
            ),
            child: Icon(icon, size: 16, color: AppColors.onSurfaceVariant),
          ),
          const SizedBox(width: 12),

          // Label
          Expanded(
            child: Text(
              label,
              style: AppTextStyles.labelMd.copyWith(
                color: AppColors.onSurface,
              ),
            ),
          ),

          // Input(s)
          if (isBP) ...[
            _numericField(
              controller: controller1,
              hint: hint1,
              width: 50,
              isDecimal: false,
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 2),
              child: Text(
                '/',
                style: AppTextStyles.bodyMd.copyWith(
                  color: AppColors.outline,
                ),
              ),
            ),
            _numericField(
              controller: controller2!,
              hint: hint2!,
              width: 50,
              isDecimal: false,
            ),
          ] else
            _numericField(
              controller: controller1,
              hint: hint1,
              width: 64,
              isDecimal: isDecimal,
            ),

          const SizedBox(width: 8),

          // Unit
          SizedBox(
            width: 42,
            child: Text(
              unit,
              style: AppTextStyles.labelSm.copyWith(
                color: AppColors.outline,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _numericField({
    required TextEditingController controller,
    required String hint,
    required double width,
    bool isDecimal = false,
  }) {
    return SizedBox(
      width: width,
      child: TextField(
        controller: controller,
        keyboardType: TextInputType.numberWithOptions(decimal: isDecimal),
        inputFormatters: [
          FilteringTextInputFormatter.allow(
            isDecimal ? RegExp(r'^\d*\.?\d*') : RegExp(r'^\d*'),
          ),
        ],
        textAlign: TextAlign.end,
        style: AppTextStyles.bodyMd.copyWith(
          color: AppColors.onBackground,
          fontWeight: FontWeight.w500,
        ),
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: AppTextStyles.bodyMd.copyWith(
            color: AppColors.outlineVariant,
          ),
          border: InputBorder.none,
          enabledBorder: InputBorder.none,
          focusedBorder: InputBorder.none,
          isDense: true,
          contentPadding: EdgeInsets.zero,
          fillColor: Colors.transparent,
          filled: true,
        ),
      ),
    );
  }

  Widget _divider() {
    return const Divider(
      height: 1,
      thickness: 1,
      indent: 16,
      endIndent: 16,
      color: AppColors.surfaceLow,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Notes Section
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildNotesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4),
          child: Text(
            'Catatan Perawatan',
            style: AppTextStyles.labelMd.copyWith(
              color: AppColors.onSurface,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: AppColors.surfaceLowest,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.outlineVariant, width: 1),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: TextField(
            controller: controller.dailyNotesCtrl,
            maxLines: 4,
            style: AppTextStyles.bodyMd,
            decoration: InputDecoration(
              hintText: 'Observasi atau catatan tambahan hari ini...',
              hintStyle: AppTextStyles.bodyMd.copyWith(
                color: AppColors.outlineVariant,
              ),
              border: InputBorder.none,
              enabledBorder: InputBorder.none,
              focusedBorder: InputBorder.none,
              contentPadding: const EdgeInsets.all(16),
              fillColor: Colors.transparent,
              filled: true,
            ),
          ),
        ),
      ],
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Complaints Section
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildComplaintsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4),
          child: Text(
            'Keluhan',
            style: AppTextStyles.labelMd.copyWith(
              color: AppColors.onSurface,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: AppColors.surfaceLowest,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.outlineVariant, width: 1),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: TextField(
            controller: controller.complaintsCtrl,
            maxLines: 3,
            style: AppTextStyles.bodyMd,
            decoration: InputDecoration(
              hintText: 'Keluhan yang dialami lansia hari ini...',
              hintStyle: AppTextStyles.bodyMd.copyWith(
                color: AppColors.outlineVariant,
              ),
              border: InputBorder.none,
              enabledBorder: InputBorder.none,
              focusedBorder: InputBorder.none,
              contentPadding: const EdgeInsets.all(16),
              fillColor: Colors.transparent,
              filled: true,
            ),
          ),
        ),
      ],
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Submit Button
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildSubmitButton() {
    return Obx(() {
      final saving = controller.isSaving.value;
      return AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: double.infinity,
        height: 56,
        child: ElevatedButton(
          onPressed: saving ? null : controller.saveHealthData,
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            foregroundColor: AppColors.onPrimary,
            disabledBackgroundColor: AppColors.primary.withValues(alpha: 0.6),
            disabledForegroundColor: AppColors.onPrimary.withValues(alpha: 0.6),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            elevation: 2,
            shadowColor: AppColors.primary.withValues(alpha: 0.3),
          ),
          child: saving
              ? const SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(
                    strokeWidth: 2.5,
                    valueColor: AlwaysStoppedAnimation(AppColors.onPrimary),
                  ),
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.check_circle_rounded, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'Simpan Data Kesehatan',
                      style: AppTextStyles.labelMd.copyWith(
                        color: AppColors.onPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
        ),
      );
    });
  }
}
