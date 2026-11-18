# REST API Architecture & Endpoint Specification — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/TechSpec | `docs/04-technical/api/openapi.yaml`<br>`docs/04-technical/error-catalogue.md`<br>`docs/02-requirements/srs.md` |

---

## 1. Standar Desain REST API
API DomiBox mengikuti konvensi RESTful dengan format serialisasi JSON UTF-8. Seluruh endpoint publik dan privat didefinisikan secara formal dalam kontrak **OpenAPI 3.1.0** pada `docs/04-technical/api/openapi.yaml`.

---

## 2. Ringkasan Endpoint Utama (Endpoint Matrix)

| Kategori | Metode | Path | Hak Akses | Deskripsi & Perilaku Sistem |
| --- | :---: | --- | :---: | --- |
| **Auth** | `POST` | `/api/v1/auth/login` | Publik | Otentikasi username/password pemilik + TOTP (`SEC-001`). |
| **Domain** | `POST` | `/api/v1/domains` | Admin | Mendaftarkan domain kustom baru (`DOM-001`). |
| **Domain** | `GET` | `/api/v1/domains` | Admin | Mengambil daftar domain terdaftar dan status verifikasi. |
| **Domain** | `POST` | `/api/v1/domains/{id}/verify` | Admin | Memeriksa rekaman DNS TXT dan MX secara on-demand (`DOM-002`). |
| **Mailbox** | `POST` | `/api/v1/mailboxes/temporary` | Publik/Admin | Membuat mailbox sementara baru dengan TTL tertentu (`MBX-001`). |
| **Mailbox** | `GET` | `/api/v1/mailboxes/{id}/messages`| Token Mailbox | Mengambil daftar email yang masuk ke mailbox (`INB-004`). |
| **Mailbox** | `POST` | `/api/v1/mailboxes/{id}/convert` | Admin | Mengonversi mailbox sementara menjadi permanen (`MBX-003`). |
| **Mailbox** | `DELETE`| `/api/v1/mailboxes/{id}` | Token Mailbox | Menghapus mailbox seketika secara tuntas (`MBX-004`). |
| **Message** | `GET` | `/api/v1/messages/{id}` | Token Mailbox | Membaca pesan email lengkap dengan HTML tersanitasi (`INB-001`). |
| **OTP** | `GET` | `/api/v1/mailboxes/{id}/otp` | Token Mailbox | Mengambil kode OTP terbaru hasil ekstraksi cepat (`OTP-001`). |
| **Telegram**| `POST` | `/api/v1/telegram/webhook` | Internal | Endpoint webhook penerima payload obrolan Telegram (`BOT-001`). |
| **System** | `GET` | `/api/v1/health` | Publik | Status kesehatan komponen sistem (`OPS-003`). |
