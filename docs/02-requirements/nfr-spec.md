# Non-Functional Requirements Specification (NFR-Spec) - DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/ReqCore | `docs/00-governance/project-charter.md`<br>`docs/00-governance/documentation-standards.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/01-product/mvp-scope.md`<br>`docs/02-requirements/brd.md`<br>`docs/02-requirements/srs.md`<br>`docs/02-requirements/traceability/traceability-matrix.md` |

---

## 1. Pendahuluan & Filosofi Kualitas Sistem (System Quality Philosophy)

Dokumen ini mendefinisikan persyaratan kualitas, atribut arsitektur, dan kriteria kinerja non-fungsional (*Non-Functional Requirements* / NFR) untuk sistem **DomiBox**. Seluruh kriteria kuantitatif dirumuskan dengan berpijak pada batasan lingkungan infrastruktur riil yang telah terverifikasi:
- **Spesifikasi Server Target (`vps-tencent3b`):** 2 vCPU AMD EPYC 7K62, total RAM 3.6 GiB (3.0 GiB available), swap 1.9 GiB, disk 59 GB (50 GB free), Docker Engine 29.9.3, Compose v5.7.0.
- **Prinsip Kejujuran Bukti:** Mengingat pengujian beban (*load testing*) dan benchmark formal belum dilaksanakan pada lingkungan riil (`F5` / `Q-001`), parameter kuantitatif yang belum divalidasi secara empiris ditandai secara tegas dengan status bukti `PROPOSED` atau `ASSUMPTION`.

---

## 2. Taksonomi Kebutuhan Non-Fungsional (NFR Taxonomy)

Kebutuhan non-fungsional diklasifikasikan ke dalam 7 dimensi kualitas sistem utama:
1. **Kinerja & Latensi (Performance & Latency)**
2. **Ketersediaan & Keandalan (Availability & Reliability)**
3. **Efisiensi Sumber Daya & Kapasitas (Resource Efficiency & Scalability)**
4. **Keamanan & Ketahanan Sistem (System Security & Resilience)**
5. **Kemudahan Pemeliharaan & Evolusi (Maintainability & Extensibility)**
6. **Usabilitas & Aksesibilitas (Usability & Accessibility)**
7. **Observabilitas & Kepatuhan Audit (Observability & Auditability)**

---

## 3. Matriks Kebutuhan Non-Fungsional Rinci (`NFR-*`)

