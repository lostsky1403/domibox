# Business Requirements Document (BRD) - DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/ReqCore | `docs/00-governance/project-charter.md`<br>`docs/00-governance/documentation-standards.md`<br>`docs/00-governance/open-questions.md`<br>`docs/00-governance/decision-log.md`<br>`docs/01-product/product-vision.md`<br>`docs/01-product/mvp-scope.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/02-requirements/traceability/traceability-matrix.md` |

---

## 1. Pendahuluan & Ringkasan Eksekutif (Executive Summary)

### 1.1 Konteks Bisnis & Latar Belakang
Dalam aktivitas rekayasa perangkat lunak, pengujian otomatisasi jaminan kualitas (QA), operasional sysadmin, dan interaksi online pribadi, pengguna terus-menerus diwajibkan memberikan alamat email untuk mendaftar akun, menguji skenario verifikasi identitas, atau menerima kode *One-Time Password* (OTP). Ketergantungan pada penyedia email publik gratis (seperti 10minutemail, Guerrilla Mail, atau Temp-Mail) memicu sejumlah kendala operasional dan risiko serius:
1. **Pemblokiran Domain Reputasi Rendah:** Domain publik layanan email sementara telah masuk dalam daftar hitam (*blacklist*) ribuan penyedia SaaS, staging sandbox, dan gerbang otentikasi.
2. **Ketiadaan Privasi & Keamanan:** Kotak masuk pada layanan gratis kerap bersifat publik atau dapat diakses siapa pun yang mengetahui nama mailbox, memicu paparan tautan verifikasi atau OTP kepada pihak ketiga.
3. **Ketergantungan Eksternal & Vendor Lock-In:** Pengguna tidak dapat menggunakan domain kustom terpercaya milik sendiri secara mandiri (*self-hosted*) dengan jaminan kedaulatan data penuh.

**DomiBox** dirancang sebagai platform manajemen email multi-domain mandiri (*self-hosted private platform*) yang memadukan kapabilitas *temporary mailbox* berbasis batas waktu kedaluwarsa (TTL) dan *permanent mailbox* terbatas untuk domain kustom pengguna.

### 1.2 Sasaran Proyek (Project Goals)
Merujuk pada `docs/00-governance/project-charter.md`, BRD ini menopang empat sasaran strategis:
- **`GOAL-001`:** Penyediaan platform mailbox mandiri & multi-domain fleksibel.
- **`GOAL-002`:** Penerimaan dan ekstraksi email masuk secara cepat, andal, dan aman.
- **`GOAL-003`:** Kemudahan akses multi-kanal terintegrasi (Web Dashboard & Telegram Bot).
- **`GOAL-004`:** Tata kelola operasional, audit, dan retensi data yang transparan dan patuh privasi.

---

## 2. Pemangku Kepentingan & Nilai Bisnis (Stakeholders & Business Value)

### 2.1 Matriks Pemangku Kepentingan
Berdasarkan `docs/01-product/stakeholder-map.md` dan `docs/01-product/personas-and-user-segments.md`:

| ID Stakeholder | Peran / Segmen | Kepentingan Utama | Nilai Bisnis yang Diterima |
| --- | --- | --- | --- |
| **STK-001** | Project Sponsor & Owner | Kedaulatan data, kepatuhan arsitektur mandiri pada VPS pribadi, efisiensi biaya infrastruktur. | Platform email mandiri yang beroperasi efisien pada VPS existing tanpa biaya langganan berulang. |
| **STK-002** | Software Engineer & QA Automation Tester | Pembuatan mailbox sekali pakai secara cepat untuk verifikasi alur reg/test dan ekstraksi OTP otomatis. | Siklus pengujian regresi dan verifikasi akun lebih cepat, isolasi akun uji coba tanpa risiko spam. |
| **STK-003** | Security & Privacy Conscious User | Perlindungan alamat email primer dari pelacakan lintas situs (*profiling*) dan pemaparan kebocoran data. | Anonimitas selektif dan pemisahan identitas dengan domain milik sendiri yang terisolasi. |
| **STK-004** | System / Abuse Administrator | Pemantauan beban server VPS, pencegahan serangan kamus/spam, pembersihan data kedaluwarsa otomatis. | Operasional server yang stabil, aman dari kehabisan memori/disk (*anti-exhaustion*), dan audit log yang akuntabel. |

