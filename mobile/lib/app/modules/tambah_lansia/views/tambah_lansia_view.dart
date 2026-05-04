import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../controllers/tambah_lansia_controller.dart';

class TambahLansiaView extends GetView<TambahLansiaController> {
  const TambahLansiaView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF9F9F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFFA8A29E)), // stone-400
          onPressed: () => Get.back(),
        ),
        title: const Text(
          'Tambah Lansia',
          style: TextStyle(
            fontFamily: 'Plus Jakarta Sans',
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: Colors.black,
          ),
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1.0),
          child: Container(
            color: const Color(0xFFF5F5F4), // stone-100
            height: 1.0,
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 1. Identitas Personal
            _buildSectionTitle('Identitas Personal'),
            const SizedBox(height: 12),
            _buildLabel('Nama Lengkap'),
            const SizedBox(height: 8),
            _buildTextField(
              hint: 'Masukkan nama lengkap',
              onChanged: (val) => controller.namaLengkap.value = val,
            ),
            const SizedBox(height: 16),
            
            _buildLabel('Umur'),
            const SizedBox(height: 8),
            _buildTextField(
              hint: 'Contoh: 75',
              keyboardType: TextInputType.number,
              onChanged: (val) => controller.umur.value = val,
            ),
            const SizedBox(height: 24),
            
            _buildLabel('Jenis Kelamin'),
            const SizedBox(height: 8),
            Row(
              children: [
                _buildToggleButton('Pria', controller.jenisKelamin),
                const SizedBox(width: 16),
                _buildToggleButton('Wanita', controller.jenisKelamin),
              ],
            ),
            
            const SizedBox(height: 32),
            const Divider(color: Color(0xFFE5E7EB)), // outline-variant/30 ~ stone-200
            const SizedBox(height: 16),

            // 2. Kesehatan & Mobilitas Section
            _buildSectionTitle('Kesehatan & Mobilitas'),
            const SizedBox(height: 12),
            
            _buildLabel('Riwayat Medis'),
            const SizedBox(height: 8),
            _buildTextField(
              hint: 'Sebutkan riwayat penyakit, alergi, atau catatan medis penting...',
              maxLines: 3,
              onChanged: (val) => controller.riwayatMedis.value = val,
            ),
            const SizedBox(height: 24),
            
            _buildLabel('Kondisi Fisik'),
            const SizedBox(height: 8),
            Row(
              children: [
                _buildToggleButton('Mandiri', controller.kondisiFisik),
                const SizedBox(width: 16),
                _buildToggleButton('Bantuan', controller.kondisiFisik),
              ],
            ),
            const SizedBox(height: 24),
            
            _buildLabel('Mobilitas'),
            const SizedBox(height: 8),
            Row(
              children: [
                _buildToggleButton('Berjalan', controller.mobilitas),
                const SizedBox(width: 16),
                _buildToggleButton('Kursi Roda', controller.mobilitas),
              ],
            ),
            
            const SizedBox(height: 32),
            const Divider(color: Color(0xFFE5E7EB)),
            const SizedBox(height: 16),

            // 3. Personal Section
            _buildSectionTitle('Personal'),
            const SizedBox(height: 12),
            
            _buildLabel('Minat & Hobi'),
            const SizedBox(height: 8),
            _buildTextField(
              hint: 'Aktivitas yang disukai, kebiasaan, dll...',
              maxLines: 3,
              onChanged: (val) => controller.minatHobi.value = val,
            ),
            
            const SizedBox(height: 48),

            // Footer Actions
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextButton(
                  onPressed: () => Get.back(),
                  style: TextButton.styleFrom(
                    foregroundColor: const Color(0xFF7E7576),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text(
                    'Batal',
                    style: TextStyle(
                      fontFamily: 'Plus Jakarta Sans',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: controller.simpan,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF000000), // primary
                    foregroundColor: const Color(0xFFFFFFFF),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    elevation: 2,
                  ),
                  child: const Text(
                    'Simpan',
                    style: TextStyle(
                      fontFamily: 'Plus Jakarta Sans',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontFamily: 'Plus Jakarta Sans',
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: Color(0xFF4C4546), // on-surface-variant
      ),
    );
  }

  Widget _buildLabel(String text) {
    return Text(
      text,
      style: const TextStyle(
        fontFamily: 'Plus Jakarta Sans',
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: Color(0xFF1B1B1B), // on-background
      ),
    );
  }

  Widget _buildTextField({
    required String hint,
    int maxLines = 1,
    TextInputType keyboardType = TextInputType.text,
    required Function(String) onChanged,
  }) {
    return TextFormField(
      maxLines: maxLines,
      keyboardType: keyboardType,
      onChanged: onChanged,
      style: const TextStyle(
        fontFamily: 'Plus Jakarta Sans',
        fontSize: 16,
        color: Color(0xFF1B1B1B),
      ),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(
          color: Color(0xFF9CA3AF), // stone-400
        ),
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Color(0xFFE7E5E4)), // stone-200
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Color(0xFFE7E5E4)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Color(0xFFD6D3D1)), // stone-300
        ),
      ),
    );
  }

  Widget _buildToggleButton(String title, RxString groupValue) {
    return Expanded(
      child: Obx(() {
        final isSelected = groupValue.value == title;
        return GestureDetector(
          onTap: () => groupValue.value = title,
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 14),
            decoration: BoxDecoration(
              color: isSelected ? const Color(0xFFD3E5CE) : Colors.transparent, // secondary-container
              border: Border.all(
                color: isSelected ? Colors.transparent : const Color(0xFFE7E5E4), // stone-200
              ),
              borderRadius: BorderRadius.circular(30),
            ),
            alignment: Alignment.center,
            child: Text(
              title,
              style: TextStyle(
                fontFamily: 'Plus Jakarta Sans',
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: isSelected ? const Color(0xFF576755) : const Color(0xFF78716C), // stone-500
              ),
            ),
          ),
        );
      }),
    );
  }
}
