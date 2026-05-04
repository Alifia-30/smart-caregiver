import 'package:get/get.dart';

class TambahLansiaController extends GetxController {
  final namaLengkap = ''.obs;
  final umur = ''.obs;
  
  final jenisKelamin = 'Pria'.obs; // Pria or Wanita
  
  final riwayatMedis = ''.obs;
  
  final kondisiFisik = 'Mandiri'.obs; // Mandiri or Bantuan
  final mobilitas = 'Berjalan'.obs; // Berjalan or Kursi Roda
  
  final minatHobi = ''.obs;

  void simpan() {
    if (namaLengkap.value.isEmpty || umur.value.isEmpty) {
      Get.snackbar('Error', 'Nama dan Umur harus diisi');
      return;
    }
    // Save logic implementation here
    Get.back();
    Get.snackbar('Sukses', 'Data Lansia berhasil ditambahkan');
  }
}
