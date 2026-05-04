import 'package:get/get.dart';

import '../controllers/tambah_lansia_controller.dart';

class TambahLansiaBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<TambahLansiaController>(
      () => TambahLansiaController(),
    );
  }
}
