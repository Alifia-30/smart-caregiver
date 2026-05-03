# Smart Caregiver Mobile

Flutter application untuk caregiver dalam memonitor dan merawat lansia.

## Tech Stack

- **Framework**: Flutter 3.9+
- **State Management**: GetX
- **Local Storage**: GetStorage
- **Typography**: Google Fonts
- **UI**: Material Design

## Fitur App

| Module | Deskripsi |
|--------|-----------|
| Splash | Initialisasi app, loading screen |
| Home | Dashboard utama untuk caregiver |
| Patient Detail | Detail informasi & data lansia |

## Struktur GetX Pattern

Setiap module terdiri dari:
- `controllers/` - Logic & state management
- `views/` - UI screens
- `bindings/` - Dependency injection

## 🚀 Quick Start

### Prerequisites
- Flutter SDK 3.9+
- Dart 3.9+

### Instalasi
```bash
cd mobile
flutter pub get
```

### Menjalankan App
```bash
flutter run
```

Untuk mode development dengan hot reload:
```bash
flutter run -d <device_id>
```

### Build APK
```bash
flutter build apk --debug
# atau
flutter build apk --release
```

## 📂 Struktur Folder

```
lib/
├── main.dart                    # Entry point
└── app/
    ├── routes/
    │   ├── app_routes.dart      # Route definitions
    │   └── app_pages.dart       # Page configurations
    └── modules/
        ├── splash/
        │   ├── controllers/
        │   ├── views/
        │   └── bindings/
        ├── home/
        │   ├── controllers/
        │   ├── views/
        │   └── bindings/
        └── patient_detail/
            ├── controllers/
            ├── views/
            └── bindings/
```

## Konfigurasi

Sesuaikan API base URL di `lib/app/core/config.dart` sesuai environment:

- **Development**: `http://localhost:8000`
- **Production**: URL server production