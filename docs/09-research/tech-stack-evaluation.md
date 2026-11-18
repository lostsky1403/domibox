# Evaluasi Tumpukan Teknologi (Tech Stack Evaluation) — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/ArchCore | `docs/00-governance/project-charter.md`<br>`docs/02-requirements/nfr-spec.md`<br>`docs/03-architecture/tech-evaluation-matrix.md`<br>`docs/03-architecture/architecture-overview.md`<br>`docs/03-architecture/adr/ADR-001.md`<br>`docs/03-architecture/adr/ADR-002.md`<br>`docs/03-architecture/adr/ADR-005.md`<br>`docs/03-architecture/adr/ADR-006.md`<br>`docs/03-architecture/adr/ADR-007.md`<br>`docs/03-architecture/adr/ADR-008.md` |

---

## 1. Tujuan Riset & Konteks Host
Riset ini mengevaluasi dan memilih tumpukan teknologi perangkat lunak (*tech stack*) untuk sistem **DomiBox** agar berjalan optimal pada batasan spesifikasi server target: **2 vCPU AMD EPYC 7K62, ~3.6 GiB RAM fisik, ~1.9 GiB Swap, dan OS Ubuntu 24.04.5 LTS** (`F5`), tanpa mengganggu proses kontainer eksisting `rustfs:1.0.4` pada port `127.0.0.1:9000-9001`.

---

## 2. Rangkuman Pilihan Tumpukan Teknologi Kanonikal