| ID NFR | Kategori / Atribut | Pernyataan Kebutuhan Non-Fungsional | Parameter Ukuran & Target Kuantitatif | Metode Pengujian & Verifikasi | Prioritas | Induk Kebutuhan | Status Bukti |
| --- | --- | --- | --- | --- | :---: | :---: | :---: |
| **NFR-001** | Ketersediaan Sistem (*Availability*) | Sistem harus menjamin ketersediaan layanan penerimaan email masuk (*inbound SMTP listener*) dan antarmuka web selama jam operasional normal. | *Uptime* sistem $\ge 99.5\%$ per bulan kalender (di luar jendela pemeliharaan terjadwal). Maksimal *downtime* tak terencana $\le 3.6$ jam/bulan. | Pemantauan berkala (*health check ping*) setiap 60 detik dari probe eksternal. | **Wajib** | `BR-001`, `FR-001` | `PROPOSED` |
| **NFR-002** | Performa Pembuatan Mailbox (*Creation Latency*) | Sistem harus mampu memproses permintaan pembuatan alamat mailbox baru (sementara atau permanen) secara instan tanpa jeda yang mengganggu pengguna. | Latensi respon pembuatan mailbox $\le 1.5$ detik pada persentil 95 (P95) dan $\le 2.0$ detik pada P99 di bawah beban 5 req/detik. | Pengujian beban sintetis API (*k6 / autocannon*) pada endpoint `/api/v1/mailboxes`. | **Wajib** | `BR-001`, `FR-002` | `PROPOSED` |
| **NFR-003** | Integritas Penyimpanan (*Data Integrity*) | Sistem harus menjamin integritas data email permanen dan mencegah korupsi atau kehilangan pesan selama kuota disk masih mencukupi. | *Zero data loss* ($0\%$ data hilang) untuk pesan yang telah berhasil diterima dengan status SMTP 250 OK pada mailbox permanen aktif. | Validasi konsistensi basis data dan verifikasi checksum badan pesan pasca penyimpanan. | **Penting** | `BR-001`, `FR-003` | `PROPOSED` |
| **NFR-004** | Latensi Pemrosesan Inbound (*Inbound Latency*) | Waktu yang dibutuhkan sistem dari saat penutupan koneksi SMTP pengirim hingga pesan tersimpan dan siap diambil oleh klien Web/API. | Latensi pemrosesan inbound $\le 3.0$ detik (P95) untuk ukuran email standar ($\le 500$ KB). | Pencatatan perbandingan timestamp log MTA `RCPT TO` dengan timestamp pesan masuk di basis data. | **Wajib** | `BR-002`, `FR-004` | `PROPOSED` |
| **NFR-005** | Akurasi Deteksi OTP (*Parsing Accuracy*) | Algoritma heuristik ekstraksi harus mampu mendeteksi kode verifikasi numerik dan alfanumerik dari email masuk secara tepat. | Akurasi deteksi kode OTP $\ge 95.0\%$ pada dataset sampel uji (minimal 50 variasi email registrasi SaaS populer). | Pengujian regresi otomatis (*unit/integration test*) menggunakan kumpulan berkas email `.eml` terstandarisasi. | **Wajib** | `BR-002`, `FR-005` | `PROPOSED` |
| **NFR-006** | Kecepatan Notifikasi Bot (*Bot Dispatch Latency*) | Sistem harus segera meneruskan ringkasan email dan kode OTP ke bot Telegram segera setelah pemrosesan pesan selesai. | Latensi pengiriman pesan ke Telegram Bot API $\le 2.0$ detik (P95) dihitung sejak selesainya parsing inbound. | Logging delta waktu eksekusi antrean notifikasi *in-process worker*. | **Wajib** | `BR-003`, `FR-006` | `PROPOSED` |
| **NFR-007** | Performa Web Dashboard (*Frontend Performance*) | Antarmuka pengguna berbasis web harus ringan, cepat dimuat, dan responsif pada perangkat desktop maupun seluler. | *First Contentful Paint* (FCP) $\le 1.5$ detik, *Largest Contentful Paint* (LCP) $\le 2.5$ detik, dan *Cumulative Layout Shift* (CLS) $\le 0.1$. | Audit otomatis menggunakan Google Lighthouse / Core Web Vitals pada jaringan pita lebar 4G/Broadband standar. | **Penting** | `BR-003`, `FR-007` | `PROPOSED` |
| **NFR-008** | Presisi Pembersihan Data (*Purge Precision*) | Proses latar belakang pembersihan mailbox kedaluwarsa harus dieksekusi secara disiplin tanpa membebani IOPS disk berlebihan. | Toleransi keterlambatan penghapusan pesan $\le 300$ detik (5 menit) setelah waktu kedaluwarsa `expires_at` terlewati. | Kueri audit periodik untuk memeriksa keberadaan rekaman kedaluwarsa yang belum dibersihkan. | **Wajib** | `BR-004`, `FR-008` | `PROPOSED` |
| **NFR-009** | Batasan Jejak Memori (*Memory Footprint*) | Seluruh kontainer aplikasi DomiBox (Core Engine, Inbound Worker, DB) tidak boleh memonopoli memori host VPS yang terbatas. | Total konsumsi memori gabungan kontainer DomiBox $\le 600$ MB dalam kondisi beban normal/idle pada host 3.6 GiB RAM. | Pemantauan kontainer runtime secara berkala via metrik `docker stats` dan cgroups memory. | **Wajib** | `BR-004`, `FR-008` | `ASSUMPTION` (Kendala VPS) |
| **NFR-010** | Batasan Ukuran Pesan (*Max Message Size*) | Sistem harus melindungi penyimpanan lokal dan bandwidth jaringan dari banjir payload lampiran email berukuran raksasa. | Batas maksimal ukuran pesan email masuk per transaksi SMTP adalah 15 MB (termasuk enkoding Base64 lampiran). | Konfigurasi batas ukuran SMTP pada engine MTA dan verifikasi penolakan dengan kode SMTP 552 Message Exceeds Fixed Limit. | **Wajib** | `BR-004`, `FR-004` | `VERIFIED` |
| **NFR-011** | Aksesibilitas Antarmuka (*Accessibility - a11y*) | Antarmuka Web Dashboard harus mematuhi standar dasar aksesibilitas web agar mudah dioperasikan dengan papan ketik (*keyboard navigation*). | Memenuhi standar kepatuhan WCAG 2.1 Level AA untuk kontras warna teks dan navigasi fokus papan ketik. | Pengujian aksesibilitas menggunakan kakas otomatis (*axe-core / Lighthouse Accessibility Score* $\ge 90$). | **Fase 2** | `BR-003`, `FR-007` | `PROPOSED` |
| **NFR-012** | Kemudahan Pemulihan Cadangan (*Backup & Recovery*) | Administrator harus dapat melakukan pencadangan data konfigurasi domain dan mailbox permanen dengan prosedur sederhana. | *Recovery Time Objective* (RTO) $\le 30$ menit dan *Recovery Point Objective* (RPO) $\le 24$ jam untuk data persisten non-disposable. | Pengujian simulasi pemulihan data dari berkas cadangan (*cold backup restore test*). | **Penting** | `BR-004`, `OPS-001` | `PROPOSED` |

