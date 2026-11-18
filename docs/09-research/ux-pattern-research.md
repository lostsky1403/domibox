# Riset Pola Antarmuka & Interaksi Pengguna (UX Pattern Research) — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/UXCore | `docs/00-governance/project-charter.md`<br>`docs/01-product/product-vision.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/09-research/ux-pattern-benchmark.md` |

---

## 1. Tujuan Riset & Metodologi
Riset ini mendokumentasikan pola interaksi pengguna (*UX Patterns*), arsitektur informasi (*Information Architecture*), dan ergonomi alur kerja (*Workflow Ergonomics*) yang dianalisis dari produk sejenis dan platform terkemuka. Dokumen ini menyelaraskan temuan mendalam dari `docs/09-research/ux-pattern-benchmark.md` (analisis 1secmail, Mail.tm, Guerrilla Mail, SimpleLogin, DuckDuckGo Email Protection, Portainer, Supabase) menjadi panduan kanonikal berlabel bukti.

---

## 2. Analisis Pola Produk Sejenis & Keputusan UX (UX Pattern Matrix)

| Produk Acuan | Pola Interaksi Utama yang Diamati | Status Bukti | Keputusan Adopsi DomiBox | Rujukan Pembuktian |
| --- | --- | :---: | --- | --- |
| **Mail.tm** | - Pembuatan alamat instan 1-klik di halaman beranda.<br>- Tombol salin alamat email persisten di bagian atas (*sticky header*).<br>- Polling inbox otomatis setiap 5 detik dengan indikator visual. | `VERIFIED` | **Adopsi Penuh:** Salin instan 1-klik dan auto-refresh inbox menjadi pola interaksi standar pada Web Dashboard (`FR-004`). | `docs/09-research/ux-pattern-benchmark.md` Bagian 2 |
| **SimpleLogin / addy.io** | - Manajemen alias permanen dengan label catatan layanan (*notes/tags*).<br>- Toggle cepat aktif/nonaktifkan alias tanpa menghapus data.<br>- Pemisahan domain kustom per alias. | `VERIFIED` | **Adopsi Sebagian:** Label layanan dan toggle suspend diadopsi untuk mailbox permanen (`FR-003`). Fitur forwarding keluar ditolak pada rilis MVP (`F1`). | `docs/09-research/ux-pattern-benchmark.md` Bagian 3 |
| **Guerrilla Mail** | - Hitung mundur TTL (*countdown timer*) yang terlihat jelas.<br>- Tombol perpanjang masa aktif manual (+10 menit / +1 jam).<br>- Pilihan kustom nama mailbox vs acak. | `VERIFIED` | **Adopsi Penuh:** Visualisasi countdown TTL interaktif dan tombol *Extend Duration* diadopsi pada Web UI dan Bot Telegram (`FR-002`). | `docs/09-research/ux-pattern-benchmark.md` Bagian 2 |
| **1secmail** | - Ekstraksi kode OTP langsung dari subjek/pratinjau email.<br>- Tidak memerlukan login akun atau pendaftaran rumit. | `VERIFIED` | **Adopsi & Peningkatan:** DomiBox memperluas pola ini dengan algoritma ekstraksi regex otomatis dan penempatan tombol salin OTP di card notifikasi Telegram (`FR-005`). | `docs/09-research/ux-pattern-benchmark.md` Bagian 4 |
| **Portainer & Supabase** | - Tata letak dashboard dua kolom: sidebar navigasi ringkas dan area konten fleksibel.<br>- Status badge indikator kesehatan layanan (Health Pill: Active, Expired, Suspended). | `VERIFIED` | **Adopsi:** Desain visual DomiBox menggunakan palet warna monokrom modern shadcn/ui dengan badge status standar WCAG Level AA (`NFR-006`). | `docs/09-research/ux-pattern-benchmark.md` Bagian 5 |

---

## 3. Prinsip Desain Antarmuka Utama (Core UX Principles)

1. **Copy-First Ergonomics:** Setiap alamat email yang dihasilkan dan kode OTP yang diekstraksi wajib memiliki tombol salin 1-klik dengan umpan balik visual (*toast notification* atau *copied checkmark*) dalam waktu $\le 100$ ms.
2. **Zero-Cognitive Friction for Ephemeral Mail:** Pengguna yang membutuhkan email cepat tidak boleh diwajibkan mengisi form konfigurasi panjang. Satu klik tombol "Generate Random Mailbox" langsung mengembalikan alamat siap pakai.
3. **Penyajian Kode OTP yang Menonjol (*OTP Hero Presentation*):** Kode verifikasi yang terdeteksi disajikan dalam *Hero Banner* berukuran huruf besar di atas badan email utama, sehingga pengguna tidak perlu menggulir atau membaca isi email yang panjang.
4. **Keamanan Rendering Tanpa Kompromi (*Zero-Trust HTML Rendering*):** Email HTML disajikan dalam wadah terisolasi (`iframe sandbox` tanpa skrip) dan gambar eksternal dinonaktifkan secara bawaan untuk melindungi privasi IP pengguna (`SEC-005`).

---

## 4. Pola Interaksi Bot Telegram (Telegram Bot UX Patterns)

- **Menu Perintah Cepat:**
  - `/new`: Menghasilkan mailbox acak instan dan mengembalikan tombol *Inline Keyboard* "Salin Alamat" & "Perpanjang 1 Jam".
  - `/list`: Menampilkan daftar mailbox aktif beserta sisa durasi TTL.
  - `/read [id]`: Mengambil pesan terakhir dan menampilkan subjek, pengirim, serta kode OTP.
- **Kartu Notifikasi Pesan Masuk (*Push Alert Card*):**
  Saat email masuk terdeteksi, bot mengirimkan pesan ringkas:
  ```text
  📬 Email Masuk Baru!
  Penerima: dev-test@sintaksis.biz.id
  Pengirim: no-reply@service.com
  Subjek: Verifikasi Akun Anda

  🔑 KODE OTP: 849201
  [📋 Salin OTP: 849201] [🌐 Buka di Web Dashboard]
  ```

---

## 5. Celah Validasi & Langkah Selanjutnya
- **Uji Keterbacaan Pengguna Nyata (`NOT VERIFIED` / `PROPOSED`):** Pengujian waktu tempuh salin OTP ($\le 5$ detik) belum diuji pada pengguna eksternal non-developer.
- **Rekomendasi:** Lakukan sesi uji kegunaan (*usability test*) pada tahap validasi implementasi MVP.
