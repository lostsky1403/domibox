# Product Requirements Document (PRD) — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-14 | omp-orchestrator/ProductDocs | `docs/00-governance/project-charter.md`<br>`docs/00-governance/documentation-standards.md`<br>`docs/00-governance/open-questions.md`<br>`docs/01-product/product-vision.md`<br>`docs/01-product/personas-and-user-segments.md`<br>`docs/01-product/mvp-scope.md`<br>`docs/01-product/stakeholder-map.md`<br>`docs/02-requirements/traceability/traceability-matrix.md`<br>`docs/09-research/mail-infrastructure-suitability.md`<br>`docs/09-research/ux-pattern-benchmark.md` |

---

## 1. Ringkasan Eksekutif & Latar Belakang (Executive Summary)

### 1.1 Konteks Masalah
Dalam pengembangan perangkat lunak, pengujian otomatisasi QA, dan aktivitas penjelajahan internet sehari-hari, pengguna sering kali diwajibkan memberikan alamat email untuk registrasi akun, verifikasi layanan SaaS, atau penerimaan kode OTP (*One-Time Password*). Praktik membagikan alamat email utama (*primary email*) menimbulkan dampak negatif berupa tumpukan spam, pelacakan data lintas platform (*cross-site profiling*), dan eksposur terhadap kebocoran data (*data breach exposure*).

Layanan email sementara (*disposable temporary email*) publik yang ada saat ini (seperti 1secmail, temp-mail.org, Guerrilla Mail) memiliki kelemahan mendasar:
1. **Pemblokiran Domain Massal:** Domain publik mereka masuk dalam daftar hitam (*blocklists*) penyedia layanan modern (Cloudflare, AWS, Google, GitHub), menyebabkan kegagalan registrasi.
2. **Ketiadaan Kerahasiaan:** Pesan masuk dapat dibaca oleh siapa saja yang mengetahui atau menebak nama inbox publik tersebut.
3. **Risiko "Disposable Mail Trap":** Layanan publik menghapus alamat secara sepihak dalam hitungan menit/jam tanpa opsi pemulihan atau perpanjangan durasi, sehingga akun berharga yang terdaftar berisiko terkunci selamanya.
4. **Kompleksitas Ekstraksi OTP:** Pengguna harus menyegarkan halaman web secara manual, membuka email HTML berat, dan menyalin manual kode verifikasi.

### 1.2 Solusi DomiBox
**DomiBox** adalah platform manajemen mailbox mandiri multi-domain (*self-hosted multi-domain email management platform*) yang dirancang untuk dioperasikan secara privat pada infrastruktur cloud milik sendiri (VPS Tencent Cloud dengan domain kustom `sintaksis.biz.id`). DomiBox menyatukan fleksibilitas mailbox sementara (*disposable/TTL-based*) dan stabilitas mailbox permanen (*persistent aliases*) dengan kapabilitas ekstraksi instan kode OTP dan tautan verifikasi otomatis, yang dihantarkan melalui Web Dashboard responsif dan Bot Telegram interaktif.

---

## 2. Sasaran Produk & Non-Sasaran (Goals & Non-Goals)

### 2.1 Sasaran Produk (Goals)
- **GOAL-001 (Private Multi-Domain Mailbox Engine):** Menyediakan kemampuan membuat dan mengelola mailbox sementara (berbasis masa aktif/TTL) dan mailbox permanen di bawah domain kustom milik pengguna sendiri guna menghindari pemblokiran daftar hitam domain publik.
- **GOAL-002 (Real-Time Inbound & Instant OTP Extraction):** Menerima email masuk secara real-time via protokol SMTP standar dan mengekstrak kode verifikasi (OTP) serta tautan aktivasi (*magic link*) secara otomatis dalam waktu ≤ 3 detik sejak email diterima MTA.
- **GOAL-003 (Multi-Channel Delivery):** Menyediakan antarmuka interaksi ganda yang seamless: Bot Telegram untuk notifikasi instan dan aksi cepat *one-click copy*, serta Web Dashboard responsif untuk penjelajahan pesan mendalam dan manajemen konfigurasi.
- **GOAL-004 (Strict Privacy & Operational Governance):** Mengisolasi data pesan per sesi/token, menerapkan pembersihan otomatis (*auto-purge*) sesuai TTL, serta menolak email yang ditujukan ke mailbox yang sudah kedaluwarsa langsung pada level protokol SMTP (`RCPT TO reject`).

