# Spesifikasi Fungsional: Antarmuka Web Dashboard (Web Dashboard) — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/ReqCore | `docs/00-governance/project-charter.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/02-requirements/srs.md`<br>`docs/03-architecture/adr/ADR-007.md`<br>`docs/01-product/ia-and-interaction-spec.md` |

---

## 1. Ringkasan Modul
Modul Antarmuka Web Dashboard (`WEB-###`) menyajikan antarmuka Single Page Application (SPA) modern, cepat, dan aksesibel berbasis React 18, Vite, Tailwind CSS, dan shadcn/ui. Dashboard ini menjadi pusat kendali visual bagi pemilik untuk mengelola domain, memantau mailbox, membaca pesan email, dan menginspeksi kode verifikasi secara aman.

---

## 2. Rincian Kebutuhan Fungsional Web Dashboard

| ID Kebutuhan | Nama Kebutuhan | Deskripsi Fungsional & Aturan Bisnis | Kriteria Penerimaan (Acceptance Criteria) | Prioritas | Status Bukti |
| :---: | --- | --- | --- | :---: | :---: |
| **WEB-001** | Antarmuka Workspace & Inbox | Tampilan terpadu yang menampilkan panel generator alamat, daftar mailbox aktif, dan penampil pesan email. | Waktu pemuatan awal antarmuka (*First Contentful Paint*) $\le 1.2$ detik pada koneksi standar (`NFR-004`). | **Wajib** | `VERIFIED` |
| **WEB-002** | Widget Generator Cepat (*Quick Generator*) | Komponen formulir ringkas untuk memilih domain, menentukan prefix (acak/kustom), durasi TTL, dan tombol instan "Salin & Gunakan". | Alamat terbuat dan tersalin ke clipboard dalam waktu $\le 100$ ms pasca respon API. | **Wajib** | `VERIFIED` |
| **WEB-003** | Penampil Pesan HTML Aman (*Safe Viewer*) | Panel pembaca pesan yang mengisolasi HTML di dalam `<iframe sandbox="allow-same-origin">` dan memblokir pelacak gambar eksternal secara bawaan (`SEC-005`). | Muatan JavaScript dinonaktifkan total; gambar luar hanya dimuat saat tombol otorisasi diklik. | **Wajib** | `VERIFIED` |
| **WEB-004** | Komponen Banner Hero OTP | Kotak penonjolan kode verifikasi di atas pesan email yang menampilkan kode dalam ukuran huruf besar dan tombol salin 1-klik. | Banner muncul otomatis jika atribut `has_otp` bernilai `true` pada payload pesan. | **Wajib** | `VERIFIED` |
| **WEB-005** | Responsivitas & Mode Gelap (*Dark Mode*) | Antarmuka mendukung tema terang dan gelap otomatis (*system preference*) serta beradaptasi pada tata letak seluler hingga desktop lebar. | Kepatuhan kontras rasio WCAG Level AA terpenuhi pada kedua tema (`NFR-006`). | **Wajib** | `VERIFIED` |

---

## 3. Komponen Arsitektur Antarmuka (Component Breakdown)
- `MailboxGeneratorCard`: Generator mailbox kustom/acak dengan switch TTL.
- `MailboxListSidebar`: Daftar mailbox aktif dengan indikator hitung mundur waktu.
- `MessageListTable`: Tabel daftar email masuk dengan penanda status OTP dan waktu terima.
- `MessageDetailViewer`: Penampil email dengan tab Header, Text, dan Iframe HTML Sanitized.
- `DomainManagerModal`: Form verifikasi DNS dan instruksi konfigurasi MX/TXT Cloudflare.
