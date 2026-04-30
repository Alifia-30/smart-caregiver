import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:google_fonts/google_fonts.dart';

import '../controllers/patient_detail_controller.dart';

class PatientDetailView extends GetView<PatientDetailController> {
  const PatientDetailView({super.key});

  @override
  Widget build(BuildContext context) {
    const Color backgroundColor = Color(0xFFF9F9F9);
    const Color primaryColor = Color(0xFF000000);
    const Color onPrimaryContainerColor = Color(0xFF848484);
    const Color secondaryContainerColor = Color(0xFFD3E5CE);
    const Color onSecondaryContainerColor = Color(0xFF576755);
    
    // Vital Colors
    const Color tdColor = Color(0xFFE9E7FD);
    const Color gulaColor = Color(0xFFFFEAD8);
    const Color suhuColor = Color(0xFFFFF8D6);

    return Scaffold(
      backgroundColor: backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            // Custom Top App Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () => Get.back(),
                    icon: const Icon(Icons.arrow_back),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                  const SizedBox(width: 16),
                  Text(
                    'Patient Details',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
                  ),
                  const Spacer(),
                  const Icon(Icons.person_outline),
                ],
              ),
            ),

            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 16),
                    // Profile Header
                    Row(
                      children: [
                        Text(
                          'Budi Santoso',
                          style: GoogleFonts.plusJakartaSans(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: primaryColor,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 4),
                          decoration: BoxDecoration(
                            color: secondaryContainerColor,
                            borderRadius: BorderRadius.circular(100),
                          ),
                          child: Text(
                            'NORMAL',
                            style: GoogleFonts.plusJakartaSans(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: onSecondaryContainerColor,
                            ),
                          ),
                        ),
                      ],
                    ),
                    Text(
                      '65 Tahun',
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 16,
                        color: onPrimaryContainerColor,
                      ),
                    ),

                    const SizedBox(height: 32),

                    // Vitals Section
                    Row(
                      children: [
                        Expanded(
                          child: _buildVitalCard(
                            label: 'TD',
                            value: '120/80',
                            unit: 'mmHg',
                            color: tdColor,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildVitalCard(
                            label: 'Gula',
                            value: '110',
                            unit: 'mg/dL',
                            color: gulaColor,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildVitalCard(
                            label: 'Suhu',
                            value: '36.5',
                            unit: '°C',
                            color: suhuColor,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 32),

                    // Health Trend Section
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 40,
                            offset: const Offset(0, 20),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Health Trend',
                                style: GoogleFonts.plusJakartaSans(
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                  color: primaryColor,
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.all(4),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFF3F3F3),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Row(
                                  children: [
                                    _buildToggleOption('7 Hari', true),
                                    _buildToggleOption('30 Hari', false),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),
                          // Chart Placeholder
                          SizedBox(
                            height: 160,
                            width: double.infinity,
                            child: CustomPaint(
                              painter: SimpleChartPainter(),
                            ),
                          ),
                          const SizedBox(height: 12),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              'Sen',
                              'Sel',
                              'Rab',
                              'Kam',
                              'Jum',
                              'Sab',
                              'Min'
                            ]
                                .map((day) => Text(
                                      day,
                                      style: GoogleFonts.plusJakartaSans(
                                        fontSize: 10,
                                        color: const Color(0xFFB4B4B4),
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ))
                                .toList(),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 32),

                    // History Section
                    Text(
                      'Riwayat Cek Kesehatan',
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: primaryColor,
                      ),
                    ),
                    const SizedBox(height: 16),
                    _buildHistoryItem(
                      day: '24',
                      month: 'OKT',
                      status: 'STABIL',
                      statusColor: secondaryContainerColor,
                      onStatusColor: onSecondaryContainerColor,
                      description:
                          'Kondisi fisik prima, tekanan darah dalam batas normal setelah istirahat.',
                    ),
                    const SizedBox(height: 12),
                    _buildHistoryItem(
                      day: '20',
                      month: 'OKT',
                      status: 'OBSERVASI',
                      statusColor: const Color(0xFFFFEAD8),
                      onStatusColor: const Color(0xFF997F6E),
                      description:
                          'Sedikit peningkatan kadar gula pagi hari, disarankan diet rendah karbo.',
                    ),
                    const SizedBox(height: 12),
                    _buildHistoryItem(
                      day: '15',
                      month: 'OKT',
                      status: 'STABIL',
                      statusColor: secondaryContainerColor,
                      onStatusColor: onSecondaryContainerColor,
                      description:
                          'Check-up rutin pasca medikasi, hasil laboratorium menunjukkan progres baik.',
                    ),
                    const SizedBox(height: 100), // Space for Bottom Nav/FAB
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: Colors.black,
        shape: const CircleBorder(),
        child: const Icon(Icons.add, color: Colors.white, size: 32),
      ),
      bottomNavigationBar: _buildBottomNavBar(),
    );
  }

  Widget _buildVitalCard({
    required String label,
    required String value,
    required String unit,
    required Color color,
  }) {
    return AspectRatio(
      aspectRatio: 1,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(24),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: GoogleFonts.plusJakartaSans(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: const Color(0xFF717171),
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.black,
                  ),
                ),
                Text(
                  unit,
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 10,
                    fontWeight: FontWeight.w500,
                    color: const Color(0xFF717171),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildToggleOption(String text, bool active) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      decoration: BoxDecoration(
        color: active ? Colors.white : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
        boxShadow: active
            ? [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ]
            : [],
      ),
      child: Text(
        text,
        style: GoogleFonts.plusJakartaSans(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: active ? Colors.black : const Color(0xFF848484),
        ),
      ),
    );
  }

  Widget _buildHistoryItem({
    required String day,
    required String month,
    required String status,
    required Color statusColor,
    required Color onStatusColor,
    required String description,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 30,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: const Color(0xFFEEEEEE),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  month,
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFFB4B4B4),
                  ),
                ),
                Text(
                  day,
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.black,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 2),
                      decoration: BoxDecoration(
                        color: statusColor,
                        borderRadius: BorderRadius.circular(100),
                      ),
                      child: Text(
                        status,
                        style: GoogleFonts.plusJakartaSans(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: onStatusColor,
                        ),
                      ),
                    ),
                    const Icon(Icons.chevron_right,
                        size: 16, color: Color(0xFFD4D4D4)),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  description,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: GoogleFonts.plusJakartaSans(
                    fontSize: 12,
                    color: const Color(0xFF848484),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }


  Widget _buildBottomNavBar() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        border: const Border(top: BorderSide(color: Color(0xFFF1F1F1))),
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildNavItem(Icons.home_filled, 'Home', true),
            _buildNavItem(Icons.favorite_outline, 'Health', false),
            _buildNavItem(Icons.calendar_today_outlined, 'Schedule', false),
          ],
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, bool active) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: active
          ? BoxDecoration(
              color: const Color(0xFFF1F1F1),
              borderRadius: BorderRadius.circular(16),
            )
          : null,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: active ? Colors.black : const Color(0xFFB4B4B4)),
          const SizedBox(height: 4),
          Text(
            label,
            style: GoogleFonts.plusJakartaSans(
              fontSize: 11,
              fontWeight: FontWeight.w500,
              color: active ? Colors.black : const Color(0xFFB4B4B4),
            ),
          ),
        ],
      ),
    );
  }
}

class SimpleChartPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final path = Path();
    path.moveTo(0, size.height * 0.875);
    path.quadraticBezierTo(
        size.width * 0.15, size.height * 0.8, size.width * 0.25, size.height * 0.625);
    path.quadraticBezierTo(
        size.width * 0.375, size.height * 0.7, size.width * 0.5, size.height * 0.7);
    path.quadraticBezierTo(
        size.width * 0.625, size.height * 0.7, size.width * 0.75, size.height * 0.375);
    path.quadraticBezierTo(
        size.width * 0.875, size.height * 0.5, size.width, size.height * 0.5);

    canvas.drawPath(path, paint);

    final dotPaint = Paint()..color = Colors.black;
    canvas.drawCircle(Offset(size.width * 0.25, size.height * 0.625), 2, dotPaint);
    canvas.drawCircle(Offset(size.width * 0.5, size.height * 0.7), 2, dotPaint);
    canvas.drawCircle(Offset(size.width * 0.75, size.height * 0.375), 2, dotPaint);
    
    // Draw grid lines
    final gridPaint = Paint()
      ..color = Colors.black.withOpacity(0.05)
      ..strokeWidth = 1;
      
    for (int i = 1; i <= 4; i++) {
      double y = size.height * i / 4;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