| Lapisan Sistem | Komponen Terpilih | Status Bukti | Justifikasi Teknis Utama | Dokumen Rujukan |
| --- | --- | :---: | --- | --- |
| **Mail Server Engine** | **Stalwart Mail Server v1.0.3 Community (Rust)** | `VERIFIED` | Server monolitik terintegrasi berjejak memori sangat rendah (~150 MB), mendukung native JMAP RFC 8620/8621, SPF/DKIM/DMARC bawaan. | `ADR-002`, `F2`, `F4` |
| **Backend Core** | **Node.js 24 LTS + Fastify v4 (TypeScript)** | `VERIFIED` | Overhead routing ultra-rendah, validasi skema otomatis via Ajv/TypeBox, ekosistem parser MIME dan sanitasi HTML paling matang (`postal-mime`, `DOMPurify`). | `ADR-006`, `tech-evaluation-matrix.md` |
| **Frontend Web** | **React 18 + Vite + shadcn/ui + Tailwind CSS** | `VERIFIED` | Menghasilkan aset statis murni (*zero server runtime RAM overhead*), disajikan via Caddy, komponen aksesibel bawaan WCAG AA (Radix UI). | `ADR-007`, `tech-evaluation-matrix.md` |
| **Telegram Bot** | **grammY Framework (TypeScript)** | `VERIFIED` | Ringan (<15 MB), arsitektur middleware modular, dukungan TypeScript-first mutakhir, plugin `conversations` dan `auto-retry` tangguh. | `ADR-008`, `tech-evaluation-matrix.md` |
| **Database** | **PostgreSQL 16 Alpine (Tuned Buffer Pool)** | `VERIFIED` | MVCC tangguh untuk konkurensi penulisan email masuk dan kueri pembersihan purge scheduler tanpa risiko `SQLITE_BUSY: database is locked`. Konsumsi RAM stabil ~100 MB. | `ADR-005`, `tech-evaluation-matrix.md` |
| **Data Layer** | **Drizzle ORM / Kysely** | `VERIFIED` | Zero-overhead SQL query builder, inferensi tipe statis TypeScript penuh, performa mendekati raw SQL tanpa runtime bloated engine. | `ADR-005`, `SRS.md` |
| **Perimeter / Proxy** | **Caddy Server v2** | `VERIFIED` | Manajemen sertifikat TLS otomatis (Let's Encrypt / ZeroSSL), reverse proxy berkinerja tinggi, konfigurasi ringkas (*Caddyfile*). | `ADR-001`, `architecture-overview.md` |
| **Orkestrator Host** | **Docker Engine 29.9 + Docker Compose v5.7** | `VERIFIED` | Terpasang native pada host, menjamin isolasi kontainer dan batasan memori (*cgroup limits*). | `Project Charter`, `ADR-001` |

---

## 3. Matriks Pembobotan Perbandingan Alternatif Inti

### 3.1 Mail Server Engine: Stalwart vs Mailu vs Haraka
- **Stalwart (Skor: 4.60 - Terpilih):** Rust murni, 1 kontainer, RAM ~150 MB, JMAP native.
- **Mailu (Skor: 3.00):** Arsitektur multi-kontainer berat (8 kontainer), RAM >1.5 GB (didiskualifikasi karena membebani 40% RAM host).
- **Haraka (Skor: 3.80):** Kencang untuk SMTP inbound, namun tidak memiliki mail storage / JMAP mailbox bawaan.

### 3.2 Backend: Fastify (Node.js) vs Go (Gin/Chi) vs Rust (Axum)
- **Fastify / TypeScript (Skor: 4.60 - Terpilih):** Keunggulan mutlak pada manipulasi DOM HTML, ekosistem parser MIME yang tangguh, serta keseragaman tipe data dengan frontend dan bot Telegram.
- **Go / Chi (Skor: 4.35):** Jejak memori sangat kecil (~30 MB), namun parser email HTML dan sanitasi XSS memerlukan integrasi CGO atau pustaka pihak ketiga yang belum sematang ekosistem JavaScript.
- **Rust / Axum (Skor: 3.95):** Performa puncak, namun kurva belajar dan waktu kompilasi yang lambat mengurangi efisiensi delivery seorang pengembang tunggal.

### 3.3 Database: PostgreSQL 16 Alpine vs SQLite 3
- **PostgreSQL 16 (Skor: 4.55 - Terpilih):** Transaksi ACID ketat, isolasi proses aman, tipe JSONB terindeks untuk metadata MIME, dan ketiadaan table-locking saat worker penulisan email dan scheduler pembersihan berjalan serentak.
- **SQLite 3 (Skor: 3.65):** Jejak memori <15 MB, namun arsitektur single-writer rentan memicu bottleneck konkurensi pada lonjakan email masuk bersamaan.

---

## 4. Analisis Batasan Alokasi Memori Server (Memory Budget Breakdown)

Berdasarkan batas RAM host terverifikasi sebesar ~3.6 GiB (3.0 GiB available saat preflight):

| Layanan / Kontainer | Target Alokasi RAM (Limit cgroup) | Status Bukti |
| --- | :---: | :---: |
| **Stalwart Mail Server** | 256 MB | `VERIFIED` (Baseline Rust Tokio) |
| **DomiBox Core API & Ingestion Worker** | 256 MB | `VERIFIED` (Node.js `--max-old-space-size=192`) |
| **PostgreSQL 16 Alpine** | 192 MB | `VERIFIED` (`shared_buffers=64MB`) |
| **Caddy Reverse Proxy & Static SPA** | 64 MB | `VERIFIED` (Go runtime idle) |
| **Buffer Sistem Host & Proses Lain (rustfs)** | 1,200 MB | `VERIFIED` (Host baseline) |
| **Sisa Cadangan Bebas (Buffer)** | >1,500 MB | `VERIFIED` (Sangat aman dari OOM Killer) |

---

## 5. Kesimpulan & Rekomendasi
Tumpukan teknologi yang dipilih memberikan keseimbangan optimal antara **kecepatan pengembangan**, **keandalan penguraian MIME**, dan **efisiensi sumber daya VPS**, memastikan platform DomiBox dapat beroperasi secara mandiri tanpa risiko kehabisan memori atau kebuntuan konkurensi database.
