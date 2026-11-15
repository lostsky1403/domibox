# Cakupan MVP (Minimum Viable Product Scope) & Batasan Rilis — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-14 | omp-orchestrator/ProductDocs | `docs/00-governance/project-charter.md`<br>`docs/00-governance/open-questions.md`<br>`docs/00-governance/decision-log.md`<br>`docs/01-product/product-vision.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/02-requirements/traceability/traceability-matrix.md` |

---

## 1. Tujuan & Filosofi Penentuan Cakupan (Scope Definition & Philosophy)

Dokumen ini menetapkan batasan yang tegas mengenai apa yang **termasuk dalam cakupan rilis MVP (*In-Scope*)** dan apa yang **dikeluarkan dari cakupan rilis MVP (*Out-of-Scope*)** untuk platform **DomiBox**.

Filosofi rilis MVP DomiBox bertumpu pada tiga prinsip utama:
1. **Solusi Tertarget untuk Masalah Riil (Problem-Targeted):** MVP berfokus menyelesaikan kebutuhan primer penerimaan email masuk, isolasi alamat sementara/permanen, dan ekstraksi cepat kode OTP/verifikasi pada domain kustom milik pengguna sendiri.
2. **Kesesuaian dengan Kendala Infrastruktur Nyata (Infrastructure-Grounded):** Mengingat keterbatasan port outbound 25 pada VPS Tencent Cloud (`F1`) serta kapasitas memori VPS 3.6 GiB RAM, arsitektur MVP memprioritaskan efisiensi sumber daya dan membatasi operasi ke arah *inbound-only*.
3. **Penyederhanaan Tata Kelola Akses (Private Single-Owner First):** Menghindari kompleksitas sistem billing, multi-tenancy komersial, dan pendaftaran publik liar yang memerlukan infrastruktur anti-fraud masif.

---

## 2. Rincian Batasan Cakupan MVP (In-Scope vs Out-of-Scope)

### 2.1 Fitur & Kapabilitas Dalam Cakupan MVP (In-Scope)