### 2.2 Bukan Sasaran MVP (Non-Goals / Out-of-Scope)
- **N-GOAL-001 (No Outbound Email Sending):** Tidak menyediakan kapabilitas pengiriman email keluar (*outbound SMTP*) pada rilis MVP karena adanya pembatasan port 25 keluar oleh Tencent Cloud (`F1`) dan prioritas pada penerimaan kode verifikasi (`OOS-OUT-01`).
- **N-GOAL-002 (No Public Multi-Tenant Registration):** Tidak menyediakan sistem registrasi pengguna publik bebas, penagihan (*billing/subscription*), atau pemisahan tenant komersial (`A-REQ-001`).
- **N-GOAL-003 (No Enterprise Masked Email Dependency):** Tidak bergantung pada fitur berbayar *masked email* Stalwart Enterprise Edition (`F2`); seluruh logika siklus hidup alamat dikelola oleh engine aplikasi DomiBox di atas Stalwart Community Edition (`F4`).
- **N-GOAL-004 (No Native Mobile App):** Tidak membangun aplikasi seluler native (Android/iOS); kebutuhan seluler dipenuhi secara optimal melalui Telegram Bot API.

---

## 3. Persona Pengguna & Pemangku Kepentingan (Personas Summary)

Rincian lengkap terdapat pada `docs/01-product/personas-and-user-segments.md` dan `docs/01-product/stakeholder-map.md`.

1. **Dev Dedi (QA & Backend Engineer):** Membutuhkan alamat sementara instan yang tembus form registrasi dan tombol salin OTP cepat untuk memvalidasi alur pendaftaran aplikasi.
2. **Rina Privasi (Privacy-Conscious User):** Membutuhkan mailbox dengan TTL fleksibel atau alias permanen pada domain kustom untuk berlangganan layanan daring tanpa pelacakan pixel.
3. **Budi Sysadmin (Single Owner & Platform Admin):** Pemilik VPS Tencent Cloud yang bertanggung jawab atas kesehatan container, konfigurasi DNS Cloudflare, dan kebersihan penyimpanan server.
4. **Agus Abuse-Ops (Security Sentinel):** Memastikan penolakan pesan masuk liar, sanitasi HTML ketat dari serangan XSS, dan perlindungan token bot.

---

## 4. Kebutuhan Bisnis (Business Requirements — `BR-*`)

| ID Kebutuhan | Nama Kebutuhan Bisnis | Deskripsi & Justifikasi Nilai | Sasaran Terkait | Prioritas | Status Bukti |
| --- | --- | --- | --- | --- | --- |
| **BR-001** | **Manajemen Mailbox Fleksibel Domain Pribadi** | Sistem harus memungkinkan pengguna membuat dan mengelola alamat email sementara (TTL) serta permanen menggunakan domain kustom terverifikasi untuk menghindari penolakan form registrasi akibat blocklist publik. | `GOAL-001` | Wajib | `PROPOSED` (Didukung `VAL-001`) |
| **BR-002** | **Pemrosesan Inbound Real-Time & Ekstraksi OTP** | Sistem harus menerima email masuk secara instan dan mengekstrak kode verifikasi/tautan konfirmasi secara otomatis tanpa mewajibkan pembacaan email lengkap secara manual. | `GOAL-002` | Wajib | `VERIFIED` (Pola UX Benchmark) |
| **BR-003** | **Interaksi Terpadu Multi-Kanal (Web & Bot)** | Sistem harus menyediakan saluran akses melalui Web Dashboard dan Bot Telegram interaktif yang mendukung operasi satu klik untuk pembuatan alamat dan penyalinan OTP. | `GOAL-003` | Wajib | `PROPOSED` (Didukung `VAL-004`) |
| **BR-004** | **Auditabilitas, Keamanan Privasi & Auto-Purge** | Sistem harus mengisolasi data antar sesi pengguna privat, membersihkan data kedaluwarsa secara terjadwal, dan menyediakan log audit yang transparan untuk kepatuhan operasional. | `GOAL-004` | Wajib | `VERIFIED` (Prinsip Keamanan Data) |

