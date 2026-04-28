import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/models/vital_model.dart';
import '../controllers/dashboard_controller.dart';

class DashboardView extends GetView<DashboardController> {
  const DashboardView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: CustomScrollView(
        slivers: [
          _buildSliverAppBar(),
          SliverToBoxAdapter(
            child: Obx(() {
              if (controller.isLoading) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(40),
                    child:
                        CircularProgressIndicator(color: AppColors.primary),
                  ),
                );
              }
              return Column(
                children: [
                  _buildStatusCard(),
                  _buildMorningVitals(),
                  _buildStabilitySection(),
                  _buildAnalysisSection(),
                  const SizedBox(height: 100),
                ],
              );
            }),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: controller.analyzeHealth,
        backgroundColor: AppColors.accent,
        foregroundColor: AppColors.onBackground,
        icon: const Icon(Icons.analytics_outlined, size: 20),
        label: Text('Analyze',
            style:
                AppTextStyles.labelMd.copyWith(fontWeight: FontWeight.w700)),
      ),
    );
  }

  Widget _buildSliverAppBar() {
    return SliverAppBar(
      expandedHeight: 200,
      floating: false,
      pinned: true,
      backgroundColor: AppColors.background,
      elevation: 0,
      scrolledUnderElevation: 0,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
        onPressed: () => Get.back(),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.edit_outlined, size: 20),
          onPressed: () {},
        ),
      ],
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          padding: const EdgeInsets.fromLTRB(20, 80, 20, 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Center(
                      child: Text(
                        controller.patient.initials,
                        style: AppTextStyles.headlineMd.copyWith(
                            color: Colors.white, fontWeight: FontWeight.w700),
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${controller.patient.name}, ${controller.patient.age}',
                          style: AppTextStyles.headlineMd,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Good morning. Eleanor rested well through the night.',
                          style: AppTextStyles.labelMd
                              .copyWith(color: AppColors.onSurfaceVariant),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusCard() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
      child: Obx(() => Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: controller.healthStatusColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                  color: controller.healthStatusColor.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: controller.healthStatusColor.withValues(alpha: 0.15),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    controller.healthStatusLabel == 'Stable'
                        ? Icons.favorite_rounded
                        : Icons.warning_rounded,
                    color: controller.healthStatusColor,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Health Status',
                          style: AppTextStyles.labelSm),
                      const SizedBox(height: 2),
                      Text(
                        controller.healthStatusLabel,
                        style: AppTextStyles.bodyMd.copyWith(
                          color: controller.healthStatusColor,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
                Text(
                  _formatDate(DateTime.now()),
                  style:
                      AppTextStyles.labelSm.copyWith(color: AppColors.outline),
                ),
              ],
            ),
          )),
    );
  }

  Widget _buildMorningVitals() {
    final vital = controller.latestVital;
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Morning Vitals', style: AppTextStyles.headlineMd),
          const SizedBox(height: 12),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            childAspectRatio: 1.5,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            children: [
              _vitalCard(
                icon: Icons.favorite_rounded,
                label: 'Blood Pressure',
                value: vital != null
                    ? '${vital.systolic?.toInt()}/${vital.diastolic?.toInt()}'
                    : '--/--',
                unit: 'mmHg',
                color: const Color(0xFFDC2626),
              ),
              _vitalCard(
                icon: Icons.monitor_heart_outlined,
                label: 'Heart Rate',
                value: vital?.heartRate?.toInt().toString() ?? '--',
                unit: 'bpm',
                color: const Color(0xFFEC4899),
              ),
              _vitalCard(
                icon: Icons.thermostat_rounded,
                label: 'Temperature',
                value: vital?.temperature?.toStringAsFixed(1) ?? '--',
                unit: '°C',
                color: const Color(0xFFF59E0B),
              ),
              _vitalCard(
                icon: Icons.water_drop_outlined,
                label: 'Blood Sugar',
                value: vital?.bloodSugar?.toInt().toString() ?? '--',
                unit: 'mg/dL',
                color: const Color(0xFF2563EB),
              ),
              _vitalCard(
                icon: Icons.air_rounded,
                label: 'SpO₂',
                value: vital?.spO2?.toInt().toString() ?? '--',
                unit: '%',
                color: const Color(0xFF16A34A),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _vitalCard({
    required IconData icon,
    required String label,
    required String value,
    required String unit,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surfaceLowest,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          )
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, size: 16, color: color),
              ),
            ],
          ),
          const Spacer(),
          Text(value,
              style: AppTextStyles.headlineMd
                  .copyWith(fontWeight: FontWeight.w700)),
          Text('$label · $unit',
              style: AppTextStyles.labelSm,
              maxLines: 1,
              overflow: TextOverflow.ellipsis),
        ],
      ),
    );
  }

  Widget _buildStabilitySection() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 24, 20, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('7-Day Stability', style: AppTextStyles.headlineMd),
              Text('Last 7 days',
                  style: AppTextStyles.labelSm
                      .copyWith(color: AppColors.outline)),
            ],
          ),
          const SizedBox(height: 16),
          Obx(() => _stabilityChart(controller.vitals)),
        ],
      ),
    );
  }

  Widget _stabilityChart(List<Vital> vitals) {
    if (vitals.isEmpty) return const SizedBox.shrink();
    final maxBP = 160.0;
    return Container(
      height: 120,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surfaceLowest,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          )
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: vitals.map((v) {
          final height = ((v.systolic ?? 120) / maxBP).clamp(0.2, 1.0);
          final isToday = v == vitals.last;
          return Column(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Expanded(
                child: Align(
                  alignment: Alignment.bottomCenter,
                  child: FractionallySizedBox(
                    heightFactor: height,
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 400),
                      width: 24,
                      decoration: BoxDecoration(
                        color: isToday
                            ? AppColors.accent
                            : AppColors.accent.withValues(alpha: 0.35),
                        borderRadius: const BorderRadius.vertical(
                            top: Radius.circular(4)),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 6),
              Text(
                v.recordedAt != null
                    ? _dayLabel(v.recordedAt!)
                    : '--',
                style: AppTextStyles.labelSm,
              ),
            ],
          );
        }).toList(),
      ),
    );
  }

  Widget _buildAnalysisSection() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 24, 20, 0),
      child: Obx(() {
        final analysis = controller.healthAnalysis;
        if (controller.isAnalyzing) {
          return Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.surfaceLowest,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                      strokeWidth: 2, color: AppColors.primary),
                ),
                SizedBox(width: 12),
                Text('Analyzing health data...'),
              ],
            ),
          );
        }
        if (analysis == null) {
          return Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.accent.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                  color: AppColors.accent.withValues(alpha: 0.25)),
            ),
            child: Row(
              children: [
                const Icon(Icons.lightbulb_outline_rounded,
                    color: AppColors.accentDark, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Tap "Analyze" to run AI fuzzy health assessment.',
                    style: AppTextStyles.bodyMd
                        .copyWith(color: AppColors.accentDark),
                  ),
                ),
              ],
            ),
          );
        }
        return _analysisCard(analysis);
      }),
    );
  }

  Widget _analysisCard(Map<String, dynamic> analysis) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surfaceLowest,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.05),
            blurRadius: 12,
            offset: const Offset(0, 4),
          )
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('AI Health Analysis', style: AppTextStyles.headlineMd),
          const SizedBox(height: 12),
          const Divider(),
          const SizedBox(height: 12),
          ...analysis.entries
              .where((e) => e.key != 'patient_id')
              .map((e) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          flex: 2,
                          child: Text(
                            _humanizeKey(e.key),
                            style: AppTextStyles.labelMd.copyWith(
                                color: AppColors.onSurfaceVariant),
                          ),
                        ),
                        Expanded(
                          flex: 3,
                          child: Text(
                            e.value?.toString() ?? '--',
                            style: AppTextStyles.bodyMd.copyWith(
                                fontWeight: FontWeight.w600),
                          ),
                        ),
                      ],
                    ),
                  )),
        ],
      ),
    );
  }

  String _humanizeKey(String key) {
    return key
        .replaceAll('_', ' ')
        .split(' ')
        .map((w) => w.isNotEmpty
            ? '${w[0].toUpperCase()}${w.substring(1)}'
            : '')
        .join(' ');
  }

  String _formatDate(DateTime dt) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${dt.day} ${months[dt.month - 1]}';
  }

  String _dayLabel(DateTime dt) {
    const days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
    return days[dt.weekday - 1];
  }
}
