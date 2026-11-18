# Spesifikasi Fungsional: Integrasi Bot Telegram (Telegram Bot) — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/ReqCore | `docs/00-governance/project-charter.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/02-requirements/srs.md`<br>`docs/03-architecture/adr/ADR-008.md`<br>`docs/04-technical/telegram-bot-specification.md` |

---

## 1. Ringkasan Modul
Modul Bot Telegram (`BOT-###`) menyediakan kanal antarmuka bergerak (*mobile interface*) yang aman dan responsif untuk pemilik sistem (*single-owner*), memungkinkan pembuatan alamat email sementara, penerimaan notifikasi instan pesan masuk, penyalinan 1-klik kode OTP, dan perpanjangan masa aktif mailbox tanpa membuka antarmuka peramban web.

---

## 2. Rincian Kebutuhan Fungsional Bot Telegram

| ID Kebutuhan | Nama Kebutuhan | Deskripsi Fungsional & Aturan Bisnis | Kriteria Penerimaan (Acceptance Criteria) | Prioritas | Status Bukti |
| :---: | --- | --- | --- | :---: | :---: |
| **BOT-001** | Autentikasi & Allowlist Chat ID | Bot hanya merespons perintah dari Chat ID Telegram yang telah dipasangkan (*paired*) menggunakan token rahasia admin sekali pakai (*one-time pairing token*). | Perintah dari akun tak dikenal diabaikan atau dijawab dengan pesan penolakan akses aman (`SEC-006`). | **Wajib** | `VERIFIED` |
| **BOT-002** | Perintah Pembuatan Cepat (`/new`) | Pengguna dapat mengetik `/new` untuk membuat mailbox sementara acak baru. Bot mengembalikan alamat email dan tombol inline keyboard "Salin Alamat" & "Perpanjang 1 Jam". | Respon bot dikirimkan dalam waktu $\le 2$ detik sejak perintah diterima (`NFR-002`). | **Wajib** | `VERIFIED` |
| **BOT-003** | Notifikasi Push Pesan Masuk | Saat pesan baru masuk ke mailbox aktif, bot secara otomatis mengirimkan pesan ringkasan: Pengirim, Subjek, Mailbox Tujuan, dan Kode OTP (jika ada). | Notifikasi diterima di aplikasi Telegram dalam waktu $\le 2$ detik sejak email diproses ingestion worker. | **Wajib** | `VERIFIED` |
| **BOT-004** | Tombol Interaktif Salin OTP | Notifikasi pesan masuk yang mengandung kode OTP menyertakan tombol inline keyboard dengan teks `Salin OTP: [KODE]` yang siap disalin oleh pengguna. | Memudahkan pengguna memverifikasi akun di ponsel dalam 1 ketukan. | **Wajib** | `VERIFIED` |
| **BOT-005** | Perintah Pemantauan & Status (`/list`, `/status`) | Pengguna dapat melihat daftar mailbox sementara yang masih aktif, sisa waktu TTL, dan jumlah pesan yang belum dibaca. | Daftar tersaji rapi dengan tombol aksi cepat per mailbox (Extend / Delete). | **Penting** | `PROPOSED` |

---

## 3. Format Pesan Notifikasi Email Masuk

```text
📬 Pesan Email Masuk Baru!
━━━━━━━━━━━━━━━━━━━━
🎯 Mailbox: dev-test@sintaksis.biz.id
👤 Dari: verifikasi@saas-service.com
📝 Subjek: Kode Konfirmasi Pendaftaran Akun

🔑 KODE OTP: 739201
━━━━━━━━━━━━━━━━━━━━
[ 📋 Salin OTP: 739201 ]
[ ⏱️ Perpanjang 1 Jam ]  [ 🗑️ Hapus Mailbox ]
```
