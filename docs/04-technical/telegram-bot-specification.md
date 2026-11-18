# Telegram Bot Technical Specification — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/TechSpec | `docs/02-requirements/functional-specs/05-telegram-bot.md`<br>`docs/03-architecture/adr/ADR-008.md`<br>`docs/04-technical/api/openapi.yaml` |

---

## 1. Arsitektur Komponen Bot
Bot Telegram DomiBox diimplementasikan menggunakan **grammY** (`ADR-008`) dalam arsitektur webhook HTTPS yang terhubung ke backend Fastify. Bot berfungsi sebagai kanal interaksi cepat (*fast interaction channel*) bagi pemilik tunggal (`STK-001`).

---

## 2. Alur Penautan Kredensial & Autentikasi (`BOT-001`, `SEC-006`)
1. Pemilik membuka Web Dashboard -> Pengaturan -> Telegram Integration.
2. Web Dashboard menghasilkan *Pairing Token* acak 8-karakter dengan masa berlaku 5 menit (`TTL = 300s`).
3. Pemilik mengirimkan perintah ke bot: `/pair <TOKEN>`.
4. Backend memvalidasi token, mencocokkan `chat_id` Telegram pengirim dengan `user_id` pemilik, dan menyimpan binding aktif pada tabel `telegram_bindings`.
5. Semua pesan atau perintah dari `chat_id` yang tidak terdaftar akan ditolak dengan respons diam (*silent drop*) atau pesan penolakan ringkas.

---

## 3. Struktur Perintah Bot (Command Specifications)

| Perintah | Parameter | Deskripsi & Perilaku Sistem |
| --- | --- | --- |
| `/start` | - | Menampilkan salam pembuka, status penautan bot, dan petunjuk penggunaan ringkas. |
| `/pair` | `<token>` | Memasangkan obrolan Telegram pemilik dengan akun admin DomiBox (`BOT-001`). |
| `/new` | `[durasi] [domain]` | Membuat mailbox sementara instan. Default durasi: 1 jam (`BOT-002`). |
| `/inbox` | `[mailbox_id]` | Menampilkan 5 email terbaru dari mailbox aktif beserta ringkasan status (`BOT-005`). |
| `/otp` | `[mailbox_id]` | Mengambil kode OTP terbaru dari pesan terakhir (`OTP-001`, `BOT-004`). |
| `/extend` | `<mailbox_id> [durasi]` | Memperpanjang masa aktif mailbox sementara (`MBX-002`). |
| `/delete` | `<mailbox_id>` | Menghapus mailbox sementara seketika secara tuntas (`MBX-004`). |
| `/status` | - | Menampilkan status ringkas server, jumlah mailbox aktif, dan penggunaan kuota. |

---

## 4. Mekanisme Notifikasi Push Real-time (`BOT-003`, `NFR-006`)
Saat email masuk diproses oleh ingestion pipeline:
1. Fastify backend mendeteksi adanya penautan Telegram aktif.
2. Ekstraktor OTP memeriksa keberadaan kode verifikasi.
3. Jika OTP ditemukan:
   - Bot mengirimkan pesan berformat MarkdownV2 ke obrolan pemilik:
     ```text
     📬 *Email Baru Diterima!*
     📍 Mailbox: `temp-8f92@sintaksis.biz.id`
     👤 Pengirim: `noreply@github.com`
     📝 Subjek: Verification Code

     🔑 *KODE OTP:* `849201`
     ```
   - Bot menyertakan tombol inline (*Inline Keyboard Button*):
     - `[ 📋 Salin Kode OTP ]` (menggunakan callback copy)
     - `[ 🌐 Buka di Web Dashboard ]` (deep link terotentikasi)
4. Waktu transmisi notifikasi dari saat email masuk hingga tiba di klien Telegram ditargetkan ≤ 2.0 detik (`NFR-006`).
