import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/models/patient_model.dart';
import '../../../data/repositories/vital_repository.dart';
import '../../../data/models/vital_model.dart';

class DashboardController extends GetxController {
  final VitalRepository _vitalRepository;

  DashboardController({required VitalRepository vitalRepository}) : _vitalRepository = vitalRepository;

  late final Patient patient;

  // ── Reactive State ─────────────────────────────────────
  final _vitals = <Vital>[].obs;
  List<Vital> get vitals => _vitals;

  final _healthAnalysis = Rxn<Map<String, dynamic>>();
  Map<String, dynamic>? get healthAnalysis => _healthAnalysis.value;

  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final _isAnalyzing = false.obs;
  bool get isAnalyzing => _isAnalyzing.value;

  final _errorMsg = ''.obs;
  String get errorMsg => _errorMsg.value;

  @override
  void onInit() {
    super.onInit();
    final arg = Get.arguments;
    if (arg is Patient) {
      patient = arg;
    } else {
      // Demo patient for fallback
      patient = Patient(id: 1, name: 'Eleanor Vance', age: 82);
    }
    loadData();
  }

  Future<void> loadData() async {
    if (patient.id == null) {
      _vitals.assignAll(_demoVitals());
      return;
    }
    _isLoading.value = true;
    try {
      final result = await _vitalRepository.fetchVitals(patient.id!);
      _vitals.assignAll(result.isEmpty ? _demoVitals() : result);
    } catch (_) {
      _vitals.assignAll(_demoVitals());
    } finally {
      _isLoading.value = false;
    }
  }

  Future<void> analyzeHealth() async {
    if (patient.id == null) return;
    _isAnalyzing.value = true;
    try {
      final result = await _vitalRepository.analyzeHealth(patient.id!);
      _healthAnalysis.value = result;
    } catch (e) {
      Get.snackbar(
        'Error',
        e.toString(),
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: AppColors.errorContainer,
        colorText: AppColors.error,
      );
    } finally {
      _isAnalyzing.value = false;
    }
  }

  Vital? get latestVital => _vitals.isNotEmpty ? _vitals.last : null;

  String get healthStatusLabel {
    final status = latestVital?.healthStatus?.toLowerCase() ?? 'normal';
    if (status.contains('danger') || status.contains('critical')) {
      return 'Needs Attention';
    }
    if (status.contains('warning') || status.contains('moderate')) {
      return 'Monitor Closely';
    }
    return 'Stable';
  }

  Color get healthStatusColor {
    final status = latestVital?.healthStatus?.toLowerCase() ?? 'normal';
    if (status.contains('danger') || status.contains('critical')) {
      return AppColors.statusDanger;
    }
    if (status.contains('warning') || status.contains('moderate')) {
      return AppColors.statusWarning;
    }
    return AppColors.statusGood;
  }

  List<Vital> _demoVitals() {
    final now = DateTime.now();
    return List.generate(7, (i) {
      return Vital(
        id: i + 1,
        patientId: 1,
        recordedAt: now.subtract(Duration(days: 6 - i)),
        systolic: 120 + (i % 3) * 5.0,
        diastolic: 80 + (i % 2) * 3.0,
        heartRate: 72 + (i % 4) * 2.0,
        temperature: 36.5 + (i % 3) * 0.2,
        bloodSugar: 95 + (i % 5) * 5.0,
        spO2: 97 + (i % 2) * 1.0,
        healthStatus: 'normal',
      );
    });
  }
}
