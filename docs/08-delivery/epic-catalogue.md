# Epic & Story Delivery Catalogue (Jira DBX)

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/DeliveryDocs | `docs/00-governance/project-charter.md`<br>`docs/02-requirements/srs.md`<br>`docs/02-requirements/traceability/traceability-matrix.md` |

---

## 1. Daftar 14 Epic Kanonikal DomiBox (Project Key: DBX)

| ID Epic | Kunci Jira Usulan | Nama Epic | Deskripsi Singkat | Prioritas |
| :--- | :--- | :--- | :--- | :---: |
| `EPIC-01` | `DBX-1` | Domain & DNS Management | Registrasi domain kustom, validasi MX/TXT Cloudflare, isolasi subdomain. | High (P1) |
| `EPIC-02` | `DBX-3` | Mailbox Lifecycle Engine | Pembuatan mailbox acak/kustom, TTL expiry, perpanjangan, konversi permanen. | High (P1) |
| `EPIC-03` | `DBX-4` | Inbound Mail Pipeline | Penerimaan SMTP port 25, penguraian MIME RFC822, penyimpanan raw EML. | High (P1) |
| `EPIC-04` | `DBX-5` | OTP & Link Extraction | Deteksi regex cerdas kode verifikasi/OTP dan tautan aktivasi instan. | High (P1) |
| `EPIC-05` | `DBX-6` | Web Dashboard Application | Single Page App (React + Vite + shadcn) untuk inbox, pratinjau, dan kontrol. | High (P1) |
| `EPIC-06` | `DBX-7` | Telegram Bot Channel | Bot interaktif (grammY) untuk notifikasi instan, salin OTP, dan manajemen cepat. | High (P1) |
| `EPIC-07` | `DBX-8` | Security & HTML Sanitization | Sanitasi DOMPurify, isolasi iframe, proteksi WebAuthn/TOTP, rate limiting. | High (P1) |
| `EPIC-08` | `DBX-9` | Background Jobs & Auto-Purge | Penjadwal TTL expiry, pembersihan data kedaluwarsa, rekonsiliasi state alias. | High (P1) |
| `EPIC-09` | `DBX-10` | Observability & Audit Trail | Logging terstruktur pino, metrik sistem, jejak audit aktivitas pemilik. | Medium (P2) |
| `EPIC-10` | `DBX-11` | Docker & VPS Deployment | Docker Compose, reverse proxy TLS Caddy, konfigurasi UFW port 25. | High (P1) |
| `EPIC-11` | `DBX-12` | Automated Testing Suite | Unit test Vitest, integrasi Supertest, E2E Playwright. | Medium (P2) |
| `EPIC-12` | `DBX-13` | Technical Spikes & Feasibility | Validasi port 25 inbound Tencent, PoC benchmark RAM Stalwart pada VPS. | High (P1) |
| `EPIC-13` | `DBX-14` | Documentation & Governance | Penataan spesifikasi SRS, OpenAPI, ADR, panduan kontribusi repositori. | High (P1) |
| `EPIC-14` | `DBX-15` | Release & Cutover Management | Checklist kesiapan rilis MVP, skenario rollback, uji penerimaan pemilik. | Medium (P2) |


## 2. Katalog User Story MVP Pokok (Format Gherkin AC) — LEGACY NUMBERING SUPERSEDED

> **LEGACY NUMBERING SUPERSEDED** — `US-001`..`US-006` below are historical catalogue labels only.
> Canonical Jira-side IDs: `US-001 → US-017` (DBX-29), `US-002 → US-005` (DBX-17), `US-003 → US-018` (DBX-30), `US-004 → US-019` (DBX-31), `US-005 → US-009` (DBX-21), `US-006 → US-007` (DBX-19). Original text below preserved verbatim; do not treat these labels as canonical.
>
> | Legacy ID | Status | Canonical ID | Jira key | Notes |
> | --- | --- | --- | --- | --- |
> | US-001 | SUPERSEDED | US-017 | DBX-29 | Mailbox creation — mailbox-lifecycle scope (EPIC-02). Created 2026-11-16, parent Epic DBX-3 (EPIC-02) |
> | US-002 | SUPERSEDED | US-005 | DBX-17 | Semantic overlap with Jira "US-005 — Ekstraksi OTP & Tautan Aktivasi" |
> | US-003 | SUPERSEDED | US-018 | DBX-30 | Temp→permanent conversion — mailbox-lifecycle scope (EPIC-02). Created 2026-11-16, parent Epic DBX-3 (EPIC-02) |
> | US-004 | SUPERSEDED | US-019 | DBX-31 | Cloudflare Email Routing conflict handling — distinct missing story. Created 2026-11-16, parent Epic DBX-1 (EPIC-01). Kept as Story for user-visible onboarding/AC traceability |
> | US-005 | SUPERSEDED | US-009 | DBX-21 | Semantic overlap with Jira "US-009 — Auto-Purge & Cleanup Job Terjadwal" |
> | US-006 | SUPERSEDED | US-007 | DBX-19 | Semantic overlap with Jira "US-007 — Notifikasi Telegram Instan & Salin OTP" |

## 3. Katalog User Story MVP Pokok (Format Gherkin AC)

