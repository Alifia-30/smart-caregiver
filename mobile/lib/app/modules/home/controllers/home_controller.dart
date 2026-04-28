import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/models/patient_model.dart';
import '../../../data/repositories/patient_repository.dart';
import '../../../routes/app_pages.dart';

class HomeController extends GetxController {
  final PatientRepository _repository;

  HomeController({required PatientRepository repository}) : _repository = repository;

  // ── Reactive State ─────────────────────────────────────
  final _patients = <Patient>[].obs;
  List<Patient> get patients => _patients;

  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final _errorMsg = ''.obs;
  String get errorMsg => _errorMsg.value;

  final _searchQuery = ''.obs;
  String get searchQuery => _searchQuery.value;

  // ── UI Controllers ────────────────────────────────────
  final searchController = TextEditingController();

  // ── Computed ──────────────────────────────────────────
  List<Patient> get filteredPatients {
    final q = _searchQuery.value.toLowerCase();
    if (q.isEmpty) return _patients;
    return _patients.where((p) => p.name.toLowerCase().contains(q)).toList();
  }

  @override
  void onInit() {
    super.onInit();
    loadPatients();
  }

  void onSearchChanged(String value) {
    _searchQuery.value = value;
  }

  Future<void> loadPatients() async {
    _isLoading.value = true;
    _errorMsg.value = '';
    try {
      final result = await _repository.fetchAll();
      _patients.assignAll(result);
    } catch (e) {
      _errorMsg.value = e.toString();
      // Seed with demo data if API unreachable for better UX in demo
      _patients.assignAll(_demoPatients());
    } finally {
      _isLoading.value = false;
    }
  }

  Future<void> deletePatient(int id) async {
    try {
      final success = await _repository.delete(id);
      if (success) {
        _patients.removeWhere((p) => p.id == id);
        Get.snackbar(
          'Success',
          'Patient removed',
          snackPosition: SnackPosition.BOTTOM,
          backgroundColor: AppColors.statusGood,
          colorText: AppColors.onPrimary,
        );
      }
    } catch (e) {
      Get.snackbar(
        'Error',
        e.toString(),
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: AppColors.errorContainer,
        colorText: AppColors.error,
      );
    }
  }

  void goToAddPatient() => Get.toNamed(Routes.addPatient);

  void goToPatientDetail(Patient patient) =>
      Get.toNamed(Routes.dashboard, arguments: patient);

  String get greeting {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  }

  List<Patient> _demoPatients() => [
        Patient(id: 1, name: 'Ibu Siti', age: 78),
        Patient(id: 2, name: 'Pak Budi', age: 82),
        Patient(id: 3, name: 'Oma Maria', age: 88),
        Patient(id: 4, name: 'Opa Joko', age: 75),
      ];

  @override
  void onClose() {
    searchController.dispose();
    super.onClose();
  }
}
