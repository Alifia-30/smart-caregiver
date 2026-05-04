import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:mobile/app/routes/app_pages.dart';

import '../controllers/home_controller.dart';

class HomeView extends GetView<HomeController> {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    const Color surfaceColor = Color(0xFFF9F9F9);
    const Color onSurfaceColor = Color(0xFF1B1B1B);
    const Color onSurfaceVariantColor = Color(0xFF4C4546);
    const Color primaryColor = Color(0xFF000000);
    const Color secondaryContainerColor = Color(0xFFD3E5CE);
    const Color tertiaryFixedColor = Color(0xFFFDDCC9);
    const Color outlineVariantColor = Color(0xFFCFC4C5);
    const Color secondaryColor = Color(0xFF536250);
    const Color errorColor = Color(0xFFBA1A1A);

    return Scaffold(
      backgroundColor: surfaceColor,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Custom Top App Bar
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Icon(Icons.menu, color: primaryColor, size: 28),
                    Text(
                      'CareTrack',
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: primaryColor,
                        letterSpacing: -0.5,
                      ),
                    ),
                    const Icon(
                      Icons.notifications_none_outlined,
                      color: primaryColor,
                      size: 28,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Greeting Section
              Text(
                'Halo, Sari 👋',
                style: GoogleFonts.plusJakartaSans(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: primaryColor,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Kamis, 24 Oktober 2024',
                style: GoogleFonts.plusJakartaSans(
                  fontSize: 14,
                  color: onSurfaceVariantColor,
                ),
              ),

              const SizedBox(height: 32),

              // Patients Section Title
              Text(
                'Pasien Saya',
                style: GoogleFonts.plusJakartaSans(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: primaryColor,
                ),
              ),
              const SizedBox(height: 16),

              // Patient List
              _buildPatientCard(
                name: 'Budi Santoso',
                age: '65 Tahun',
                status: 'Stabil',
                statusColor: secondaryColor,
                backgroundColor: secondaryContainerColor,
                imageUrl:
                    'https://lh3.googleusercontent.com/aida-public/AB6AXuD9F7uUGSzbuMoAMa5YJbePkhQC9M54ApZcI5t68cccbtqS-echkieElbrafbmB3orkuIPFOfBcvN8xgLvzjimUVQ0KS1zllB8aS4R05NwTbFh7m056GX7Ry-_cx_e7mN2y-YjzWxNQRVDq0zzzvDo1Mb6Lvekr6KusEyoGzT4mQPideQlwC_5fNoVE4N8vMkeVfBLpbz91pIKoLk6CBXoiH7LLHBkOEzbVDceBCoRXll9S0PSff7WPFAb2fSllmkA-zdqiq3Qvpng',
              ),
              const SizedBox(height: 16),
              _buildPatientCard(
                name: 'Siti Aminah',
                age: '72 Tahun',
                status: 'Perlu Perhatian',
                statusColor: errorColor,
                backgroundColor: tertiaryFixedColor,
                imageUrl:
                    'https://lh3.googleusercontent.com/aida-public/AB6AXuCu47Bswe-kechA7-4BxSxMADf7gHS_ezXJ5TVLfwlsT7V0fccGbMsMXm1JSEh2WnVBO7627Thd6Np2QJoX48AvLHEFA4Wv6-3TXmfPWNHHHkx8BR3TCI4DRGi0rGIdWRKXTvQ9vTJQwWqFRuYUdpXwKkyHTf1eQNZ__eDEaMs4tJf7fI1uBhgL_dptlYVjXqzncYqDibiWXBwlPV-f9CcYW7s66wQdSyTNZoP2JP9L9m171I3QKYojGiHzgU8CAD8470ds0vkfQU8',
              ),
              const SizedBox(height: 16),

              // Add Patient Button
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: const Color(0xFFF3F3F3),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: outlineVariantColor,
                    width: 2,
                    style: BorderStyle
                        .solid, // Flutter doesn't have native dashed border in BoxDecoration easily
                  ),
                ),
                child: Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: const BoxDecoration(
                        color: Color(0xFFE2E2E2),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.add, color: primaryColor),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Tambah Pasien',
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: onSurfaceColor,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPatientCard({
    required String name,
    required String age,
    required String status,
    required Color statusColor,
    required Color backgroundColor,
    required String imageUrl,
  }) {
    return GestureDetector(
      onTap: () => Get.toNamed(Routes.DASHBOARD),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.5),
                    shape: BoxShape.circle,
                    image: DecorationImage(
                      image: NetworkImage(imageUrl),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: statusColor,
                    borderRadius: BorderRadius.circular(100),
                  ),
                  child: Text(
                    status.toUpperCase(),
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      letterSpacing: 1.0,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Text(
              name,
              style: GoogleFonts.plusJakartaSans(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: const Color(0xFF000000),
              ),
            ),
            Text(
              age,
              style: GoogleFonts.plusJakartaSans(
                fontSize: 12,
                color: const Color(0xFF4C4546),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
