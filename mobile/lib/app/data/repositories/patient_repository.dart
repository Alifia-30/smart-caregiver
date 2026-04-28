import 'package:get/get.dart';
import '../providers/api_provider.dart';
import '../models/patient_model.dart';

class PatientRepository {
  final ApiProvider _api = Get.find<ApiProvider>();

  Future<List<Patient>> fetchAll() async {
    final res = await _api.getPatients();
    if (res.statusCode == 200) {
      final List data = res.body as List;
      return data.map((e) => Patient.fromJson(e)).toList();
    }
    throw Exception('Failed to load patients: ${res.statusCode}');
  }

  Future<Patient> fetchOne(int id) async {
    final res = await _api.getPatient(id);
    if (res.statusCode == 200) return Patient.fromJson(res.body);
    throw Exception('Patient not found');
  }

  Future<Patient> create(Map<String, dynamic> body) async {
    final res = await _api.createPatient(body);
    if (res.statusCode == 200 || res.statusCode == 201) {
      return Patient.fromJson(res.body);
    }
    throw Exception('Failed to create patient');
  }

  Future<bool> delete(int id) async {
    final res = await _api.deletePatient(id);
    return res.statusCode == 200 || res.statusCode == 204;
  }
}
