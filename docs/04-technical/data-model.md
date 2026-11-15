# Data Model & Storage Specification — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/TechSpec | `docs/04-technical/database-schema.md`<br>`docs/03-architecture/adr/ADR-005.md`<br>`docs/02-requirements/srs.md` |

---

## 1. Ikhtisar Model Data
Dokumen spesifikasi model data ini mendefinisikan struktur entitas logis dan fisik untuk platform **DomiBox**, melengkapi `docs/04-technical/database-schema.md`. Sistem menggunakan **PostgreSQL 16** sebagai penyimpanan relasional utama dengan Drizzle ORM / Kysely untuk manajemen migrasi dan pengetikan tipe aman (*type-safe*).

---

## 2. Definisi Entitas Inti (Core Entities)

### 2.1 `User` (Pemilik Tunggal)
Menyimpan kredensial autentikasi pemilik platform (*single-owner*).
- `id` (UUIDv7, PK): Identifikator unik pengguna.
- `username` (VARCHAR(64), UK): Username login administratif.
- `password_hash` (TEXT): Hash sandi menggunakan Argon2id (`SEC-001`).
- `totp_secret` (TEXT, Nullable): Kunci rahasia TOTP terenkripsi AES-256-GCM untuk 2FA.
- `role` (VARCHAR(16)): Peran hak akses (default: `'OWNER'`).
- `created_at`, `updated_at` (TIMESTAMPTZ).

### 2.2 `Domain`
Mewakili domain kustom yang didaftarkan ke platform DomiBox (`DOM-001` s/d `DOM-005`).
- `id` (UUIDv7, PK): Identifikator unik domain.
- `domain_name` (VARCHAR(255), UK): Nama FQDN domain (mis. `sintaksis.biz.id`).
- `verification_token` (VARCHAR(64)): Token unik TXT acak 32-karakter (`domibox-verify=<token>`).
- `mx_status` (VARCHAR(32)): Status verifikasi rekaman MX (`PENDING`, `VERIFIED`, `FAILED`, `CONFLICT_CLOUDFLARE_ROUTING`).
- `txt_status` (VARCHAR(32)): Status verifikasi kepemilikan TXT (`PENDING`, `VERIFIED`, `FAILED`).
- `status` (VARCHAR(32)): Status operasional (`PENDING_VERIFICATION`, `ACTIVE`, `SUSPENDED`, `DELETED`).
- `is_default` (BOOLEAN): Penanda domain default pembuatan acak (default: `false`).
- `created_at`, `updated_at` (TIMESTAMPTZ).

### 2.3 `Mailbox`
Menyimpan alamat email sementara (*disposable*) dan permanen (`MBX-001` s/d `MBX-005`).
- `id` (UUIDv7, PK): Identifikator unik mailbox.
- `domain_id` (UUID, FK -> `Domain.id`, ON DELETE RESTRICT).
- `address` (VARCHAR(320), UK): Alamat email lengkap (mis. `temp-8f92@sintaksis.biz.id`).
- `local_part` (VARCHAR(64)): Bagian nama sebelum karakter `@`.
- `access_token_hash` (CHAR(64)): Hash SHA-256 dari access token 32-karakter (`SEC-002`).
- `is_permanent` (BOOLEAN): `false` untuk temporary, `true` untuk permanen (`MBX-003`).
- `expires_at` (TIMESTAMPTZ, Nullable): Batas waktu TTL untuk mailbox temporary. `NULL` untuk permanen.
- `status` (VARCHAR(32)): Status siklus hidup (`ACTIVE`, `EXPIRED`, `PURGED`).
- `storage_quota_bytes` (BIGINT): Kuota penyimpanan maksimum (default: 104,857,600 bytes = 100 MB).
- `created_at`, `updated_at` (TIMESTAMPTZ).

### 2.4 `Message`
Menyimpan metadata dan isi email yang diterima (`INB-001` s/d `INB-005`).
- `id` (UUIDv7, PK): Identifikator unik pesan.
- `mailbox_id` (UUID, FK -> `Mailbox.id`, ON DELETE CASCADE).
- `sender_address` (VARCHAR(320)): Alamat email pengirim (Envelope / Header From).
- `sender_name` (VARCHAR(255), Nullable): Nama pengirim terurai.
- `subject` (TEXT): Subjek email.
- `text_body` (TEXT, Nullable): Konten pesan teks murni.
- `html_body_sanitized` (TEXT, Nullable): Konten pesan HTML yang telah disanitasi DOMPurify (`SEC-005`).
- `extracted_otp` (VARCHAR(32), Nullable): Kode verifikasi/OTP hasil ekstraksi heuristik (`OTP-001`, `OTP-002`).
- `extracted_link` (TEXT, Nullable): Tautan aktivasi/verifikasi hasil ekstraksi (`OTP-003`).
- `raw_eml_path` (VARCHAR(512), Nullable): Lokasi berkas mentah RFC822 pada volume persisten.
- `spf_status`, `dkim_status`, `dmarc_status` (VARCHAR(16)): Status evaluasi autentikasi inbound (`SEC-004`).
- `size_bytes` (INTEGER): Ukuran total payload email.
- `is_read` (BOOLEAN): Status dibaca (default: `false`).
- `received_at` (TIMESTAMPTZ): Waktu email diterima.

### 2.5 `TelegramBinding`
Menyimpan data otentikasi penautan bot Telegram pemilik (`BOT-001`, `SEC-006`).
- `id` (UUIDv7, PK).
- `user_id` (UUID, FK -> `User.id`).
- `chat_id` (BIGINT, UK): ID obrolan Telegram pemilik.
- `username` (VARCHAR(64), Nullable): Username akun Telegram.
- `status` (VARCHAR(32)): Status penautan (`ACTIVE`, `REVOKED`).
- `paired_at` (TIMESTAMPTZ).

### 2.6 `AuditLog`
Mencatat aktivitas administratif sistem secara immutable (`OPS-005`, `SEC-008`).
- `id` (BIGINT, PK, SERIAL).
- `user_id` (UUID, Nullable).
- `action` (VARCHAR(64)): Jenis aksi (mis. `CREATE_MAILBOX`, `PURGE_EXPIRED`, `VERIFY_DOMAIN`).
- `entity_type` (VARCHAR(32)): Tipe entitas yang dimutasi.
- `entity_id` (VARCHAR(64)): ID entitas.
- `ip_address` (VARCHAR(45)): Alamat IP pemanggil.
- `user_agent` (TEXT, Nullable).
- `metadata` (JSONB, Nullable): Detail payload aksi.
- `created_at` (TIMESTAMPTZ): Waktu aksi dicatat.

---

## 3. Strategi Pengindeksan & Kinerja Basis Data
1. `idx_mailboxes_expires_at`: `CREATE INDEX idx_mailboxes_expires_at ON mailboxes (expires_at) WHERE status = 'ACTIVE';` -> Mengoptimalkan kueri background purge scheduler setiap 60 detik (`MBX-005`, `NFR-008`).
2. `idx_mailboxes_token_hash`: `CREATE INDEX idx_mailboxes_token_hash ON mailboxes (access_token_hash);` -> Mengoptimalkan autentikasi bearer token mailbox API.
3. `idx_messages_mailbox_received`: `CREATE INDEX idx_messages_mailbox_received ON messages (mailbox_id, received_at DESC);` -> Mengoptimalkan pagination daftar inbox Web Dashboard.