| ID Fitur | Modul Terkait | Deskripsi Fitur MVP | Prioritas | Justifikasi Teknis / Bisnis |
| --- | --- | --- | --- | --- |
| **MVP-DOM-01** | `DOM-001` | **Manajemen Domain Kustom Tunggal/Pilot (`sintaksis.biz.id`):** Validasi konfigurasi DNS (pemeriksaan record MX dan TXT verifikasi kepemilikan). | Wajib | Prasyarat utama penerimaan email masuk ke mail engine Stalwart. |
| **MVP-MBX-01** | `MBX-001` | **Mailbox Sementara (TTL-based Disposable Mailbox):** Pembuatan alamat email instan dengan durasi masa aktif yang dapat dipilih (10 menit, 1 jam, 24 jam, hingga 7 hari). | Wajib | Menyelesaikan masalah spam saat registrasi akun uji coba (`VAL-003`). |
| **MVP-MBX-02** | `MBX-001` | **Perpanjangan & Penghapusan Manual Mailbox Sementara:** Kemampuan menambah durasi TTL atau menghapus mailbox sebelum waktunya. | Wajib | Mencegah terputusnya akses saat proses verifikasi belum selesai. |
| **MVP-MBX-03** | `MBX-002` | **Mailbox / Alias Permanen Terbatas:** Penyediaan alamat email yang tidak kedaluwarsa untuk layanan penting yang membutuhkan akses jangka panjang. | Penting | Memenuhi proposisi nilai hibrida (temp + perm) sesuai Piagam Proyek. |
| **MVP-INB-01** | `INB-001` | **Penerimaan Email Masuk (Inbound-Only SMTP):** Menerima pesan email masuk via port SMTP standar (port 25) pada VPS Tencent Cloud. | Wajib | Fungsi inti platform; tidak membutuhkan izin unblock outbound port 25. |
| **MVP-INB-02** | `INB-001` | **MIME Parsing & Pemisahan Bagian Pesan:** Penguraian email menjadi metadata (From, To, Date, Subject), teks polos (plaintext), dan HTML aman. | Wajib | Prasyarat ekstraksi data teks dan rendering antarmuka pengguna. |
| **MVP-OTP-01** | `OTP-001` | **Ekstraksi Otomatis Kode OTP (4–8 Karakter):** Algoritma heuristik berbasis regex untuk mendeteksi kode verifikasi numerik dan alfanumerik. | Wajib | Mengurangi waktu salin kode secara drastis (`VAL-002`). |
| **MVP-OTP-02** | `OTP-001` | **Deteksi Tautan Verifikasi (Magic Link):** Identifikasi URL konfirmasi pendaftaran/aktivasi akun di dalam badan email. | Penting | Memudahkan aktivasi akun 1-klik tanpa membaca seluruh email. |
| **MVP-BOT-01** | `BOT-001` | **Integrasi Bot Telegram (Akses Cepat):** Perintah bot (`/new`, `/list`, `/read`, `/extend`) untuk membuat dan memantau mailbox sementara. | Wajib | Akses mobile instan tanpa harus membuka dashboard web. |
| **MVP-BOT-02** | `BOT-001` | **Notifikasi Instan Pesan Masuk & Tombol Salin OTP:** Notifikasi otomatis saat email tiba dengan tombol interaktif untuk menyalin kode OTP dalam 1 klik. | Wajib | Pola UX unggulan hasil benchmark `docs/09-research/ux-pattern-benchmark.md`. |
| **MVP-WEB-01** | `WEB-001` | **Web Dashboard Responsif:** Antarmuka inbox minimalis untuk membuat mailbox, melihat daftar email, membaca isi pesan, dan status domain. | Wajib | Akses visual komprehensif bagi pengguna desktop/laptop. |
| **MVP-WEB-02** | `WEB-001` | **Sanitasi HTML & Proteksi XSS:** Isolasi rendering email HTML dan penonaktifan gambar eksternal (anti-tracking pixel) secara default. | Wajib | Standar keamanan privasi (`SEC-005`). |
| **MVP-OPS-01** | `OPS-001` | **Scheduler Pembersihan Otomatis (Auto-Purge Engine):** Daemon internal untuk menghapus mailbox sementara dan email terkait setelah masa TTL habis. | Wajib | Mencegah pembengkakan penyimpanan VPS dan menjaga higiene data (`F4`). |
| **MVP-SEC-01** | `SEC-001`..`008` | **Proteksi Akses Tunggal & Autentikasi Admin:** Proteksi antarmuka web dan pairing bot Telegram berbasis token/kunci rahasia milik owner. | Wajib | Menjamin privasi penuh platform privat single-owner. |

---

### 2.2 Fitur & Kapabilitas di Luar Cakupan MVP (Out-of-Scope — Ditunda ke Fase 2)

| ID Fitur Tertunda | Nama Fitur / Modul | Alasan Penundaan ke Fase 2 / Rilis Berikutnya | Tergantung Pada |
| --- | --- | --- | --- |
| **OOS-OUT-01** | **Pengiriman Email Keluar (Outbound SMTP):** Kemampuan mengirim atau membalas email ke server luar via port 25/465/587. | Port 25 outbound diblokir oleh Tencent Cloud (`F1`); memerlukan prosedur unblock berbelit atau relay SMTP eksternal berbayar; risiko reputasi IP spam. | Penyelesaian `OQ-SMTP-OUT-001` / Persetujuan Owner |
| **OOS-MUL-02** | **Multi-Tenancy Komersial Publik:** Pendaftaran mandiri publik, sistem kuota per organisasi, dan isolasi tenant tingkat enterprise. | Menambah kompleksitas arsitektur secara signifikan; risiko abuse spam publik sangat tinggi; target rilis MVP adalah privat single-owner (`A-REQ-001`). | Keputusan Strategis Pasca-MVP |
| **OOS-BIL-03** | **Sistem Pembayaran & Billing (Subscription):** Integrasi payment gateway (Stripe/Midtrans), invoice, dan paket langganan berbayar. | Platform MVP berstatus self-hosted non-komersial untuk penggunaan mandiri. | Model Bisnis Komersial (TBD) |
| **OOS-API-04** | **Public Developer REST API & Webhook:** Dokumentasi API terbuka, manajemen API token publik, dan custom webhook push. | Pengujian awal cukup melalui bot Telegram dan dashboard web internal. | Fase 2 Otomatisasi QA |
| **OOS-APP-05** | **Aplikasi Mobile Asli (iOS / Android Native App):** Pembuatan aplikasi seluler dedicated. | Kebutuhan akses seluler sudah terpenuhi sepenuhnya secara efisien melalui Telegram Bot. | Fase Masa Depan |
| **OOS-ENT-06** | **Stalwart Masked Email Native Integration:** Penggunaan fitur masked email bawaan Stalwart. | Fitur ini berstatus Enterprise-only dan berbayar pada Stalwart v1.0.3 (`F2`). DomiBox MVP menggunakan primitif Community (alias/virtual routing). | `ADR-0003` |

