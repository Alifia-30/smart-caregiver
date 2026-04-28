class Patient {
  final int? id;
  final String name;
  final int age;
  final String? address;
  final String? phone;
  final String? bloodType;
  final String? gender;
  final String? profilePhoto;
  final String? physicalCondition;
  final String? mobilityLevel;
  final String? medicalHistory;
  final String? allergies;
  final String? hobbies;
  final String? notes;
  final String? avatarInitial;

  Patient({
    this.id,
    required this.name,
    required this.age,
    this.address,
    this.phone,
    this.bloodType,
    this.gender,
    this.profilePhoto,
    this.physicalCondition,
    this.mobilityLevel,
    this.medicalHistory,
    this.allergies,
    this.hobbies,
    this.notes,
    this.avatarInitial,
  });

  factory Patient.fromJson(Map<String, dynamic> json) {
    return Patient(
      id: json['id'],
      name: json['name'] ?? '',
      age: json['age'] ?? 0,
      address: json['address'],
      phone: json['phone'],
      bloodType: json['blood_type'],
      gender: json['gender'],
      profilePhoto: json['profile_photo'],
      physicalCondition: json['physical_condition'],
      mobilityLevel: json['mobility_level'],
      medicalHistory: json['medical_history'],
      allergies: json['allergies'],
      hobbies: json['hobbies'],
      notes: json['notes'],
      avatarInitial: json['name'] != null && (json['name'] as String).isNotEmpty
          ? (json['name'] as String)[0].toUpperCase()
          : 'P',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'age': age,
      'address': address,
      'phone': phone,
      'blood_type': bloodType,
      'gender': gender,
      'profile_photo': profilePhoto,
      'physical_condition': physicalCondition,
      'mobility_level': mobilityLevel,
      'medical_history': medicalHistory,
      'allergies': allergies,
      'hobbies': hobbies,
      'notes': notes,
    };
  }

  String get initials {
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : 'P';
  }
}
