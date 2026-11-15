# Visi Produk (Product Vision) & Proposisi Nilai — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-14 | omp-orchestrator/ProductDocs | `docs/00-governance/project-charter.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/01-product/personas-and-user-segments.md`<br>`docs/01-product/mvp-scope.md`<br>`docs/09-research/problem-value-research.md` |

---

## 1. Ringkasan Eksekutif & Latar Belakang (Executive Summary)

**DomiBox** adalah platform manajemen mailbox mandiri (*self-hosted multi-domain email management platform*) yang dirancang khusus untuk memenuhi kebutuhan penerimaan email masuk (*inbound email*), verifikasi akun, registrasi layanan uji coba, isolasi identitas privasi, dan ekstraksi cepat kode OTP (*One-Time Password*) atau tautan verifikasi otomatis (*magic link*).

Dalam ekosistem digital saat ini, kebutuhan privasi data, kepemilikan infrastruktur komunikasi secara independen, serta pengujian sistem berbasis email menghadapi tantangan signifikan:
1. **Penyebaran Alamat Email Pribadi/Korporat Utama:** Pengguna terpaksa membagikan alamat email primer saat mendaftar ke puluhan layanan uji coba, platform SaaS, buletin, atau pengujian aplikasi. Dampaknya adalah membanjirnya spam, pelacakan profil (*profiling*), dan risiko paparan kebocoran data (*data breach exposure*).
2. **Keterbatasan Layanan Temporary Mail Publik:** Layanan disposable email publik (seperti 1secmail, temp-mail, Guerrilla Mail) memiliki kelemahan mendasar:
   - Domain publik mereka sering diblokir secara agresif oleh filter registrasi layanan SaaS modern (misal: Cloudflare, Google, AWS, GitHub).
   - Pesan email masuk dapat dibaca publik tanpa proteksi privasi.
   - Tidak ada jaminan ketersediaan, kontrol data, maupun retensi pesan teratur.
3. **Ketiadaan Solusi Terpadu Temp + Permanent Mailbox Mandiri:** Sebagian besar solusi yang ada terkotak-kotak menjadi sekadar layanan alias/forwarder (SimpleLogin, addy.io) atau mail server konvensional yang rumit dikelola (Postfix, Stalwart murni). DomiBox menyatukan fleksibilitas mailbox sementara (*disposable/TTL-based*) dan stabilitas mailbox permanen di atas domain kustom milik pengguna sendiri.

---

## 2. Pernyataan Visi Produk (Product Vision Statement)

```
Untuk:
  Pengembang perangkat lunak, QA engineer, profesional privasi, dan pemilik domain mandiri
Yang membutuhkan:
  Alat penerimaan email yang cepat, terisolasi, dan aman untuk registrasi akun, verifikasi OTP, dan pengetesan alur pesan
DomiBox adalah:
  Platform manajemen mailbox mandiri multi-domain yang mengintegrasikan pembuatan alamat email sementara (berbasis TTL) dan permanen
Yang menyediakan:
  Ekstraksi otomatis kode OTP/magic link seketika, notifikasi instan multi-kanal (Web Dashboard & Telegram Bot), serta kontrol penuh atas retensi dan isolasi data
Berbeda dengan:
  Layanan temp-mail publik yang rawan diblokir dan tidak aman, serta layanan email forwarding komersial pihak ketiga yang mengenakan biaya langganan
Produk kami:
  Berjalan secara self-hosted di infrastruktur VPS milik sendiri dengan domain kustom pribadi, menjamin kerahasiaan 100%, ketiadaan pelacakan data, dan biaya operasional yang efisien.
```

---

## 3. Hipotesis Masalah & Nilai (Problem & Value Hypotheses)

Sesuai dengan `docs/00-governance/documentation-standards.md`, bagian ini membedakan secara tegas antara temuan yang telah terverifikasi, hipotesis nilai, dan celah pembuktian yang memerlukan riset primer terperinci (merujuk pada celah `Q-001` / `docs/09-research/problem-value-research.md`).

### 3.1 Hipotesis Masalah Pengguna (User Problem Hypotheses)

