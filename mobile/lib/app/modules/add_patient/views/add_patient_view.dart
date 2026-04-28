import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../../../routes/app_pages.dart';
import '../controllers/add_patient_controller.dart';

class AddPatientView extends GetView<AddPatientController> {
  const AddPatientView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          onPressed: () => Get.back(),
        ),
        title: const Text('Add New Patient'),
        actions: [
          TextButton(
            onPressed: () => Get.offAllNamed(Routes.home),
            child: Text('Cancel',
                style: AppTextStyles.labelMd
                    .copyWith(color: AppColors.outline)),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Form(
                key: controller.formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _sectionTitle('Profile Photo'),
                    const SizedBox(height: 16),
                    _buildProfilePhotoPicker(),
                    const SizedBox(height: 32),

                    _sectionTitle('Basic Information'),
                    const SizedBox(height: 16),
                    _field(
                      label: 'Full Name',
                      controller: controller.nameController,
                      icon: Icons.person_outline_rounded,
                      hint: 'e.g. Ibu Siti',
                      required: true,
                      validator: (value) =>
                          value == null || value.trim().isEmpty ? 'Please enter a name' : null,
                    ),
                    const SizedBox(height: 16),
                    _field(
                      label: 'Age',
                      controller: controller.ageController,
                      icon: Icons.cake_outlined,
                      hint: 'e.g. 78',
                      keyboardType: TextInputType.number,
                    ),
                    const SizedBox(height: 16),
                    _buildDropdown(
                      label: 'Gender',
                      value: controller.gender,
                      items: controller.genders,
                      hint: 'Select gender',
                    ),
                    const SizedBox(height: 16),
                    _field(
                      label: 'Address',
                      controller: controller.addressController,
                      icon: Icons.location_on_outlined,
                      hint: 'Street address',
                      maxLines: 2,
                    ),
                    const SizedBox(height: 16),
                    _field(
                      label: 'Phone Number',
                      controller: controller.phoneController,
                      icon: Icons.phone_outlined,
                      hint: '+62 xxx xxxx xxxx',
                      keyboardType: TextInputType.phone,
                    ),
                    const SizedBox(height: 32),

                    _sectionTitle('Health & Physical Condition'),
                    const SizedBox(height: 16),
                    _buildDropdown(
                      label: 'Blood Type',
                      value: controller.bloodType,
                      items: controller.bloodTypes,
                      hint: 'Select blood type',
                    ),
                    const SizedBox(height: 16),
                    _field(
                      label: 'Physical Condition',
                      controller: controller.physicalConditionController,
                      icon: Icons.health_and_safety_outlined,
                      hint: 'e.g. Weak, Good, Requires therapy',
                      maxLines: 2,
                    ),
                    const SizedBox(height: 16),
                    _buildDropdown(
                      label: 'Mobility Level',
                      value: controller.mobilityLevel,
                      items: controller.mobilityLevels,
                      hint: 'Select mobility level',
                    ),
                    const SizedBox(height: 16),
                    _field(
                      label: 'Medical History',
                      controller: controller.medicalHistoryController,
                      icon: Icons.medical_information_outlined,
                      hint: 'e.g. Hypertension, Diabetes Type 2',
                      maxLines: 3,
                    ),
                    const SizedBox(height: 16),
                    _field(
                      label: 'Allergies',
                      controller: controller.allergiesController,
                      icon: Icons.warning_amber_outlined,
                      hint: 'e.g. Penicillin, Shellfish',
                      maxLines: 2,
                    ),
                    const SizedBox(height: 32),

                    _sectionTitle('Personal & Interests'),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.accent.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.info_outline_rounded,
                              size: 18, color: AppColors.accentDark),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Used for AI-powered activity recommendations.',
                              style: AppTextStyles.labelMd
                                  .copyWith(color: AppColors.accentDark),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    _field(
                      label: 'Hobbies & Interests',
                      controller: controller.hobbiesController,
                      icon: Icons.star_outline_rounded,
                      hint: 'e.g. Gardening, Reading, Music',
                      maxLines: 3,
                    ),
                    const SizedBox(height: 16),
                    _field(
                      label: 'Additional Notes',
                      controller: controller.notesController,
                      icon: Icons.notes_rounded,
                      hint: 'Anything else the caregiver should know...',
                      maxLines: 4,
                    ),
                  ],
                ),
              ),
            ),
          ),
          _buildBottomBar(),
        ],
      ),
    );
  }

  Widget _buildProfilePhotoPicker() {
    return Center(
      child: Stack(
        children: [
          CircleAvatar(
            radius: 50,
            backgroundColor: AppColors.surface,
            child: const Icon(Icons.person, size: 50, color: AppColors.outline),
          ),
          Positioned(
            bottom: 0,
            right: 0,
            child: InkWell(
              onTap: controller.pickProfilePhoto,
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: const BoxDecoration(
                  color: AppColors.primary,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.camera_alt, color: Colors.white, size: 20),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionTitle(String title) {
    return Text(
      title,
      style: AppTextStyles.headlineMd.copyWith(fontWeight: FontWeight.bold),
    );
  }

  Widget _buildDropdown({
    required String label,
    required RxnString value,
    required List<String> items,
    required String hint,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label,
            style: AppTextStyles.labelMd
                .copyWith(color: AppColors.onSurfaceVariant)),
        const SizedBox(height: 8),
        Obx(() => DropdownButtonFormField<String>(
              initialValue: value.value,
              hint: Text(hint, style: AppTextStyles.bodyMd),
              decoration: const InputDecoration(),
              items: items
                  .map((t) => DropdownMenuItem(value: t, child: Text(t)))
                  .toList(),
              onChanged: (v) => value.value = v,
              style: AppTextStyles.bodyMd,
            )),
      ],
    );
  }

  Widget _field({
    required String label,
    required TextEditingController controller,
    required IconData icon,
    String? hint,
    bool required = false,
    int maxLines = 1,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        RichText(
          text: TextSpan(
            text: label,
            style: AppTextStyles.labelMd
                .copyWith(color: AppColors.onSurfaceVariant),
            children: required
                ? [
                    const TextSpan(
                        text: ' *', style: TextStyle(color: AppColors.error))
                  ]
                : null,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          maxLines: maxLines,
          keyboardType: keyboardType,
          style: AppTextStyles.bodyMd,
          validator: validator,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon:
                maxLines == 1 ? Icon(icon, size: 20, color: AppColors.outline) : null,
          ),
        ),
      ],
    );
  }

  Widget _buildBottomBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
      decoration: BoxDecoration(
        color: AppColors.background,
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.05),
            blurRadius: 12,
            offset: const Offset(0, -4),
          )
        ],
      ),
      child: Obx(() {
        return ElevatedButton(
          onPressed: controller.isLoading ? null : controller.submit,
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            foregroundColor: AppColors.onPrimary,
          ),
          child: controller.isLoading
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(
                      strokeWidth: 2, valueColor: AlwaysStoppedAnimation(Colors.white)),
                )
              : const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Save Patient'),
                    SizedBox(width: 8),
                    Icon(Icons.check_circle_outline_rounded),
                  ],
                ),
        );
      }),
    );
  }
}
