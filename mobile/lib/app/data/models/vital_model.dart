class Vital {
  final int? id;
  final int patientId;
  final DateTime? recordedAt;
  final double? systolic;
  final double? diastolic;
  final double? heartRate;
  final double? temperature;
  final double? bloodSugar;
  final double? spO2;
  final String? healthStatus;
  final String? notes;

  Vital({
    this.id,
    required this.patientId,
    this.recordedAt,
    this.systolic,
    this.diastolic,
    this.heartRate,
    this.temperature,
    this.bloodSugar,
    this.spO2,
    this.healthStatus,
    this.notes,
  });

  factory Vital.fromJson(Map<String, dynamic> json) {
    return Vital(
      id: json['id'],
      patientId: json['patient_id'] ?? 0,
      recordedAt: json['recorded_at'] != null
          ? DateTime.tryParse(json['recorded_at'])
          : null,
      systolic: (json['systolic'] as num?)?.toDouble(),
      diastolic: (json['diastolic'] as num?)?.toDouble(),
      heartRate: (json['heart_rate'] as num?)?.toDouble(),
      temperature: (json['temperature'] as num?)?.toDouble(),
      bloodSugar: (json['blood_sugar'] as num?)?.toDouble(),
      spO2: (json['spo2'] as num?)?.toDouble(),
      healthStatus: json['health_status'],
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() => {
        'patient_id': patientId,
        'systolic': systolic,
        'diastolic': diastolic,
        'heart_rate': heartRate,
        'temperature': temperature,
        'blood_sugar': bloodSugar,
        'spo2': spO2,
        'notes': notes,
      };
}