| ID Masalah | Pernyataan Masalah | Tingkat Dampak | Status Bukti | Rujukan & Catatan Validasi |
| --- | --- | --- | --- | --- |
| **PRB-001** | **Kelelahan Spam & Paparan Kebocoran:** Pengguna merasa enggan menggunakan email primer untuk pendaftaran layanan baru karena khawatir alamatnya dijual ke pihak ketiga atau terkena spam tak terhentikan. | Tinggi | `ASSUMPTION` | Merujuk pada celah `Q-001`. Data kualitatif umum mendukung, namun survei primer terukur belum dikuantifikasi. |
| **PRB-002** | **Pemblokiran Domain Temp-Mail Publik:** Layanan temp-mail gratisan umum ditolak oleh form pendaftaran web karena domain mereka masuk dalam daftar hitam (*disposable email blocklists*). | Sangat Tinggi | `VERIFIED` | Terkonfirmasi dalam riset komparatif `docs/09-research/competitive-comparative-research.md` dan benchmark UX `docs/09-research/ux-pattern-benchmark.md`. |
| **PRB-003** | **Friksi Ekstraksi Kode OTP/Verifikasi:** Pengguna harus membuka antarmuka webmail lengkap, menunggu sinkronisasi folder, membuka email HTML berat, dan menyalin manual 4–8 digit kode OTP. | Sedang | `VERIFIED` | Benchmark pada Mail.tm, Guerrilla Mail, SimpleLogin menunjukkan UX copy-first OTP mempersingkat alur kerja secara signifikan. |
| **PRB-004** | **Ketakutan Kehilangan Akses Akun (Disposable Mail Trap):** Layanan temp-mail publik menghapus email setelah waktu singkat tanpa opsi perpanjangan atau pemulihan permanen, sehingga akun yang terdaftar terkunci selamanya. | Tinggi | `ASSUMPTION` | Menjadi dasar kebutuhan fitur konversi temporary ke permanent alias atau pengaturan TTL fleksibel. |
| **PRB-005** | **Kompleksitas Operasional Mail Server Tradisional:** Menyiapkan Postfix/Dovecot/DKIM/SpamAssassin dari nol membutuhkan keahlian sysadmin tinggi dan rentan salah konfigurasi. | Tinggi | `VERIFIED` | Analisis kelayakan infrastruktur `docs/09-research/mail-infrastructure-suitability.md` menunjukkan perlunya arsitektur terpadu (Stalwart/Docker). |

### 3.2 Hipotesis Proposisi Nilai (Value Proposition Hypotheses)

| ID Proposisi | Hipotesis Nilai | Target Manfaat Kuantitatif (Hipotesis) | Status Bukti | Kebutuhan Terkait |
| --- | --- | --- | --- | --- |
| **VAL-001** | **Domain Kustom Anti-Block:** Penggunaan domain pribadi milik pengguna menghilangkan risiko penolakan form registrasi akibat blocklist domain publik. | Rasio keberhasilan registrasi email masuk mendekati 100% pada domain terverifikasi. | `ASSUMPTION` | `DOM-001`, `BR-001` |
| **VAL-002** | **Zero-Friction OTP Copy:** Ekstraksi otomatis kode OTP dan tautan verifikasi langsung di banner atas pesan serta notifikasi bot Telegram. | Mengurangi waktu salin kode verifikasi dari rata-rata ~25 detik menjadi < 5 detik. | `PROPOSED` | `OTP-001`, `BOT-001`, `BR-002` |
| **VAL-003** | **Fleksibilitas Siklus Hidup Mailbox:** Pengguna dapat membuat mailbox sementara 10 menit s/d 7 hari, memperpanjang durasi, atau menetapkan mailbox permanen untuk akun penting. | Menghilangkan risiko "disposable mail trap" sebesar 100% untuk akun yang ingin dipertahankan. | `PROPOSED` | `MBX-001`, `MBX-002`, `BR-001` |
| **VAL-004** | **Akses Multi-Kanal Terpadu (Telegram Bot + Web Dashboard):** Pengguna dapat menerima kode OTP langsung di Telegram tanpa perlu membuka browser, atau beralih ke dashboard web untuk inspeksi pesan mendalam. | Mengakomodasi kebutuhan akses mobile cepat (< 3 detik) via bot Telegram. | `PROPOSED` | `BOT-001`, `WEB-001`, `BR-003` |
| **VAL-005** | **Kedaulatan & Sanitasi Data Total:** Seluruh email disimpan di server privat pengguna; rendering HTML disanitasi ketat untuk mencegah pelacakan pixel dan eksekusi skrip jahat. | Mencegah 100% pelacakan beacon eksternal dan risiko XSS berbasis email. | `VERIFIED` (Desain Konseptual) | `SEC-005`, `SEC-008`, `BR-004` |

---

## 4. Sasaran Hasil & Indikator Keberhasilan Strategis (Target Outcomes)

### 4.1 Sasaran Hasil Jangka Pendek (MVP Outcomes)
1. **Penerimaan Email Inbound Handal:** Mampu menerima email masuk dari penyedia global (Google, Microsoft, Cloudflare, SendGrid, Amazon SES) ke domain `sintaksis.biz.id` (pilot domain) dengan latensi pemrosesan inbound ≤ 3 detik (`NFR-004`).
2. **Penyediaan Alamat Instan:** Pengguna dapat men-generate alamat email sementara dalam ≤ 1.5 detik (`NFR-002`) baik melalui Web UI maupun Telegram Bot.
3. **Ekstraksi OTP Akurat:** Parser heuristik regex mampu mengekstrak kode verifikasi angka/alfanumerik 4–8 karakter serta tautan konfirmasi dengan akurasi target ≥ 95% (`NFR-005`, status `PROPOSED`).
4. **Isolasi Keamanan Ketat:** Tidak ada kebocoran pesan antar sesi atau token akses (`SEC-002`), serta tidak ada eksekusi XSS dari payload email masuk (`SEC-005`).