---

## 4. Analisis Skalabilitas & Kapasitas (Capacity & Scaling Projections)

### 4.1 Batas Beban MVP Terencana (Target MVP Load Envelope)
Berdasarkan keterbatasan satu node VPS Tencent Cloud (`vps-tencent3b`):
- **Jumlah Domain Terdaftar:** Hingga 10 domain kustom aktif.
- **Mailbox Sementara Bersamaan (*Concurrent Active Temp Mailboxes*):** Hingga 500 mailbox aktif bersamaan.
- **Mailbox Permanen Terdaftar:** Hingga 20 mailbox permanen.
- **Laju Aliran Email Masuk (*Inbound Throughput*):** Rata-rata 1–2 email/menit, dengan ketahanan lonjakan (*burst capacity*) hingga 20 email/menit selama 5 menit berturut-turut tanpa kehilangan antrean.
- **Kapasitas Penyimpanan Disk Tersedia:** Alokasi penyimpanan maksimum untuk DomiBox adalah 10 GB dari total 50 GB ruang disk bebas pada VPS.

### 4.2 Prosedur Degradasi Terkendali (*Graceful Degradation*)
1. Jika utilisasi memori kontainer mencapai $> 85\%$ batas batas (misal: $> 510$ MB), sistem mendahulukan pemrosesan teks polos dan menunda parsing lampiran non-esensial.
2. Jika kuota disk tersisa $< 2$ GB, penerimaan email pada mailbox sementara baru dihentikan sementara dengan kode SMTP 452 Insufficient System Storage (meminta pengirim mencoba lagi nanti), sembari memicu siklus pembersihan darurat (*emergency purge*).

---

## 5. Rencana Pengujian Beban & Validasi Kualitas (Verification Strategy)

Setiap NFR yang bertanda `PROPOSED` wajib melalui pengujian terukur sebelum status rilis dinaikkan menjadi `VERIFIED` pada fase pengujian lanjutan (`Phase 6 Quality`):
- `NFR-001`, `NFR-004`: Diverifikasi melalui skenario uji integrasi `TC-001` dan `TC-004`.
- `NFR-002`, `NFR-006`: Diverifikasi melalui uji performa API `TC-002` dan `TC-006`.
- `NFR-005`: Diverifikasi melalui uji akurasi regresi parser `TC-005`.
- `NFR-008`, `NFR-009`: Diverifikasi melalui uji ketahanan scheduler dan pemantauan kontainer Docker `TC-008`.