---

## 3. Kebutuhan Bisnis Inti (Core Business Requirements — `BR-*`)

Tabel kebutuhan bisnis ini mendefinisikan kapabilitas tingkat tinggi, relasi sasaran piagam, stakeholder sasaran, proposisi nilai, dan status verifikasi bukti sesuai `docs/00-governance/documentation-standards.md`.

| ID BR | Pernyataan Kebutuhan Bisnis | Sasaran Piagam (`GOAL`) | Stakeholder Sasaran | Proposisi Nilai & Justifikasi Bisnis | Status Bukti | Rujukan Risiko & Masalah |
| --- | --- | --- | --- | --- | --- | --- |
| **BR-001** | Sistem harus memungkinkan pemilik sistem mengelola domain kustom pribadi serta membuat alamat email sementara (*temporary mailbox*) dan permanen (*persistent aliases*) secara fleksibel. | `GOAL-001` | STK-001, STK-002, STK-003 | Menghilangkan ketergantungan pada penyedia disposable email pihak ketiga; menggunakan domain bereputasi tinggi yang tidak diblokir oleh layanan verifikasi pihak ketiga. | `PROPOSED` | `RISK-001`, `RISK-004`, `Q-001`, `Q-003` |
| **BR-002** | Sistem harus memproses email masuk (*inbound mail*) secara real-time dan mengekstrak kode verifikasi/OTP serta tautan aktivasi secara otomatis dan akurat. | `GOAL-002` | STK-002, STK-003 | Memangkas friksi pengguna dari membaca keseluruhan badan email panjang menjadi penyalinan kode OTP instan (*one-click copy*), mempercepat proses pendaftaran/pengujian. | `PROPOSED` | `RISK-005`, `Q-001`, `ux-pattern-benchmark.md` |
| **BR-003** | Sistem harus menyediakan interaksi multi-kanal melalui antarmuka Web Dashboard responsif dan bot Telegram untuk notifikasi instan serta aksi cepat. | `GOAL-003` | STK-002, STK-003, STK-004 | Memberikan kenyamanan mobilitas tinggi; pengguna dapat menerima kode OTP atau membuat alamat email baru langsung dari aplikasi perpesanan tanpa harus selalu membuka peramban web. | `PROPOSED` | `RISK-006`, `Q-004`, `ux-pattern-benchmark.md` |
| **BR-004** | Sistem harus menjamin kedaulatan data, isolasi akses pesan, pembersihan otomatis data kedaluwarsa (*auto-purge*), dan jejak audit yang akuntabel pada infrastruktur VPS mandiri. | `GOAL-004` | STK-001, STK-004 | Memastikan kepatuhan privasi data, mencegah kehabisan kapasitas penyimpanan VPS (disk/memory exhaustion), serta melindungi sistem dari akses tanpa izin. | `VERIFIED` | `RISK-004`, `RISK-005`, `RISK-007`, `mail-infrastructure-suitability.md` |

---

## 4. Analisis Kelayakan & Batasan Batas MVP (Feasibility & MVP Boundaries)