### 4.2 Sasaran Hasil Jangka Menengah (Post-MVP / Fase 2)
1. **Dukungan Multi-Domain Tak Terbatas:** Pengguna dapat menambahkan lebih dari 1 domain kustom dengan verifikasi DNS otomatis.
2. **Pengiriman Email Keluar (Outbound SMTP):** Kemampuan mengirim email balasan atau inisiasi pengiriman dari mailbox permanen (menunggu penyelesaian isu port 25 outbound Tencent Cloud / `Q-SMTP-OUT-001`).
3. **API & Webhook Terbuka:** Integrasi CI/CD automated testing untuk tim QA guna mengambil OTP secara terprogram via REST API.

---

## 5. Diferensiasi Kompetitif (Competitive Differentiation)

Berdasarkan kompilasi riset komparatif (`docs/09-research/competitive-comparative-research.md`) dan benchmark pola UX (`docs/09-research/ux-pattern-benchmark.md`), posisi DomiBox dibandingkan alternatif pasar adalah sebagai berikut:

| Dimensi Evaluasi | Disposable Mail Publik (1secmail, Mail.tm) | Layanan Email Alias (SimpleLogin, addy.io) | Mail Server Standar (Postfix, iRedMail, Stalwart Standalone) | DomiBox (Target Platform) |
| --- | --- | --- | --- | --- |
| **Kepemilikan Domain** | Domain publik bersama (sering di-blacklist) | Subdomain vendor atau domain kustom berbayar | Domain kustom sendiri | **Domain kustom sendiri (Private)** |
| **Kerahasiaan Pesan** | Rendah (seringkali terbuka untuk siapa saja yang tahu inbox) | Tinggi (diteruskan ke mailbox primer) | Tinggi (disimpan di server sendiri) | **Tinggi (Terisolasi per sesi/kunci privat)** |
| **Ekstraksi Khusus OTP** | Tidak ada / parsing dasar teks | Terbatas (hanya meneruskan isi email utuh) | Tidak ada (butuh mail client terpisah) | **Otomatis (Regex + Heuristik + Quick Copy Button)** |
| **Integrasi Telegram Bot** | Sangat terbatas / bot pihak ketiga tidak resmi | Terbatas pada webhook notifikasi | Butuh script integrasi manual | **Native 1st-class integration (DomiBox Bot)** |
| **Dukungan Temp + Perm** | Hanya sementara (TTL paksa) | Hanya alias permanen (forwarding) | Hanya permanen (akun fisik) | **Hibrida: Mailbox Sementara (TTL) & Permanen** |
| **Kebutuhan Mailbox Primer**| Tidak butuh | Wajib punya mailbox tujuan (Gmail/Outlook) | Tidak butuh | **Mandiri (Inbox mandiri di Web Dashboard & Bot)** |
| **Penyimpanan & Retensi** | Dihapus server publik tanpa kontrol | Tergantung mailbox tujuan | Konfigurasi cron/quota rumit | **Auto-purge terkonfigurasi per TTL akun/kebijakan** |

---

## 6. Asumsi Strategis & Keterbatasan (Strategic Assumptions & Constraints)

1. **Model Penggunaan Tunggal / Privat (`A-REQ-001`):** Untuk rilis MVP, DomiBox ditujukan untuk penggunaan pribadi pemilik (*single-owner*) atau kelompok internal tertutup. Tidak ada sistem pendaftaran publik bebas, penagihan (*billing*), ataupun multi-tenancy komersial.
2. **Infrastruktur Hosting Mandiri (`A-REQ-003`):** Sistem di-host pada VPS Tencent Cloud (`vps-tencent3b`, 2 vCPU, 3.6 GiB RAM, OS Ubuntu 24.04.5 LTS, Docker Engine 29.9.3) yang telah terverifikasi aman dari tabrakan port listening.
3. **Fokus Inbound SMTP pada MVP:** Mengingat pembatasan port 25 keluar (*outbound*) oleh Tencent Cloud (`F1` / `ADR-0010`), MVP DomiBox berfokus 100% pada penerimaan email masuk (*inbound-only*).
4. **Ketiadaan Validasi Riset Kuantitatif (`Q-001`):** Angka metrik pain point pengguna belum diverifikasi melalui riset primer skala besar; kebutuhan saat ini diturunkan dari observasi pola engineering dan pemodelan ancaman privasi.
