# Smart Caregiver Server

Backend FastAPI untuk aplikasi Smart Caregiver - sistem monitoring dan perawatan lansia.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy)
- **Migration**: Alembic
- **Authentication**: JWT + Google OAuth
- **Additional**: Fuzzy Logic System untuk risk analysis

## Fitur API

| Endpoint | Deskripsi |
|----------|-----------|
| `/auth` | Authentication (register, login, JWT) |
| `/auth/google` | Google OAuth login |
| `/elderly` | CRUD data lansia |
| `/health` | Data kesehatan & rekomendasi |
| `/dashboard` | Analytics & overview |
| `/viewer` | Real-time monitoring |
| `/notification` | Sistem notifikasi |

## Fuzzy Logic System

Sistem menggunakan fuzzy logic untuk analisis risiko kesehatan:
- **Metabolic Risk**: Analisis risiko metabolik
- **Cardiovascular Risk**: Analisis risiko cardiovascular
- **Infection Risk**: Analisis risiko infeksi

## 🚀 Quick Start

### 1. Setup Environment
Salin file `.env.example` ke `.env` dan isi variabel yang diperlukan.
```bash
cp .env.example .env
```

### 2. Instalasi
Buat virtual environment dan install dependensi:
```bash
python -m venv .venv
source .venv/bin/activate  # Untuk Mac/Linux
# atau
.venv\Scripts\activate     # Untuk Windows

pip install -r requirements.txt
```

### 3. Database Migration
Jalankan migrasi untuk membuat tabel di database:
```bash
alembic upgrade head
```

---

## 🛠 Development

### Menjalankan Server Lokal
Server akan berjalan di `http://localhost:8000`.
```bash
uvicorn src.main:app --reload
```

### Membuat Migrasi Baru
Jika Anda mengubah model di `src/database/models/`, buat migrasi baru:
```bash
alembic revision --autogenerate -m "nama_perubahan"
alembic upgrade head
```

## 📂 Struktur Folder

```
src/
├── main.py              # Entry point aplikasi
├── app/
│   ├── routers/         # API endpoints
│   │   ├── auth.py
│   │   ├── auth_google.py
│   │   ├── elderly.py
│   │   ├── health.py
│   │   ├── dashboard.py
│   │   ├── viewer.py
│   │   └── notification.py
│   ├── services/        # Business logic
│   ├── schemas/         # Pydantic models
│   └── core/            # Config, security, fuzzy logic
│       └── fuzzy/       # Fuzzy logic engine
│           ├── metabolic.py
│           ├── cardiovascular.py
│           └── infection.py
└── database/
    ├── models/          # SQLAlchemy models
    │   ├── user.py
    │   ├── elderly.py
    │   ├── health.py
    │   ├── schedule.py
    │   ├── notification.py
    │   └── recommendation.py
    ├── session.py
    └── init_db.py
migrations/              # Alembic migrations
```

## 📄 API Documentation

Setelah server berjalan, akses dokumentasi API di:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc