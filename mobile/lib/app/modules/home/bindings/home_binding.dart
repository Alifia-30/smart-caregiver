import 'package:get/get.dart';

import '../../../data/repositories/patient_repository.dart';
import '../controllers/home_controller.dart';

class HomeBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => PatientRepository());
    Get.lazyPut<HomeController>(
      () => HomeController(repository: Get.find()),
    );
  }
}