---

## 5. Kebutuhan Fungsional (Functional Requirements — `FR-*` / Modul)

Sesuai konvensi kanonikal pada `docs/02-requirements/traceability/traceability-matrix.md`, kebutuhan fungsional dikelompokkan ke dalam modul-modul 3-digit:

### 5.1 Modul Manajemen Domain (`DOM-###`)

| ID Fungsional | Modul / Fitur | Deskripsi Fungsional Detail | Kebutuhan Bisnis | Prioritas | Kriteria Penerimaan Inti |
| --- | --- | --- | --- | --- | --- |
| **FR-001** | **DOM-001**: Konfigurasi & Verifikasi DNS Domain | Sistem harus menyediakan antarmuka untuk mendaftarkan domain kustom (pilot: `sintaksis.biz.id`) dan memverifikasi kesiapan record MX dan TXT verifikasi kepemilikan sebelum domain diaktifkan. | `BR-001` | Wajib | Verifikasi memeriksa status MX record via resolver internal; jika MX mengarah ke IP VPS, status domain berubah menjadi `ACTIVE`. |
| **FR-001.1** | **DOM-002**: Pemeriksaan Konflik DNS Cloudflare | Sistem harus mendeteksi dan memberi peringatan jika domain dikonfigurasi menggunakan Cloudflare Email Routing yang menimpa MX record asli (`F3`). | `BR-001` | Penting | Tampilan peringatan visual muncul jika MX record terdeteksi mengarah ke `route*.mx.cloudflare.net`. |

### 5.2 Modul Siklus Hidup Mailbox Core (`MBX-###`)

| ID Fungsional | Modul / Fitur | Deskripsi Fungsional Detail | Kebutuhan Bisnis | Prioritas | Kriteria Penerimaan Inti |
| --- | --- | --- | --- | --- | --- |
| **FR-002** | **MBX-001**: Pembuatan Mailbox Sementara (TTL) | Pengguna dapat membuat mailbox sementara baru dengan nama acak atau kustom di bawah domain aktif, disertai pilihan durasi TTL (10 menit, 1 jam, 24 jam, 7 hari). | `BR-001` | Wajib | Alamat email instan terbuat dalam ≤ 1.5 detik (`NFR-002`); hitung mundur TTL dimulai seketika. |
| **FR-002.1** | **MBX-002**: Perpanjangan & Penghapusan Mailbox TTL | Pengguna dapat menambah durasi masa aktif mailbox sementara yang sedang berjalan atau menghapusnya secara manual sewaktu-waktu. | `BR-001` | Wajib | Tombol "Extend TTL" menambah masa aktif sesuai pilihan; tombol "Delete" mengubah status menjadi `REVOKED`. |
| **FR-003** | **MBX-003**: Mailbox & Alias Permanen Terbatas | Pengguna dapat membuat alamat email permanen yang tidak memiliki batas waktu kedaluwarsa untuk layanan bernilai tinggi. | `BR-001` | Penting | Mailbox permanen berstatus `PERSISTENT`, tidak terpengaruh oleh auto-purge engine, dengan pembatasan kuota storage (`SEC-003`). |

### 5.3 Modul Pemrosesan Email Masuk (`INB-###`)

