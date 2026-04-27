# Smart Caregiver Server

Backend FastAPI untuk aplikasi Smart Caregiver.

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

## 📂 Struktur Folder Utama
- `src/main.py`: Entry point aplikasi.
- `src/app/`: Logic aplikasi (routers, services, core).
- `src/database/`: Schema database dan model SQLAlchemy.
- `migrations/`: Script migrasi database (Alembic).
