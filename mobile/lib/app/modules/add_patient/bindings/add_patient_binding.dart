import 'package:get/get.dart';
import '../../../data/repositories/patient_repository.dart';
import '../controllers/add_patient_controller.dart';

class AddPatientBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => PatientRepository());
    Get.lazyPut<AddPatientController>(
      () => AddPatientController(repository: Get.find()),
    );
  }
}