| ID Fungsional | Modul / Fitur | Deskripsi Fungsional Detail | Kebutuhan Bisnis | Prioritas | Kriteria Penerimaan Inti |
| --- | --- | --- | --- | --- | --- |
| **FR-004** | **INB-001**: Penerimaan Email Inbound SMTP | Mail engine (Stalwart) harus menerima koneksi SMTP masuk pada port 25 dari server pengirim eksternal dan memverifikasi penerima pada tahap `RCPT TO`. | `BR-002` | Wajib | Jika alamat tujuan valid dan aktif, email diterima (250 OK); jika alamat tujuan kedaluwarsa/tidak terdaftar, koneksi ditolak (550 Recipient Rejected). |
| **FR-004.1** | **INB-002**: Parsing MIME & Dekomposisi Pesan | Sistem mem-parse payload email masuk menjadi komponen terstruktur: headers (From, To, Date, Subject), Plaintext Body, HTML Body, dan daftar metadata lampiran. | `BR-002` | Wajib | Pesan berhasil disimpan ke basis data terindeks dalam waktu ≤ 3 detik sejak penerimaan (`NFR-004`). |
| **FR-004.2** | **INB-003**: Evaluasi Autentikasi Pengirim (SPF/DKIM) | Sistem membaca hasil evaluasi SPF, DKIM, dan DMARC dari header email masuk (`Authentication-Results`) dan menyimpannya sebagai status keamanan pesan. | `BR-004` | Penting | Status SPF/DKIM (Pass/Fail/Neutral) tersimpan dan dapat ditampilkan pada antarmuka pengguna (`SEC-004`). |

### 5.4 Modul Ekstraksi OTP & Pesan Verifikasi (`OTP-###`)

| ID Fungsional | Modul / Fitur | Deskripsi Fungsional Detail | Kebutuhan Bisnis | Prioritas | Kriteria Penerimaan Inti |
| --- | --- | --- | --- | --- | --- |
| **FR-005** | **OTP-001**: Ekstraksi Heuristik Kode OTP | Sistem menjalankan parser regex heuristik pada subjek dan badan email untuk mendeteksi kode verifikasi 4–8 karakter (angka/alfanumerik) dan kata kunci pendamping (e.g., "kode verifikasi", "OTP", "security code"). | `BR-002` | Wajib | Kode OTP berhasil diekstraksi dan disajikan secara terpisah pada metadata pesan dengan target akurasi ≥ 95% (`NFR-005`). |
| **FR-005.1** | **OTP-002**: Deteksi Magic Link & Tombol Konfirmasi | Sistem mengekstrak URL aktivasi akun atau tombol verifikasi primer dari badan email HTML/Plaintext. | `BR-002` | Penting | Tautan verifikasi utama berhasil diisolasi dan disajikan sebagai tautan aksi langsung. |

### 5.5 Modul Integrasi Bot Telegram (`BOT-###`)

| ID Fungsional | Modul / Fitur | Deskripsi Fungsional Detail | Kebutuhan Bisnis | Prioritas | Kriteria Penerimaan Inti |
| --- | --- | --- | --- | --- | --- |
| **FR-006** | **BOT-001**: Perintah Manajemen Mailbox Bot | Bot Telegram mendukung perintah interaktif (`/start`, `/new`, `/list`, `/read`, `/extend`, `/delete`) untuk mengelola mailbox langsung dari jendela chat Telegram. | `BR-003` | Wajib | Respon perintah bot dikirimkan dalam waktu ≤ 1.5 detik sejak pengguna mengirimkan command. |
| **FR-006.1** | **BOT-002**: Notifikasi Real-Time & Inline Copy OTP | Saat email masuk tiba, bot mengirimkan notifikasi ringkasan berisi Pengirim, Subjek, Kode OTP (teks tebal/monospaced), dan Inline Keyboard dengan tombol "Copy OTP". | `BR-003` | Wajib | Notifikasi bot terkirim dalam waktu ≤ 2 detik sejak email selesai diproses (`NFR-006`). |

### 5.6 Modul Web Dashboard (`WEB-###`)