---

## 3. Asumsi-Asumsi Kritis MVP (Critical MVP Assumptions)

Sesuai `docs/02-requirements/requirements-assumptions-register.md`:
1. **`A-REQ-001` (Single-Tenant / Private Owner):** Sistem dijalankan untuk satu pemilik atau kelompok internal tepercaya.
2. **`A-REQ-002` (Akses Kontrol DNS):** Pemilik memiliki wewenang mengelola DNS domain pilot `sintaksis.biz.id` di Cloudflare DNS untuk mengarahkan MX ke IP VPS Tencent Cloud (`43.153.206.84`).
3. **`A-REQ-003` (VPS IP Publik & Ketersediaan Port):** VPS memiliki IP publik statis dan port TCP/25 inbound tidak diblokir oleh penyedia cloud di tingkat security group jaringan (`F6`).
4. **`A-REQ-004` (Inbound-Only Sufficiency):** Kebutuhan utama penerimaan kode verifikasi dan registrasi akun dapat terpenuhi secara tuntas tanpa kapabilitas pengiriman email keluar (*inbound-only is sufficient for MVP validation*).

---

## 4. Batasan Teknis & Operasional (Constraints)

1. **Batasan Memori & Komputasi VPS:** Server hanya memiliki RAM total 3.6 GiB (3.0 GiB available saat inspeksi) dan 2 vCPU. Seluruh container (DomiBox Core, Stalwart Mail Server, Database PostgreSQL/SQLite, Caddy/Reverse Proxy) tidak boleh mengonsumsi lebih dari 1.5 GiB RAM pada kondisi operasional normal.
2. **Ketiadaan Tabrakan Port RustFS:** Container `rustfs/rustfs:1.0.4` yang sudah aktif di VPS pada port loopback `127.0.0.1:9000-9001` tidak boleh diubah, dimatikan, atau diganggu konfigurasinya.
3. **Keterbatasan Primitif Mail Engine Stalwart Community Edition:** Karena fitur *masked email* Stalwart berbayar (*Enterprise*), logika penghitungan masa aktif (TTL), kadaluarsa, dan pembersihan mailbox sementara wajib diimplementasikan oleh engine scheduler DomiBox sendiri melalui manipulasi JMAP/database internal (`F2`, `F4`).
4. **Tanpa Prototype UI Fisik Pra-Syarat:** Sesuai kebijakan tata kelola, tidak ada klaim prototype visual Figma atau kode antarmuka yang dibuat sebelum spesifikasi PRD dan arsitektur disetujui.

---

## 5. Ketergantungan Eksternal (External Dependencies)

