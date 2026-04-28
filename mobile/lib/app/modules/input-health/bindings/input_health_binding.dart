import 'package:get/get.dart';

import '../controllers/input_health_controller.dart';

class InputHealthBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<InputHealthController>(
      () => InputHealthController(),
    );
  }
}