| ID Fungsional | Modul / Fitur | Deskripsi Fungsional Detail | Kebutuhan Bisnis | Prioritas | Kriteria Penerimaan Inti |
| --- | --- | --- | --- | --- | --- |
| **FR-007** | **WEB-001**: Antarmuka Responsif Inbox & Viewer | Antarmuka web responsif (desktop & mobile) yang menampilkan daftar mailbox, daftar email masuk secara real-time, detail pesan, serta tombol aksi cepat salin alamat dan salin OTP. | `BR-003` | Wajib | Waktu muat awal halaman web ≤ 2.0 detik (`NFR-007`); sinkronisasi pesan baru via WebSocket/Polling real-time. |
| **FR-007.1** | **WEB-002**: Sanitasi Kontrol Tampilan HTML Aman | Viewer email web merender HTML di dalam container terisolasi (*sandboxed iframe*) dengan penonaktifan eksekusi skrip, pemblokiran unduhan otomatis, dan pemblokiran gambar eksternal secara default. | `BR-004` | Wajib | Mencegah 100% risiko eksekusi payload XSS dan kebocoran tracking pixel (`SEC-005`, `SEC-007`). |

### 5.7 Modul Operasional, Logging & Scheduler (`OPS-###`)

| ID Fungsional | Modul / Fitur | Deskripsi Fungsional Detail | Kebutuhan Bisnis | Prioritas | Kriteria Penerimaan Inti |
| --- | --- | --- | --- | --- | --- |
| **FR-008** | **OPS-001**: Scheduler Pembersihan Otomatis (Auto-Purge) | Layanan latar belakang terjadwal yang secara berkala (misal: tiap 60 detik) memeriksa mailbox dengan TTL kedaluwarsa, mengubah status routing menjadi nonaktif di mail engine, dan menghapus data email fisik sesuai kebijakan retensi. | `BR-004` | Wajib | Mailbox yang melewati masa aktif berhenti menerima email seketika; pesan terhapus dari storage dalam ≤ 5 menit pasca-kedaluwarsa (`NFR-008`). |
| **FR-008.1** | **OPS-002**: Audit Logging Terstruktur | Pencatatan seluruh kejadian penting sistem (pembuatan mailbox, penerimaan email, penolakan SMTP, pembersihan data, login admin) ke dalam log terstruktur JSON yang tidak dapat dimanipulasi dari UI. | `BR-004` | Wajib | Log audit terekam dengan timestamp ISO-8601 dan identifier sesi (`SEC-008`). |

---

## 6. Kebutuhan Non-Fungsional (Non-Functional Requirements — `NFR-*`)

| ID NFR | Kategori | Parameter Ukuran / Target Kuantitatif | Kebutuhan Bisnis Terkait | Status Bukti |
| --- | --- | --- | --- | --- |
| **NFR-001** | Ketersediaan Sistem | Ketersediaan layanan aplikasi dan penerimaan mail ≥ 99.5% per bulan (di luar pemeliharaan terjadwal). | `BR-001` | `PROPOSED` |
| **NFR-002** | Performa Pembuatan Mailbox | Waktu pembuatan alamat mailbox baru (API / Web / Bot) ≤ 1.5 detik pada persentil 95 (P95). | `BR-001` | `PROPOSED` |
| **NFR-003** | Integritas Data Permanen | Tingkat keberhasilan penyimpanan data email permanen 100% tanpa kehilangan bit (*zero data loss*) selama storage kuota tersedia. | `BR-001` | `PROPOSED` |
| **NFR-004** | Latensi Pemrosesan Email Inbound | Waktu dari penyelesaian koneksi SMTP hingga email tersimpan dan siap dibaca ≤ 3.0 detik (P95). | `BR-002` | `PROPOSED` |
| **NFR-005** | Akurasi Ekstraksi OTP | Rasio ketepatan deteksi kode OTP pada email verifikasi umum ≥ 95% (berdasarkan sampel uji coba). | `BR-002` | `PROPOSED` |
| **NFR-006** | Kecepatan Notifikasi Bot | Latensi penghantaran notifikasi dari selesainya pemrosesan inbound hingga pengiriman ke Telegram Bot API ≤ 2.0 detik (P95). | `BR-003` | `PROPOSED` |
| **NFR-007** | Waktu Muat Antarmuka Web | First Contentful Paint (FCP) Web Dashboard ≤ 1.5 detik dan Total Load Time ≤ 2.0 detik pada jaringan pita lebar standar. | `BR-003` | `PROPOSED` |
| **NFR-008** | Presisi Penjadwalan Retensi | Toleransi keterlambatan eksekusi pembersihan data kedaluwarsa (*purge delay*) ≤ 300 detik (5 menit) dari batas waktu TTL. | `BR-004` | `PROPOSED` |
| **NFR-009** | Batasan Jejak Memori (Resource Footprint) | Total konsumsi RAM aplikasi DomiBox Core + database ≤ 600 MB dalam kondisi normal pada VPS 3.6 GiB RAM. | `BR-004` | `ASSUMPTION` (Berdasarkan kendala `vps-tencent3b`) |