### 4.1 Keselarasan Batasan MVP (`Q-003`)
Merujuk pada keputusan arsitektur dan penentuan batasan cakupan `docs/01-product/mvp-scope.md`:
1. **In-Scope Bisnis (MVP):**
   - Penerimaan email masuk (*inbound-only*) pada port 25 / relay terkonfigurasi.
   - Manajemen domain kustom (pilot: `sintaksis.biz.id`).
   - Mailbox sementara dengan TTL otomatis (10 menit, 1 jam, 24 jam, kustom).
   - Mailbox permanen terbatas untuk admin single-owner.
   - Parser dan ekstraktor kode OTP / magic link.
   - Web Dashboard responsif & integrasi bot Telegram satu arah/dua arah terpasang (*paired*).
   - Scheduler pembersihan data kedaluwarsa (*auto-purge*).
2. **Out-of-Scope Bisnis (Fase 2 / Pasca-MVP):**
   - Pengiriman email keluar (*outbound SMTP submission*) ke server pihak ketiga (dibatasi oleh kebijakan port 25 outbound cloud `F1` / `RISK-007`).
   - Sistem tagihan (*billing*), kuota berbayar, dan pendaftaran publik multi-tenant (`A-001`, `Q-003`).
   - Aplikasi mobile native (Android / iOS).

### 4.2 Analisis Kesenjangan Bukti (Evidence Gaps & Assumptions)
Sesuai ketetapan tata kelola `DEC-003`:
- **`Q-001` (Problem-Value Research Gap):** Angka metrik konversi dan pain point bisnis kuantitatif ditandai sebagai `ASSUMPTION` / `PROPOSED` karena dokumen sumber primer `docs/09-research/problem-value-research.md` berstatus placeholder gap.
- **`Q-002` (Competitive Benchmark Gap):** Perbandingan matriks fitur kompetitor komersial pada `docs/09-research/competitive-comparative-research.md` merupakan estimasi terstruktur yang memerlukan validasi empiris lanjutan.

---

## 5. Kriteria Keberhasilan Bisnis (Business Success Criteria)

Keberhasilan implementasi kebutuhan bisnis ini akan diukur melalui parameter kuantitatif yang berstatus `PROPOSED` (menunggu pengujian rilis pertama):
1. **Efisiensi Waktu Pengujian QA:** Penurunan durasi siklus pengujian pendaftaran akun baru hingga ≥ 50% dibandingkan penggunaan email manual.
2. **Tingkat Keandalan Penerimaan (Inbound Delivery Rate):** Keberhasilan penerimaan email masuk dari domain SaaS eksternal sah mencapai ≥ 99.0%.
3. **Akurasi Deteksi OTP:** Minimal 95% kode OTP pada email uji coba berhasil diekstraksi ke antarmuka ringkas.
4. **Stabilitas Sumber Daya Mandiri:** Platform beroperasi stabil pada VPS spesifikasi 2 vCPU / 3.6 GiB RAM dengan alokasi memori DomiBox Core < 600 MB.

---

## 6. Keterlacakan ke Fase Perancangan (Downstream Traceability)
Kebutuhan bisnis ini diturunkan secara langsung ke dalam artefak rekayasa berikutnya. Identitas kunci modul mengikuti Skema ID Kanonikal (DEC-001) dan dirinci pada `docs/02-requirements/functional-specs/01..07-*.md` (`FR-*` = alias pengelompokan SRS):
- `BR-001` → `DOM-001..005` (Domain), `MBX-001..005` (Mailbox & Lifecycle), `SRS.md` §3.1–3.2, `ADR-001`, `ADR-002`.
- `BR-002` → `INB-001..005` (Inbox & parsing/sanitasi), `OTP-001..005` (Ekstraksi & penyajian OTP/magic link), `SRS.md` §3.3–3.4, `ADR-003`, `ADR-004`.
- `BR-003` → `BOT-001..005` (Telegram), `WEB-001..005` (Web Dashboard), `SRS.md` §3.5–3.6, `ADR-005`, `ADR-006`.
- `BR-004` → `OPS-001..005` (Autentikasi admin, auto-purge, health, rate limit, audit), `NFR-001` s/d `NFR-012`, `SEC-001` s/d `SEC-012`, `SRS.md` §3.7, `ADR-007` s/d `ADR-012`.
