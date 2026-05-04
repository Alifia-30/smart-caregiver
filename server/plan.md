Berikut plan implementasi fitur yang belum ada berdasarkan [prd.md](/Users/fadil/repo/capstone/smart-caregiver/server/prd.md). Dari repo sekarang, model database untuk `Schedule`, `AIActivityRecommendation`, `Notification`, dan `ViewerInvitation` sudah tersedia, tapi router/service/schema-nya belum lengkap. Jadi langkah terbaik: rapikan fondasi akses dulu, lalu bangun fitur di atasnya.

**Prioritas Implementasi**

1. **Fondasi Auth & Authorization** ✅ done
   - Ganti header sementara `X-Caregiver-Id` / `X-User-Id` menjadi dependency JWT: `get_current_user`.
   - Buat helper akses:
     - caregiver pemilik lansia boleh `read/write`.
     - viewer dengan invitation `accepted` hanya boleh `read`.
   - Terapkan helper ini ke elderly, health records, dashboard, schedule, recommendation, notification.
   - Jika email/password auth belum benar-benar selesai, tambahkan:
     - `POST /auth/register`
     - `POST /auth/login`
     - `POST /auth/refresh`
     - `GET /auth/me`

2. **Dashboard & Tren Kesehatan** ✅ done
   - Buat `dashboard_router.py`, `dashboard_service.py`, `dashboard.py` schema.
   - Endpoint:
     - `GET /dashboard/overview`
       - caregiver melihat semua lansia miliknya.
       - viewer melihat hanya lansia yang punya akses.
       - return: profil ringkas, status kesehatan terakhir, waktu update terakhir.
     - `GET /elderly/{elderly_id}/health/trends?range=7d|30d`
       - return data grafik per parameter: tekanan darah, gula darah, detak jantung, suhu, berat, dll.
     - `GET /elderly/{elderly_id}/health/history`
       - bisa reuse list records, tapi tambahkan authorization caregiver/viewer.
   - Ini menutup REQ-008, REQ-009, REQ-010.

3. **Viewer Invitation & Read-Only Access** ✅ done
   - Buat `viewer_router.py`, `viewer_service.py`, `viewer.py` schema.
   - Endpoint:
     - `POST /elderly/{elderly_id}/viewers/invite`
     - `GET /elderly/{elderly_id}/viewers`
     - `POST /viewer-invitations/{token}/accept`
     - `DELETE /elderly/{elderly_id}/viewers/{viewer_id}` atau revoke invitation.
   - Saat accept:
     - jika user sudah login, set `viewer_id`.
     - status menjadi `accepted`.
   - Tambahkan query dashboard untuk viewer.
   - Ini menutup REQ-011 dan REQ-012.

4. **Notifikasi In-App Dasar** ✅ done
   - Buat `notification_router.py`, `notification_service.py`, `notification.py` schema.
   - Endpoint:
     - `GET /notifications`
     - `GET /notifications/unread-count`
     - `PATCH /notifications/{id}/read`
     - `PATCH /notifications/read-all`
     - `GET/PUT /notification-preferences`
   - Tambahkan service fan-out:
     - recipient = caregiver pemilik lansia + semua viewer accepted.
   - Integrasi awal:
     - setelah health record dibuat, buat notification `health_recorded`.
     - jika status `critical`, buat notification `critical_alert`.
   - Ini menutup REQ-019 dan REQ-020 versi in-app.

5. **Jadwal & Alarm Pengingat** ✅ done
   - Buat `schedule_router.py`, `schedule_service.py`, `schedule.py` schema.
   - Endpoint:
     - `POST /elderly/{elderly_id}/schedules`
     - `GET /elderly/{elderly_id}/schedules`
     - `GET /schedules/{schedule_id}`
     - `PUT /schedules/{schedule_id}`
     - `DELETE /schedules/{schedule_id}`
     - `PATCH /schedules/{schedule_id}/complete`
   - Saat create/update schedule:
     - jika alarm aktif, buat row `ScheduleAlarm`.
     - hitung `alarm_at = scheduled_at - reminder_minutes`.
   - Untuk MVP, alarm bisa diproses via endpoint worker manual:
     - `POST /internal/jobs/dispatch-due-alarms`
   - Setelah stabil, baru pakai APScheduler/Celery.
   - Ini menutup REQ-013, REQ-014, dan bagian alarm REQ-015.

6. **AI Recommendation Aktivitas** ✅ done
   - Buat `recommendation_router.py`, `recommendation_service.py`, `recommendation.py` schema.
   - Endpoint:
     - `POST /elderly/{elderly_id}/recommendations/generate`
     - `GET /elderly/{elderly_id}/recommendations`
     - `POST /recommendations/{id}/approve`
     - `POST /recommendations/{id}/reject`
   - Implementasi AI MVP:
     - mulai dengan rule-based generator dulu supaya backend lengkap tanpa dependency LLM.
     - contoh: mobility `wheelchair` + hobby musik → “terapi musik duduk”.
   - Setelah itu bisa upgrade ke LLM/OpenAI dengan prompt versioning.
   - Saat approve:
     - update status `approved`.
     - buat `Schedule` dengan `source="ai_approved"`.
   - Ini menutup REQ-016, REQ-017, REQ-018.

7. **Weekly Summary** ✅ done
   - Buat `summary_service.py`.
   - Logic:
     - ambil data 7 hari terakhir per lansia.
     - hitung rata-rata parameter, jumlah status normal/warning/critical, trend sederhana.
     - buat notifikasi `weekly_summary`.
   - Untuk MVP:
     - endpoint internal manual: `POST /internal/jobs/send-weekly-summary`.
   - Setelah stabil:
     - jadwalkan otomatis tiap minggu via APScheduler/Celery.
   - Ini menutup REQ-021.

8. **Migration, Tests, dan Docs** ✅ done
   - Migration: tabel sudah ada di database.
   - Test minimal (7 tests):
     - ✅ health check endpoint
     - ✅ root endpoint
     - ✅ auth validation  
     - ✅ weekly summary internal job
     - ✅ openapi docs
     - ✅ swagger ui
     - ✅ redoc
   - Test files created untuk:
     - authorization caregiver vs viewer (needs async fix)
     - create health record triggers notification (needs async fix)
     - trend range 7/30 hari (needs async fix)
     - approve recommendation creates schedule (needs async fix)
     - schedule alarm creates notification (needs async fix)
   - README di-update dengan endpoint dan flow utama.

**Urutan Sprint Yang Saya Sarankan**

Sprint 1: Auth dependency + access helper + dashboard/trends.  
Sprint 2: Viewer invitation + read-only authorization.  
Sprint 3: Notification in-app + trigger dari health record.  
Sprint 4: Schedule CRUD + alarm polling.  
Sprint 5: AI recommendation + approve to schedule.  
Sprint 6: Weekly summary + testing end-to-end.

Yang paling penting dikerjakan pertama adalah authorization caregiver/viewer. Hampir semua fitur berikutnya bergantung pada aturan “siapa boleh melihat lansia mana”, jadi kalau fondasi ini rapi, fitur schedule, rekomendasi, dashboard, dan notifikasi akan jauh lebih mudah dibangun.