---

## 7. Kontrol Keamanan & Privasi (Security & Privacy Controls — `SEC-*`)

| ID Kontrol | Aspek Keamanan | Spesifikasi Kontrol Teknis | Kebutuhan Terkait | Status Bukti |
| --- | --- | --- | --- | --- |
| **SEC-001** | Validasi Domain Spoofing | Pengecekan ketat DNS TXT verification token sebelum domain diizinkan aktif menerima email masuk guna mencegah pembajakan domain pihak ketiga. | `DOM-001`, `BR-001` | `VERIFIED` |
| **SEC-002** | Isolasi Akses Mailbox | Setiap mailbox sementara dilindungi oleh token sesi atau kunci akses privat acak; pengguna tanpa token dilarang mengakses isi pesan. | `MBX-001`, `BR-004` | `VERIFIED` |
| **SEC-003** | Pembatasan Kuota & Anti-Exhaustion | Batas penyimpanan default per mailbox sementara (maksimum 50 pesan atau 10 MB); penolakan otomatis jika kuota terlampaui untuk melindungi storage VPS. | `MBX-002`, `BR-004` | `PROPOSED` |
| **SEC-004** | Validasi Reputasi Pengirim | Pemeriksaan hasil validasi SPF, DKIM, dan DMARC pada setiap email masuk; pemberian label peringatan (*visual warning*) jika pengirim gagal terotentikasi. | `INB-001`, `BR-004` | `VERIFIED` |
| **SEC-005** | Sanitasi Konten Email & Anti-XSS | Penggunaan pustaka sanitasi HTML ketat (e.g., DOMPurify/ammonia), penonaktifan tag `<script>`, `<iframe>`, atribut berbahaya (`onerror`, `onload`), dan pemblokiran gambar eksternal (*tracking beacons*) secara default. | `OTP-001`, `WEB-001`, `BR-004` | `VERIFIED` |
| **SEC-006** | Autentikasi Pairing Bot Telegram | Mekanisme verifikasi satu kali (*one-time pairing token*) antara akun Web Admin dengan Telegram Chat ID; perintah bot dari Chat ID tidak terdaftar ditolak seketika. | `BOT-001`, `BR-003` | `PROPOSED` |
| **SEC-007** | Proteksi Antarmuka Web (CSP & CSRF) | Implementasi Content Security Policy (CSP) ketat, header HTTP keamanan (`X-Frame-Options`, `X-Content-Type-Options`), proteksi CSRF berbasis token, dan cookie sesi `SameSite=Strict; Secure; HttpOnly`. | `WEB-001`, `BR-004` | `VERIFIED` |
| **SEC-008** | Tamper-Evident Audit Logging | Log audit sistem disimpan pada file log append-only lokal dengan hak akses terbatas root/admin; pencatatan seluruh mutasi data sensitif. | `OPS-001`, `BR-004` | `VERIFIED` |

---

## 8. Metrik Keberhasilan Produk (Success Metrics)

