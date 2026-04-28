import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/repositories/patient_repository.dart';
import '../../../routes/app_pages.dart';

class AddPatientController extends GetxController {
  final PatientRepository _repository;

  AddPatientController({required PatientRepository repository}) : _repository = repository;

  // ── Reactive State ─────────────────────────────────────
  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final bloodType = RxnString();
  final gender = RxnString();
  final mobilityLevel = RxnString();
  final profilePhotoPath = RxnString();

  // ── UI Controllers ────────────────────────────────────
  final formKey = GlobalKey<FormState>();
  final nameController = TextEditingController();
  final ageController = TextEditingController();
  final addressController = TextEditingController();
  final phoneController = TextEditingController();
  final physicalConditionController = TextEditingController();
  final medicalHistoryController = TextEditingController();
  final allergiesController = TextEditingController();
  final hobbiesController = TextEditingController();
  final notesController = TextEditingController();

  final bloodTypes = ['A', 'B', 'AB', 'O', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
  final genders = ['Male', 'Female'];
  final mobilityLevels = ['Independent', 'Requires Assistance', 'Wheelchair Bound', 'Bedridden'];

  void pickProfilePhoto() {
    Get.snackbar(
      'Notice',
      'Image picker is not implemented yet.',
      snackPosition: SnackPosition.BOTTOM,
      backgroundColor: AppColors.surface,
      colorText: AppColors.onSurface,
    );
  }

  Future<void> submit() async {
    if (!formKey.currentState!.validate()) {
      return;
    }

    _isLoading.value = true;
    try {
      final body = {
        'name': nameController.text.trim(),
        'age': int.tryParse(ageController.text.trim()) ?? 0,
        'address': addressController.text.trim(),
        'phone': phoneController.text.trim(),
        'blood_type': bloodType.value,
        'gender': gender.value,
        'profile_photo': profilePhotoPath.value,
        'physical_condition': physicalConditionController.text.trim(),
        'mobility_level': mobilityLevel.value,
        'medical_history': medicalHistoryController.text.trim(),
        'allergies': allergiesController.text.trim(),
        'hobbies': hobbiesController.text.trim(),
        'notes': notesController.text.trim(),
      };

      await _repository.create(body);
      Get.offNamed(Routes.onboarding, arguments: nameController.text.trim());
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

  @override
  void onClose() {
    nameController.dispose();
    ageController.dispose();
    addressController.dispose();
    phoneController.dispose();
    physicalConditionController.dispose();
    medicalHistoryController.dispose();
    allergiesController.dispose();
    hobbiesController.dispose();
    notesController.dispose();
    super.onClose();
  }
}
