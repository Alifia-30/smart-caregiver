import 'package:get/get.dart';

import '../modules/auth/bindings/auth_binding.dart';
import '../modules/auth/views/auth_view.dart';
import '../modules/home/bindings/home_binding.dart';
import '../modules/home/views/home_view.dart';
import '../modules/add_patient/bindings/add_patient_binding.dart';
import '../modules/add_patient/views/add_patient_view.dart';
import '../modules/onboarding/views/onboarding_view.dart';
import '../modules/dashboard/bindings/dashboard_binding.dart';
import '../modules/dashboard/views/dashboard_view.dart';

part 'app_routes.dart';

class AppPages {
  AppPages._();

  static const initial = Routes.login;

  static final routes = [
    GetPage(
      name: _Paths.login,
      page: () => const AuthView(),
      binding: AuthBinding(),
      transition: Transition.fadeIn,
    ),
    GetPage(
      name: _Paths.home,
      page: () => const HomeView(),
      binding: HomeBinding(),
      transition: Transition.fadeIn,
    ),
    GetPage(
      name: _Paths.addPatient,
      page: () => const AddPatientView(),
      binding: AddPatientBinding(),
      transition: Transition.rightToLeft,
    ),
    GetPage(
      name: _Paths.onboarding,
      page: () => const OnboardingView(),
      transition: Transition.upToDown,
    ),
    GetPage(
      name: _Paths.dashboard,
      page: () => const DashboardView(),
      binding: DashboardBinding(),
      transition: Transition.rightToLeft,
    ),
  ];
}
