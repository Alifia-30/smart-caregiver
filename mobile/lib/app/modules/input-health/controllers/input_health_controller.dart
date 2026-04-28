import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../data/models/health_record_model.dart';

class InputHealthController extends GetxController {
  // ── Form controllers ────────────────────────────────────────────────────
  final systolicCtrl = TextEditingController();
  final diastolicCtrl = TextEditingController();
  final bloodSugarCtrl = TextEditingController();
  final heartRateCtrl = TextEditingController();
  final temperatureCtrl = TextEditingController();
  final weightCtrl = TextEditingController();
  final cholesterolCtrl = TextEditingController();
  final uricAcidCtrl = TextEditingController();
  final spo2Ctrl = TextEditingController();
  final dailyNotesCtrl = TextEditingController();
  final complaintsCtrl = TextEditingController();

  // ── Reactive state ──────────────────────────────────────────────────────
  final selectedStatus = HealthStatus.normal.obs;
  final isLoading = false.obs;
  final isSaving = false.obs;

  /// Mock elderly ID — will be replaced with actual navigation argument later
  String get elderlyId => Get.arguments?['elderlyId'] ?? 'mock-elderly-001';
  String get elderlyName => Get.arguments?['elderlyName'] ?? 'Siti Aminah';


  @override
  void onClose() {
    systolicCtrl.dispose();
    diastolicCtrl.dispose();
    bloodSugarCtrl.dispose();
    heartRateCtrl.dispose();
    temperatureCtrl.dispose();
    weightCtrl.dispose();
    cholesterolCtrl.dispose();
    uricAcidCtrl.dispose();
    spo2Ctrl.dispose();
    dailyNotesCtrl.dispose();
    complaintsCtrl.dispose();
    super.onClose();
  }

  // ── Actions ─────────────────────────────────────────────────────────────

  void selectStatus(HealthStatus status) {
    selectedStatus.value = status;
  }

  /// Validates that at least one vital parameter is filled in.
  bool _validate() {
    final hasVitals = systolicCtrl.text.isNotEmpty ||
        diastolicCtrl.text.isNotEmpty ||
        bloodSugarCtrl.text.isNotEmpty ||
        heartRateCtrl.text.isNotEmpty ||
        temperatureCtrl.text.isNotEmpty ||
        weightCtrl.text.isNotEmpty ||
        cholesterolCtrl.text.isNotEmpty ||
        uricAcidCtrl.text.isNotEmpty ||
        spo2Ctrl.text.isNotEmpty;

    if (!hasVitals) {
      Get.snackbar(
        'Data Kosong',
        'Isi minimal satu parameter vital sebelum menyimpan.',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red.shade50,
        colorText: Colors.red.shade900,
        margin: const EdgeInsets.all(16),
        borderRadius: 12,
        duration: const Duration(seconds: 3),
      );
      return false;
    }
    return true;
  }

  /// Builds a [HealthRecord] from the current form state.
  HealthRecord _buildRecord() {
    return HealthRecord(
      elderlyId: elderlyId,
      systolicBp: double.tryParse(systolicCtrl.text),
      diastolicBp: double.tryParse(diastolicCtrl.text),
      bloodSugar: double.tryParse(bloodSugarCtrl.text),
      heartRate: double.tryParse(heartRateCtrl.text),
      bodyTemperature: double.tryParse(temperatureCtrl.text),
      bodyWeight: double.tryParse(weightCtrl.text),
      cholesterol: double.tryParse(cholesterolCtrl.text),
      uricAcid: double.tryParse(uricAcidCtrl.text),
      spo2Level: double.tryParse(spo2Ctrl.text),
      dailyNotes: dailyNotesCtrl.text.isNotEmpty ? dailyNotesCtrl.text : null,
      complaints: complaintsCtrl.text.isNotEmpty ? complaintsCtrl.text : null,
      healthStatus: selectedStatus.value,
      recordedAt: DateTime.now(),
    );
  }

  /// Simulates saving the health record (mock).
  Future<void> saveHealthData() async {
    if (!_validate()) return;

    isSaving.value = true;

    final record = _buildRecord();

    // ── Mock network delay ───────────────────────────────────────────────
    await Future.delayed(const Duration(seconds: 1));

    // Log the payload for development debugging
    debugPrint('── Mock Save HealthRecord ──');
    debugPrint(record.toJson().toString());

    isSaving.value = false;

    Get.snackbar(
      'Berhasil Disimpan',
      'Data kesehatan $elderlyName berhasil dicatat.',
      snackPosition: SnackPosition.BOTTOM,
      backgroundColor: Colors.green.shade50,
      colorText: Colors.green.shade900,
      margin: const EdgeInsets.all(16),
      borderRadius: 12,
      icon: const Padding(
        padding: EdgeInsets.only(left: 12),
        child: Icon(Icons.check_circle_rounded, color: Colors.green),
      ),
      duration: const Duration(seconds: 3),
    );

    // Navigate back after a short delay to let the user see the snackbar
    await Future.delayed(const Duration(milliseconds: 600));
    Get.back(result: record);
  }
}
