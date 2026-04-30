import 'package:get/get.dart';

import '../modules/home/bindings/home_binding.dart';
import '../modules/home/views/home_view.dart';
import '../modules/patient_detail/bindings/patient_detail_binding.dart';
import '../modules/patient_detail/views/patient_detail_view.dart';
part 'app_routes.dart';

class AppPages {
  AppPages._();

  static const INITIAL = Routes.HOME;

  static final routes = [
    GetPage(
      name: _Paths.HOME,
      page: () => const HomeView(),
      binding: HomeBinding(),
    ),
    GetPage(
      name: _Paths.PATIENT_DETAIL,
      page: () => const PatientDetailView(),
      binding: PatientDetailBinding(),
    ),
  ];
}
