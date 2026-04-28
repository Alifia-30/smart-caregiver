import 'package:get/get.dart';
import '../providers/api_provider.dart';
import '../models/vital_model.dart';

class VitalRepository {
  final ApiProvider _api = Get.find<ApiProvider>();

  Future<List<Vital>> fetchVitals(int patientId) async {
    final res = await _api.getVitals(patientId);
    if (res.statusCode == 200) {
      final List data = res.body as List;
      return data.map((e) => Vital.fromJson(e)).toList();
    }
    throw Exception('Failed to load vitals');
  }

  Future<Vital> addVital(int patientId, Map<String, dynamic> body) async {
    final res = await _api.addVital(patientId, body);
    if (res.statusCode == 200 || res.statusCode == 201) {
      return Vital.fromJson(res.body);
    }
    throw Exception('Failed to save vital');
  }

  Future<Map<String, dynamic>> analyzeHealth(int patientId) async {
    final res = await Get.find<ApiProvider>().analyzeHealth(patientId);
    if (res.statusCode == 200) return res.body as Map<String, dynamic>;
    throw Exception('Failed to analyze health');
  }
}
