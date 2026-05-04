import 'package:get/get.dart';

class LoginController extends GetxController {
  final email = ''.obs;
  final password = ''.obs;
  
  final isPasswordHidden = true.obs;

  void togglePasswordVisibility() {
    isPasswordHidden.value = !isPasswordHidden.value;
  }

  void login() {
    // Implement login logic here
    // For now, let's just go to home if valid
    if (email.value.isNotEmpty && password.value.isNotEmpty) {
      Get.offAllNamed('/home');
    } else {
      Get.snackbar('Error', 'Please fill in both email and password');
    }
  }

  void loginWithGoogle() {
    // Implement Google login logic here
  }
}
