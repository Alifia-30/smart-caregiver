import 'package:get/get.dart';
import '../../../data/repositories/vital_repository.dart';
import '../controllers/dashboard_controller.dart';

class DashboardBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => VitalRepository());
    Get.lazyPut<DashboardController>(
      () => DashboardController(vitalRepository: Get.find()),
    );
  }
}
