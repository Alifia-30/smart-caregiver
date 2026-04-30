import 'package:get/get.dart';
import 'package:mobile/app/routes/app_pages.dart';


class SplashController extends GetxController {
  @override
  void onInit() {
    super.onInit();
    // Navigate to HOME after a 3-second delay
    Future.delayed(const Duration(seconds: 3), () {
      Get.offAllNamed(Routes.HOME);
    });
  }
}
