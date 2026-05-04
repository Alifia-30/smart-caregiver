import 'package:flutter/material.dart';
import 'package:get/get.dart';

class DashboardController extends GetxController {
  final currentIndex = 0.obs;

  void changePage(int index) {
    currentIndex.value = index;
  }

  final List<Map<String, dynamic>> healthMetrics = [
    {
      'color': const Color(0xFFFDDCC9),
      'icon': Icons.water_drop_outlined,
      'iconColor': const Color(0xFFE65100),
      'title': 'Kolesterol',
      'value': '180',
      'unit': 'mg/dL',
    },
    {
      'color': const Color(0xFFD6E7D0),
      'icon': Icons.bloodtype_outlined,
      'iconColor': const Color(0xFF2E7D32),
      'title': 'Tensi',
      'value': '120/80',
      'unit': 'mmHg',
    },
    {
      'color': const Color(0xFFEEEEEE),
      'icon': Icons.science_outlined,
      'iconColor': const Color(0xFF424242),
      'title': 'Asam Urat',
      'value': '5.5',
      'unit': 'mg/dL',
    },
    {
      'color': const Color(0xFFFFDAD6),
      'icon': Icons.opacity,
      'iconColor': const Color(0xFFC62828),
      'title': 'Gula Darah',
      'value': '110',
      'unit': 'mg/dL',
    },
    {
      'color': const Color(0xFFE2E2E2),
      'icon': Icons.thermostat_outlined,
      'iconColor': const Color(0xFFEF6C00),
      'title': 'Suhu',
      'value': '36.5',
      'unit': '°C',
    },
    {
      'color': const Color(0xFFFDDCC9),
      'icon': Icons.air,
      'iconColor': const Color(0xFF1565C0),
      'title': 'Saturasi',
      'value': '98',
      'unit': '%',
    },
    {
      'color': const Color(0xFFEEEEEE),
      'icon': Icons.monitor_weight_outlined,
      'iconColor': const Color(0xFF4E342E),
      'title': 'Berat Badan',
      'value': '70',
      'unit': 'kg',
    },
    {
      'color': const Color(0xFFD6E7D0),
      'icon': Icons.favorite_border,
      'iconColor': const Color(0xFFC62828),
      'title': 'Detak Jantung',
      'value': '72',
      'unit': 'bpm',
    },
  ];

  final count = 0.obs;
  @override
  void onInit() {
    super.onInit();
  }

  @override
  void onReady() {
    super.onReady();
  }

  @override
  void onClose() {
    super.onClose();
  }

  void increment() => count.value++;
}
