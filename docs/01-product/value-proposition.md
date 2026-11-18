# Proposisi Nilai (Value Proposition) & Kanvas Solusi — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/ProductCore | `docs/00-governance/project-charter.md`<br>`docs/01-product/product-vision.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/01-product/personas-and-user-segments.md`<br>`docs/01-product/mvp-scope.md`<br>`docs/02-requirements/brd.md` |

---

## 1. Ringkasan Eksekutif Nilai Solusi
Platform **DomiBox** memposisikan diri sebagai solusi manajemen email mandiri (*self-hosted*) berfokus privasi yang menjembatani jurang pemisah antara layanan *disposable email* publik (yang rawan diblokir dan tidak aman) dengan server email konvensional (yang berat, rumit, dan minim otomatisasi).

---

## 2. Kanvas Proposisi Nilai (Value Proposition Canvas)

### 2.1 Profil Pengguna (Customer Profile)
- **Tugas Pengguna (*Customer Jobs*):**
  - Mendaftar ke layanan SaaS baru, buletin berita, atau uji coba perangkat lunak tanpa membagikan alamat email utama.
  - Menerima dan menyalin kode verifikasi (OTP) atau tautan aktivasi (*magic link*) dengan cepat.
  - Menjalankan pengujian otomatisasi alur email (QA automated end-to-end testing).
  - Menjaga kerahasiaan identitas digital pribadi secara independen di atas domain milik sendiri.
- **Keluhan & Hambatan (*Pains*):**
  - Alamat email primer kebanjiran spam dan terekspos risiko kebocoran data (*data breaches*).
  - Domain layanan temp-mail publik (1secmail, temp-mail) masuk daftar hitam (*disposable blocklists*) dan ditolak form registrasi.
  - Friksi membuka webmail konvensional yang lambat hanya untuk menyalin 6 digit kode OTP.
  - Akun penting terkunci permanen karena mailbox sementara publik kedaluwarsa tanpa opsi pemulihan (*disposable mail trap*).
- **Keuntungan yang Diharapkan (*Gains*):**
  - Rasio keberhasilan registrasi mendekati 100% menggunakan domain kustom pribadi.
  - Alur ekstraksi kode OTP ultra-cepat (< 5 detik) langsung siap salin (*copy-first*).
  - Kebebasan memilih masa aktif (TTL 10 menit hingga 7 hari) atau menjadikannya permanen.
  - Notifikasi instan di perangkat seluler melalui bot Telegram terenkripsi.

### 2.2 Peta Nilai Solusi DomiBox (*Value Map*)
- **Produk & Layanan (*Products & Services*):**
  - Single-owner Multi-domain Email Management Platform (Web Dashboard SPA + Telegram Bot).
- **Pereda Keluhan (*Pain Relievers*):**
  - **Dukungan Domain Kustom Pribadi:** Melewati filter anti-disposable pihak ketiga dengan kepemilikan DNS penuh (`VAL-001`).
  - **Anti-Trap Retention:** Kemampuan memperpanjang TTL atau mengubah mailbox sementara menjadi alias permanen (`VAL-003`).
  - **Zero-Trust Data Sovereign:** Data email tersimpan di VPS privat sendiri; rendering HTML terisolasi tanpa eksekusi skrip atau pelacak gambar (`VAL-005`).
- **Pencipta Keuntungan (*Gain Creators*):**
  - **Hero OTP Presentation & 1-Click Copy:** Banner penonjolan kode OTP otomatis dan tombol salin cepat di Web & Telegram (`VAL-002`).
  - **Akses Multi-Kanal Terpadu:** Pengguna dapat memantau pesan langsung dari Telegram tanpa perlu membuka browser (`VAL-004`).

---

## 3. Matriks Diferensiasi Nilai Strategis

| Dimensi Nilai | Layanan Temp-Mail Publik | Email Forwarder Komersial | Mail Server Tradisional | DomiBox (Target) |
| --- | :---: | :---: | :---: | :---: |
| **Kedaulatan Data** | Nol (Publik) | Rendah (Pihak Ketiga) | Penuh (Self-hosted) | **Penuh (Self-hosted)** |
| **Anti-Blocklist Form** | Buruk | Sedang | Sangat Baik | **Sangat Baik (Domain Pribadi)** |
| **Ergonomi Salin OTP** | Sedang | Buruk (Email Utuh) | Buruk (Webmail Biasa) | **Superior (Otomatis & 1-Klik)** |
| **Notifikasi Mobile** | Jarang | Mengikuti Push Mailbox | Butuh Klien IMAP | **Native Bot Telegram** |
| **Kompleksitas Setup** | Nol | Rendah | Sangat Tinggi | **Rendah (Docker Compose Monolith)** |
| **Biaya Operasional** | Gratis (Iklan) | Langganan Bulanan | Biaya VPS Tinggi | **Sangat Hemat (VPS 3.6 GB RAM)** |

---

## 4. Keterkaitan dengan Sasaran MVP & Status Bukti
Proposisi nilai ini diturunkan langsung dari hipotesis `VAL-001` hingga `VAL-005` pada `docs/01-product/product-vision.md` dan direalisasikan secara bertahap melalui fitur-fitur yang tercantum dalam `docs/01-product/mvp-scope.md`.