Sesuai `docs/00-governance/documentation-standards.md`, semua metrik target kuantitatif ditandai secara eksplisit status pembuktiannya:

| Kategori Metrik | Indikator Kinerja Utama (KPI) | Nilai Sasaran Target | Status Bukti | Metode Pengukuran |
| --- | --- | --- | --- | --- |
| **Penerimaan Inbound** | Rasio Keberhasilan Penerimaan Email Masuk | ≥ 99.0% dari email terkirim yang sah | `PROPOSED` | Perbandingan log SMTP accepted vs rejected pada alamat aktif |
| **Kecepatan OTP** | Waktu Ekstraksi & Tampilan Kode OTP | ≤ 3.0 detik sejak email masuk | `PROPOSED` | Timestamp log MTA ke timestamp log parser OTP |
| **Akurasi Parsing** | Rasio Deteksi Kode OTP yang Benar | ≥ 95.0% pada email uji coba verifikasi | `PROPOSED` | Validasi silang manual & otomatis pada 50 email sampel |
| **Keterlibatan Bot** | Rasio Penggunaan Aksi via Telegram Bot | ≥ 50.0% dari total operasi generate/copy | `PROPOSED` | Log metrik command bot vs log UI dashboard |
| **Efisiensi Sumber Daya** | Konsumsi Memori Total Aplikasi DomiBox | < 600 MB RAM idle/baseline | `ASSUMPTION` | Pemantauan kontainer Docker via `docker stats` |
| **Kebersihan Data** | Keberhasilan Penghapusan Mailbox Kedaluwarsa | 100% mailbox kadaluarsa terhapus dalam toleransi 5 menit | `PROPOSED` | Pemeriksaan konsistensi DB pasca-jadwal purge |

---

## 9. Penyelarasan Rencana Delivery (14 Epics Alignment)

Sesuai dengan Piagam Proyek (`docs/00-governance/project-charter.md`) dan RTM (`docs/02-requirements/traceability/traceability-matrix.md`), kebutuhan PRD ini diselaraskan dengan kerangka kerja 14 Epic Jira (`DBX-*`):

| ID Epic | Nama Epic Delivery | Lingkup Kebutuhan Terkait | Status Cakupan MVP |
| --- | --- | --- | --- |
| **EPIC-01** | Project Bootstrap & Engineering Governance | `docs/00-governance/*`, RTM, Dokumentasi Dasar | Selesai / Sedang Berjalan |
| **EPIC-02** | Domain Management & DNS Integration | `DOM-001`, `DOM-002`, `FR-001`, `SEC-001` | **Wajib (In-Scope MVP)** |
| **EPIC-03** | Mailbox Core Engine & Lifecycle Management | `MBX-001`, `MBX-002`, `MBX-003`, `FR-002`, `FR-003` | **Wajib (In-Scope MVP)** |
| **EPIC-04** | Inbound Mail Processing & MIME Ingestion | `INB-001`, `INB-002`, `INB-003`, `FR-004`, `SEC-004` | **Wajib (In-Scope MVP)** |
| **EPIC-05** | OTP Extraction & Message Content Analysis | `OTP-001`, `OTP-002`, `FR-005`, `NFR-005` | **Wajib (In-Scope MVP)** |
| **EPIC-06** | Telegram Bot Interface & Quick Actions | `BOT-001`, `BOT-002`, `FR-006`, `SEC-006` | **Wajib (In-Scope MVP)** |
| **EPIC-07** | Web Dashboard & Responsive Inbox Viewer | `WEB-001`, `WEB-002`, `FR-007`, `SEC-005`, `SEC-007` | **Wajib (In-Scope MVP)** |
| **EPIC-08** | Security Hardening & Privacy Isolation | `SEC-001` s/d `SEC-008`, Proteksi Rahasia | **Wajib (In-Scope MVP)** |
| **EPIC-09** | Background Scheduler & Auto-Purge Engine | `OPS-001`, `FR-008`, `NFR-008` | **Wajib (In-Scope MVP)** |
| **EPIC-10** | Observability, Audit Logging & Metrics | `OPS-002`, `FR-008.1`, `NFR-009` | **Wajib (In-Scope MVP)** |
| **EPIC-11** | Quality Assurance, Testing Suite & E2E Validation | Kriteria Uji `TC-001` s/d `TC-008`, Validasi Gate | **Wajib (In-Scope MVP)** |
| **EPIC-12** | Container Deployment & VPS Infrastructure | Konfigurasi Docker Compose VPS Tencent Cloud | **Wajib (In-Scope MVP)** |
| **EPIC-13** | Outbound SMTP & Relaying Infrastructure | `OOS-OUT-01` (Kirim email keluar) | **Fase 2 (Out-of-Scope MVP)** |
| **EPIC-14** | Multi-Tenancy, Public API & Commercial Billing | `OOS-MUL-02`, `OOS-BIL-03`, `OOS-API-04` | **Fase 2 (Out-of-Scope MVP)** |

