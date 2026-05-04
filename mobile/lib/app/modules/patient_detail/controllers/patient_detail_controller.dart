import 'package:get/get.dart';

class PatientDetailController extends GetxController {
  final patientName = 'Budi Santoso'.obs;

  final records = [
    {
      'status': 'Normal',
      'date': '24 Okt, 08:30',
      'measurements': 'TD: 120/80 | Gula: 95',
      'notes': 'Kondisi stabil, nafsu makan baik, rutin jalan pagi...',
      'color': 0xFFD1E8D1,
      'textColor': 0xFF111F11,
    },
    {
      'status': 'Perlu Perhatian',
      'date': '21 Okt, 19:45',
      'measurements': 'TD: 145/95 | Gula: 110',
      'notes': 'Sedikit pusing di area tengkuk, kurang tidur semalam...',
      'color': 0xFFFADADD,
      'textColor': 0xFF584234,
    },
    {
      'status': 'Normal',
      'date': '18 Okt, 09:15',
      'measurements': 'TD: 118/75 | Gula: 92',
      'notes': 'Setelah kontrol ke klinik, obat dilanjutkan sesuai resep...',
      'color': 0xFFD1E8D1,
      'textColor': 0xFF111F11,
    },
    {
      'status': 'Normal',
      'date': '14 Okt, 08:20',
      'measurements': 'TD: 122/82 | Gula: 88',
      'notes': 'Kondisi sangat prima, sudah mulai rutin berenang...',
      'color': 0xFFD1E8D1,
      'textColor': 0xFF111F11,
    },
  ].obs;
}
