# Prinsip Pengalaman Pengguna (UX Principles) — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/UXCore | `docs/00-governance/project-charter.md`<br>`docs/01-product/product-vision.md`<br>`docs/09-research/ux-pattern-research.md`<br>`docs/09-research/ux-pattern-benchmark.md` |

---

## 1. Filosofi & Pendekatan Desain
Platform **DomiBox** memprioritaskan efisiensi operasional dan utilitas fungsional di atas dekorasi visual. Desain antarmuka DomiBox berpegang pada filosofi **"Fast, Predictable, and Zero-Friction"**, memastikan pengguna dapat membuat alamat email sementara, menerima pesan, dan menyalin kode OTP dalam hitungan detik.

---

## 2. Lima Prinsip Utama UX DomiBox

### 2.1 Ergonomi Berorientasi Salin Instan (*Copy-First Ergonomics*)
- Setiap kali alamat email atau kode OTP dihasilkan, sistem menyediakan tombol salin 1-klik yang mudah dijangkau.
- Umpan balik visual (*micro-interaction*) berupa ikon centang hijau atau pesan toast muncul seketika ($\le 100$ ms) setelah aksi salin dilakukan.

### 2.2 Penonjolan Hero OTP (*OTP Hero Banner*)
- Kode verifikasi 4–8 karakter yang terdeteksi disajikan dalam banner visual berukuran besar di bagian paling atas tampilan detail pesan.
- Pengguna tidak boleh dipaksa menggulir ke bawah atau membaca badan email promosi yang panjang untuk menemukan kode verifikasi.

### 2.3 Kejelasan Masa Aktif & Kontrol Retensi (*Explicit TTL Visibility*)
- Sisa masa aktif mailbox sementara wajib ditampilkan dengan indikator hitung mundur (*countdown timer*) yang dinamis.
- Pengguna diberikan kontrol eksplisit untuk memperpanjang durasi (+1 jam, +24 jam) atau menghapus mailbox seketika sebelum waktu habis.

### 2.4 Keamanan Rendering Bawaan (*Zero-Trust Safe Rendering*)
- Email HTML disajikan dalam wadah terisolasi (`iframe sandbox` tanpa eksekusi JavaScript).
- Gambar eksternal diblokir secara default (*Anti-Tracking Pixel*) untuk melindungi privasi lokasi dan alamat IP pengguna, dengan opsi pembukaan manual oleh pengguna.

### 2.5 Keseragaman Paradigma Multi-Kanal (*Unified Multi-Channel Experience*)
- Aksi-aksi inti pada Web Dashboard (buat alamat, lihat pesan, salin OTP, perpanjang waktu) memiliki padanan perintah langsung yang identik pada Bot Telegram (`/new`, `/read`, `/extend`, `/delete`).

---

## 3. Standar Aksesibilitas & Responsivitas
- **Kepatuhan WCAG:** Seluruh komponen antarmuka menggunakan primitif Radix UI / shadcn/ui yang memenuhi standar WCAG Level AA untuk kontras warna teks dan navigasi papan ketik (*keyboard navigation*).
- **Desain Responsif:** Tampilan dashboard web beradaptasi secara mulus mulai dari layar desktop lebar ($>1200$ px), tablet ($768-1024$ px), hingga layar seluler ($<600$ px).
