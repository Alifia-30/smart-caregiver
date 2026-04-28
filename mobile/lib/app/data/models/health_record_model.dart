/// Health record model aligned with server schema: health_records table.
///
/// See: server/src/database/models/health.py — HealthRecord
class HealthRecord {
  final String? id;
  final String elderlyId;
  final String? recordedBy;

  // ── Vital parameters (REQ-005) ──────────────────────────────────────────
  final double? systolicBp;       // mmHg
  final double? diastolicBp;      // mmHg
  final double? bloodSugar;       // mg/dL
  final double? heartRate;        // bpm
  final double? bodyTemperature;  // °C
  final double? bodyWeight;       // kg
  final double? cholesterol;      // mg/dL
  final double? uricAcid;         // mg/dL
  final double? spo2Level;        // %

  // ── Qualitative notes (REQ-006) ─────────────────────────────────────────
  final String? dailyNotes;
  final String? complaints;

  // ── Computed status (REQ-007) ───────────────────────────────────────────
  final HealthStatus healthStatus;

  // ── Fuzzy logic analysis scores ─────────────────────────────────────────
  final double? cardioScore;      // 0–100
  final double? metabolicScore;   // 0–100
  final double? infectionScore;   // 0–100
  final double? fuzzyFinalScore;  // 0–100

  // ── Timestamps ──────────────────────────────────────────────────────────
  final DateTime recordedAt;
  final DateTime? createdAt;

  HealthRecord({
    this.id,
    required this.elderlyId,
    this.recordedBy,
    this.systolicBp,
    this.diastolicBp,
    this.bloodSugar,
    this.heartRate,
    this.bodyTemperature,
    this.bodyWeight,
    this.cholesterol,
    this.uricAcid,
    this.spo2Level,
    this.dailyNotes,
    this.complaints,
    this.healthStatus = HealthStatus.normal,
    this.cardioScore,
    this.metabolicScore,
    this.infectionScore,
    this.fuzzyFinalScore,
    required this.recordedAt,
    this.createdAt,
  });

  factory HealthRecord.fromJson(Map<String, dynamic> json) {
    return HealthRecord(
      id: json['id'],
      elderlyId: json['elderly_id'] ?? '',
      recordedBy: json['recorded_by'],
      systolicBp: (json['systolic_bp'] as num?)?.toDouble(),
      diastolicBp: (json['diastolic_bp'] as num?)?.toDouble(),
      bloodSugar: (json['blood_sugar'] as num?)?.toDouble(),
      heartRate: (json['heart_rate'] as num?)?.toDouble(),
      bodyTemperature: (json['body_temperature'] as num?)?.toDouble(),
      bodyWeight: (json['body_weight'] as num?)?.toDouble(),
      cholesterol: (json['cholesterol'] as num?)?.toDouble(),
      uricAcid: (json['uric_acid'] as num?)?.toDouble(),
      spo2Level: (json['spo2_level'] as num?)?.toDouble(),
      dailyNotes: json['daily_notes'],
      complaints: json['complaints'],
      healthStatus: HealthStatus.fromString(json['health_status'] ?? 'normal'),
      cardioScore: (json['cardio_score'] as num?)?.toDouble(),
      metabolicScore: (json['metabolic_score'] as num?)?.toDouble(),
      infectionScore: (json['infection_score'] as num?)?.toDouble(),
      fuzzyFinalScore: (json['fuzzy_final_score'] as num?)?.toDouble(),
      recordedAt: json['recorded_at'] != null
          ? DateTime.parse(json['recorded_at'])
          : DateTime.now(),
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        if (id != null) 'id': id,
        'elderly_id': elderlyId,
        if (recordedBy != null) 'recorded_by': recordedBy,
        'systolic_bp': systolicBp,
        'diastolic_bp': diastolicBp,
        'blood_sugar': bloodSugar,
        'heart_rate': heartRate,
        'body_temperature': bodyTemperature,
        'body_weight': bodyWeight,
        'cholesterol': cholesterol,
        'uric_acid': uricAcid,
        'spo2_level': spo2Level,
        'daily_notes': dailyNotes,
        'complaints': complaints,
        'health_status': healthStatus.value,
        'recorded_at': recordedAt.toIso8601String(),
      };

  HealthRecord copyWith({
    String? id,
    String? elderlyId,
    String? recordedBy,
    double? systolicBp,
    double? diastolicBp,
    double? bloodSugar,
    double? heartRate,
    double? bodyTemperature,
    double? bodyWeight,
    double? cholesterol,
    double? uricAcid,
    double? spo2Level,
    String? dailyNotes,
    String? complaints,
    HealthStatus? healthStatus,
    double? cardioScore,
    double? metabolicScore,
    double? infectionScore,
    double? fuzzyFinalScore,
    DateTime? recordedAt,
    DateTime? createdAt,
  }) {
    return HealthRecord(
      id: id ?? this.id,
      elderlyId: elderlyId ?? this.elderlyId,
      recordedBy: recordedBy ?? this.recordedBy,
      systolicBp: systolicBp ?? this.systolicBp,
      diastolicBp: diastolicBp ?? this.diastolicBp,
      bloodSugar: bloodSugar ?? this.bloodSugar,
      heartRate: heartRate ?? this.heartRate,
      bodyTemperature: bodyTemperature ?? this.bodyTemperature,
      bodyWeight: bodyWeight ?? this.bodyWeight,
      cholesterol: cholesterol ?? this.cholesterol,
      uricAcid: uricAcid ?? this.uricAcid,
      spo2Level: spo2Level ?? this.spo2Level,
      dailyNotes: dailyNotes ?? this.dailyNotes,
      complaints: complaints ?? this.complaints,
      healthStatus: healthStatus ?? this.healthStatus,
      cardioScore: cardioScore ?? this.cardioScore,
      metabolicScore: metabolicScore ?? this.metabolicScore,
      infectionScore: infectionScore ?? this.infectionScore,
      fuzzyFinalScore: fuzzyFinalScore ?? this.fuzzyFinalScore,
      recordedAt: recordedAt ?? this.recordedAt,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

/// Matches server enum: HealthStatus
enum HealthStatus {
  normal('normal'),
  warning('warning'),
  needsAttention('needs_attention'),
  critical('critical');

  const HealthStatus(this.value);
  final String value;

  static HealthStatus fromString(String value) {
    return HealthStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => HealthStatus.normal,
    );
  }

  String get label {
    switch (this) {
      case HealthStatus.normal:
        return 'Normal';
      case HealthStatus.warning:
        return 'Warning';
      case HealthStatus.needsAttention:
        return 'Attention';
      case HealthStatus.critical:
        return 'Critical';
    }
  }
}