---

## 10. Catatan Ruang Lingkup UX (UX Scope Note)
Sesuai dengan ketentuan tata kelola proyek:
- **Status Prototype Fisik:** Belum ada prototype visual Figma atau kode antarmuka yang dibuat (*prototype belum dibuat*).
- **Dasar Perancangan Antarmuka:** Perancangan antarmuka Web dan Telegram Bot diturunkan secara murni dari sintesis pola interaksi unggulan yang tervalidasi pada dokumen `docs/09-research/ux-pattern-benchmark.md`:
  1. *Copy-First Navigation:* Penempatan tombol salin alamat dan OTP pada lapisan teratas visual.
  2. *Live Countdown Timer:* Tampilan visual sisa waktu aktif mailbox sementara.
  3. *Zero-Friction Message Peek:* Panel pratinjau instan teks polos pesan sebelum membuka tampilan HTML lengkap.

---

## 11. Manajemen Risiko & Rujukan Riset (Risks & Research Evidence Gaps)

### 11.1 Risiko Utama Produk (`RISK-*`)
1. **`RISK-001` (Blokir Port Jaringan Inbound Cloud):** Port 25 inbound berpotensi diblokir oleh firewall Tencent Cloud. Mitigasi: Eksekusi PoC validasi port 25 (`mail-infrastructure-suitability.md` §10.1) sebelum membekukan konfigurasi.
2. **`RISK-004` (Penyalahgunaan Spam / Dictionary Attack):** Pengirim eksternal membombardir domain dengan jutaan alamat acak. Mitigasi: Penerapan penolakan langsung di tahap `RCPT TO` oleh Stalwart untuk alamat yang tidak aktif (`INB-001`).
3. **`RISK-005` (Injeksi XSS melalui Email HTML):** Pengirim email menyisipkan skrip berbahaya pada badan email. Mitigasi: Isolasi rendering menggunakan sandboxed iframe dan pembersihan DOM berbasis pustaka sanitasi ketat (`SEC-005`).

### 11.2 Keterkaitan dengan Isu Terbuka Tata Kelola (`Q-*`)
1. **`Q-001` (Ketiadaan Riset Masalah Primer Terverifikasi):** Status dokumen `docs/09-research/problem-value-research.md` adalah `PROPOSED/GAP`. PRD ini secara eksplisit menandai seluruh hipotesis masalah sebagai `ASSUMPTION` guna mencegah klaim bukti palsu.
2. **`Q-002` (Ketiadaan Riset Kompetitif Primer Terverifikasi):** Data komparatif kompetitor pada `docs/09-research/competitive-comparative-research.md` diakui sebagai kerangka perbandingan hipotetis berstatus `PROPOSED`.
3. **`Q-003` (Batas Cakupan MVP DomiBox):** Dokumen ini secara resmi mengusulkan resolusi bahwa MVP berfokus pada **Temporary Mailbox (TTL) + Permanent Mailbox Terbatas**, dengan pengecualian tegas terhadap kapabilitas outbound SMTP, billing, dan pendaftaran publik.
