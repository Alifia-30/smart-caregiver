import 'package:flutter/foundation.dart';
import 'package:get/get.dart';

class ApiProvider extends GetConnect {
  // Base URL — update to your FastAPI backend address
  static const String baseApiUrl = 'http://10.0.2.2:8000';

  @override
  void onInit() {
    httpClient.baseUrl = baseApiUrl;
    httpClient.defaultContentType = 'application/json';
    httpClient.timeout = const Duration(seconds: 30);

    // Response interceptor for logging
    httpClient.addResponseModifier((request, response) {
      if (kDebugMode) {
        print('API [${request.method}] ${request.url} => ${response.statusCode}');
      }
      return response;
    });

    super.onInit();
  }

  // ── Auth ──────────────────────────────────────────────
  Future<Response> login(String email, String password) =>
      post('/auth/login', {'email': email, 'password': password});

  Future<Response> register(
          String name, String email, String password) =>
      post('/auth/register',
          {'name': name, 'email': email, 'password': password});

  // ── Patients ──────────────────────────────────────────
  Future<Response> getPatients() => get('/patients/');

  Future<Response> getPatient(int id) => get('/patients/$id');

  Future<Response> createPatient(Map<String, dynamic> body) =>
      post('/patients/', body);

  Future<Response> updatePatient(int id, Map<String, dynamic> body) =>
      put('/patients/$id', body);

  Future<Response> deletePatient(int id) => delete('/patients/$id');

  // ── Vitals ────────────────────────────────────────────
  Future<Response> getVitals(int patientId) =>
      get('/patients/$patientId/vitals');

  Future<Response> addVital(int patientId, Map<String, dynamic> body) =>
      post('/patients/$patientId/vitals', body);

  // ── Health Analysis ───────────────────────────────────
  Future<Response> analyzeHealth(int patientId) =>
      get('/health-analysis/analyze/$patientId');
}