| Entitas Ketergantungan | Komponen Terkait | Tingkat Ketergantungan | Risiko & Dampak Kegagalan |
| --- | --- | --- | --- |
| **Tencent Cloud Network / SG** | Port 25 Inbound | Kritis (Blocker) | Jika port 25 inbound diblokir provider, email eksternal tidak dapat masuk sama sekali (`RISK-001`). |
| **Cloudflare DNS Authority** | Domain `sintaksis.biz.id` | Kritis | Keterlambatan perambatan record MX atau konflik konfigurasi Email Routing Cloudflare (`F3`) menyebabkan kegagalan routing email. |
| **Telegram Bot API Platform** | Bot Notifikasi (`BOT-001`) | Tinggi | Jika API Telegram mengalami gangguan atau terkena rate limit, notifikasi instan beralih ke fallback Web Dashboard. |
| **Stalwart Mail Server Release** | Mail Core Engine (`v1.0.3`) | Kritis | Stabilitas daemon Rust Stalwart di Linux Ubuntu 24.04.5 LTS. |

---

## 6. Penyelarasan Pertanyaan Terbuka (Open Questions Alignment)

Bagian ini menautkan cakupan MVP dengan isu tata kelola pada `docs/00-governance/open-questions.md`:

| ID Pertanyaan | Ringkasan Isu Terbuka | Dampak Terhadap Batasan MVP | Status Resolusi pada Dokumen Ini |
| --- | --- | --- | --- |
| **`Q-001`** | Bukti primer untuk Problem-Value Research belum ditemukan. | Spesifikasi kebutuhan bisnis (`BR-001` s/d `BR-004`) disusun berbasis hipotesis terstruktur. | Ditandai `PROPOSED` / `ASSUMPTION`; tidak menghambat pembekuan batasan teknis MVP. |
| **`Q-002`** | Bukti komparatif kompetitor sebagian besar berstatus placeholder. | Benchmark UX diturunkan dari analisis pola produk sejenis (1secmail, SimpleLogin, DuckDuckGo EP). | Ditandai transparan sebagai input hipotesis pembanding. |
| **`Q-003`** | **Eksplisit Batas Cakupan MVP DomiBox:** Apakah temporary-only atau hybrid (temp + permanent)? | **Teresolusi di level PRD/Scope:** MVP mencakup Temporary Mailbox penuh (prioritas utama) ditambah penyediaan Alias/Mailbox Permanen terbatas untuk akun bernilai tinggi. Fitur outbound, billing, dan multi-tenant publik resmi dikeluarkan dari MVP (`OOS-OUT-01` s/d `OOS-BIL-03`). |
| **`Q-004`** | Model identitas & autentikasi pengguna tunggal (Single Owner Auth). | Memilih antara kunci API sederhana, sesi berbasis cookie terproteksi password, atau pairing token Telegram. | Ditentukan dalam PRD/SRS melalui mekanisme Admin Secret Token / Passkey (`SEC-002`). |

---

## 7. Kriteria Kesiapan Rilis MVP (MVP Release Gate Criteria)

Sebelum rilis MVP dinyatakan siap digunakan oleh pemilik (*Go-Live Ready*), sistem wajib memenuhi kriteria gerbang berikut:
1. **Gate 1 (Inbound Verification):** Pengujian pengiriman email dari minimal 3 penyedia besar (Gmail, Outlook/Hotmail, Yahoo) ke alamat `test@sintaksis.biz.id` berhasil diterima dan dicatat dalam log dalam waktu ≤ 3 detik.
2. **Gate 2 (OTP Extraction Accuracy):** Pengujian dengan 20 variasi email registrasi verifikasi nyata menunjukkan parser OTP berhasil mengekstrak kode dengan akurasi minimal 95% (minimal 19 dari 20 kode benar).
3. **Gate 3 (Telegram Notification End-to-End):** Pesan email masuk memicu notifikasi bot Telegram dengan tombol salin OTP yang berfungsi dalam waktu ≤ 2 detik sejak email diterima MTA.
4. **Gate 4 (TTL Auto-Purge Precision):** Mailbox sementara dengan TTL 10 menit terbukti tidak lagi menerima email baru setelah menit ke-10, dan isi pesan dibersihkan dari penyimpanan sesuai jadwal retensi.
5. **Gate 5 (Zero Secret Leakage):** Tidak ada kebocoran kunci rahasia (*secret tokens/API keys*) pada repositori kode atau log audit publik.