### US-001: Pembuatan Mailbox Sementara Cepat
- **Sebagai** Pemilik Platform DomiBox,
- **Saya ingin** membuat alamat email sementara acak dalam satu klik,
- **Agar** saya dapat menggunakannya langsung untuk pendaftaran akun tanpa mengekspos email utama.
- **Kriteria Penerimaan (Gherkin):**
  ```gherkin
  Skenario: Pembuatan temporary mailbox acak sukses
    Ketika pengguna menekan tombol "Generate Mailbox Acak" di Web Dashboard atau Telegram
    Maka sistem membuat alamat email baru dengan domain aktif default
    Dan alias terdaftar secara otomatis di engine Stalwart via JMAP
    Dan masa aktif diatur selama 60 menit secara default
    Dan alamat email disalin otomatis ke clipboard pengguna
  ```

### US-002: Ekstraksi Kode OTP Otomatis
- **Sebagai** Pengguna Platform DomiBox,
- **Saya ingin** kode verifikasi OTP diekstraksi dan disorot secara jelas saat email tiba,
- **Agar** saya tidak perlu membaca seluruh isi pesan email yang panjang.
- **Kriteria Penerimaan (Gherkin):**
  ```gherkin
  Skenario: Ekstraksi OTP berhasil dari email masuk
    Ketika email masuk diterima untuk mailbox aktif yang memuat kode verifikasi 6-digit
    Maka sistem memproses teks pesan menggunakan pola regex ekstraksi OTP
    Dan kode OTP ditampilkan pada kartu ringkasan pesan dengan tombol "Salin Kode"
    Dan bot Telegram mengirimkan notifikasi instan yang mencantumkan kode OTP tersebut
  ```

### US-003: Konversi Mailbox Sementara ke Permanen
- **Sebagai** Pemilik Platform DomiBox,
- **Saya ingin** mengonversi mailbox sementara yang aktif menjadi mailbox permanen,
- **Agar** saya tidak kehilangan akses email penting atau akun layanan yang membutuhkan retensi jangka panjang.
- **Kriteria Penerimaan (Gherkin AC):**
  - **Given** sebuah mailbox sementara berstatus `ACTIVE` dengan masa kedaluwarsa tertentu (`expires_at`),
  - **When** pemilik memanggil aksi konversi permanen (`MBX-003`),
  - **Then** sistem mengubah nilai `expires_at` menjadi `NULL`, mengubah penanda `is_permanent` menjadi `true`, dan menetapkan kuota penyimpanan persisten maksimal 100 MB.

### US-004: Penanganan Konflik Cloudflare Email Routing
- **Sebagai** Pemilik Platform DomiBox,
- **Saya ingin** sistem mendeteksi keberadaan rekaman MX Cloudflare Email Routing saat pendaftaran domain,
- **Agar** saya mendapatkan panduan konfigurasi subdomain yang tepat tanpa merusak layanan email yang sudah berjalan (`F3`).
- **Kriteria Penerimaan (Gherkin AC):**
  - **Given** domain yang didaftarkan memiliki rekaman DNS MX mengarah ke `route*.mx.cloudflare.net`,
  - **When** sistem menjalankan verifikasi DNS (`DOM-003`),
  - **Then** status domain ditandai sebagai `CONFLICT_CLOUDFLARE_ROUTING`, aktivasi ditahan, dan panduan penggunaan subdomain (mis. `mail.domain.com`) disajikan ke antarmuka pengguna.

### US-005: Pembersihan Otomatis Mailbox Kedaluwarsa (Auto-Purge)
- **Sebagai** Pemilik Platform DomiBox,
- **Saya ingin** mailbox dan pesan email yang telah melewati batas TTL dihapus secara otomatis dan tuntas,
- **Agar** kapasitas penyimpanan VPS berdaya hemat tetap aman dari kehabisan memori dan disk (`F4`, `NFR-008`).
- **Kriteria Penerimaan (Gherkin AC):**
  - **Given** terdapat sejumlah mailbox sementara dengan `expires_at < NOW()` dan pesan email terkait,
  - **When** scheduler pembersihan latar belakang berjalan pada interval 60 detik (`MBX-005`, `OPS-002`),
  - **Then** data pesan email dihapus dari basis data dan engine email, mailbox ditandai `PURGED`, dan jejak audit pembersihan dicatat tanpa mengunci tabel utama melebihi 2 detik.

### US-006: Notifikasi & Ekstraksi OTP Instan via Telegram Bot
- **Sebagai** Pemilik Platform DomiBox,
- **Saya ingin** menerima notifikasi push kode OTP langsung di Telegram beserta tombol salin satu-klik,
- **Agar** saya dapat menyelesaikan verifikasi login atau registrasi secara instan dari perangkat seluler (`BOT-003`, `OTP-005`).
- **Kriteria Penerimaan (Gherkin AC):**
  - **Given** akun Telegram pemilik telah tertaut melalui pairing token valid (`BOT-001`),
  - **When** email verifikasi baru yang memuat kode OTP masuk ke salah satu mailbox aktif,
  - **Then** bot Telegram mengirimkan pesan notifikasi dalam waktu < 2 detik berisi pengirim, subjek, kode OTP yang diperbesar, dan tombol inline "Salin OTP".
