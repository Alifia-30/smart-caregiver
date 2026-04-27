# Smart Caregiver Server

Backend FastAPI untuk aplikasi Smart Caregiver, dideploy menggunakan Cloudflare Workers (Pyodide).

## 🚀 Quick Start

### 1. Setup Environment
Salin file `.env.example` ke `.env` dan isi variabel yang diperlukan (terutama `DATABASE_URL` dari Neon PostgreSQL).
```bash
cp .env.example .env
```
*Pastikan DATABASE_URL menggunakan prefix `postgresql+asyncpg://`*

### 2. Install Dependencies

**Menggunakan uv (Direkomendasikan):**
```bash
uv sync
```

**Menggunakan pip:**
```bash
pip install .
```

### 3. Database Migration
Jalankan migrasi untuk membuat tabel di database:
```bash
# Menggunakan uv
uv run alembic upgrade head

# Menggunakan python biasa
alembic upgrade head
```

---

## 🛠 Development

### Menjalankan Server Lokal
Server akan berjalan di `http://localhost:8000`.

**Menggunakan Bun (NPM scripts):**
```bash
bun run dev:local
```

**Menggunakan uv/python langsung:**
```bash
uv run uvicorn src.main:app --reload
```

### Membuat Migrasi Baru
Jika Anda mengubah model di `src/database/models/`, buat migrasi baru:
```bash
uv run alembic revision --autogenerate -m "nama_perubahan"
uv run alembic upgrade head
```

---

## 🌐 Deployment
Project ini siap dideploy ke Cloudflare Workers.

```bash
bun run deploy
# atau
uv run pywrangler deploy
```

## 📂 Struktur Folder Utama
- `src/main.py`: Entry point aplikasi.
- `src/app/`: Logic aplikasi (routers, services, core).
- `src/database/`: Schema database dan model SQLAlchemy.
- `migrations/`: Script migrasi database (Alembic).
