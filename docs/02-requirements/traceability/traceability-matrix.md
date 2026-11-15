# Requirements Traceability Matrix (RTM)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Requirements Lead / Orchestrator (ReqTrace)`  
- `docs/00-governance/project-charter.md`
- `docs/00-governance/documentation-standards.md`
- `docs/00-governance/open-questions.md`
- `docs/00-governance/decision-log.md`
- `docs/02-requirements/requirements-assumptions-register.md`
- `docs/02-requirements/brd.md`
- `docs/02-requirements/srs.md`
- `docs/02-requirements/nfr-spec.md`
- `docs/02-requirements/security-privacy-requirements.md`
- `docs/02-requirements/scope-and-change-control.md`
- `docs/01-product/prd/TEMPLATE_PRD_IMPROVED.md`
- `docs/09-research/mail-infrastructure-suitability.md`
- `docs/09-research/ux-pattern-benchmark.md`
- `docs/09-research/problem-value-research.md`
- `docs/09-research/competitive-comparative-research.md`

---

## 1. Tujuan & Ruang Lingkup (Purpose & Scope)
Dokumen ini berfungsi sebagai kerangka kerja utama (*canonical framework*) keterlacakan kebutuhan (*Requirements Traceability Matrix* / RTM) untuk inisiatif platform **DomiBox**. Matriks ini menghubungkan sasaran piagam proyek (*Project Charter Goals*), Kebutuhan Bisnis (`BR-*`), Kebutuhan Fungsional (`FR-*` / modul `DOM-`, `MBX-`, `INB-`, `OTP-`, `BOT-`, `WEB-`, `OPS-`), Kebutuhan Non-Fungsional (`NFR-*`), Kontrol Keamanan & Privasi (`SEC-*`), Keputusan Arsitektur (`ADR-*`), Rencana Pengujian (`TC-*`), hingga perencanaan rilis dan item Jira (`DBX-*`).

Semua pemetaan yang belum difinalisasi atau masih dalam tahap perumusan spesifikasi ditandai secara eksplisit sebagai `TBD` (*To Be Determined*) atau `PENDING` guna menjamin integritas audit dan menghindari fabrikasi status.

---

## 2. Skema Identifikasi & Konvensi (Canonical ID Conventions)
Sesuai dengan standar dokumentasi pada `docs/00-governance/documentation-standards.md` dan keputusan `DEC-001`:

| Domain | Skema ID | Contoh | Deskripsi |
| --- | --- | --- | --- |
| Sasaran Piagam (Charter Goal) | `GOAL-###` | `GOAL-001` | Sasaran hasil tingkat tinggi dari project charter |
| Kebutuhan Bisnis (Business Req) | `BR-###` | `BR-001` | Kebutuhan bisnis dan justifikasi nilai produk |
| Kebutuhan Fungsional (Umum) | `FR-###` | `FR-001` | Spesifikasi fungsional sistem |
| Modul Domain Management | `DOM-###` | `DOM-001` | Manajemen domain, DNS verification, MX checks |
| Modul Mailbox Core | `MBX-###` | `MBX-001` | Siklus hidup mailbox sementara dan permanen |
| Modul Inbound Mail Processing | `INB-###` | `INB-001` | Penerimaan email masuk, parsing MIME, routing |
| Modul OTP & Message Extraction | `OTP-###` | `OTP-001` | Deteksi kode OTP, link verifikasi, security isolation |
| Modul Bot & Notification | `BOT-###` | `BOT-001` | Integrasi bot Telegram, notifikasi instan |
| Modul Web Dashboard | `WEB-###` | `WEB-001` | Antarmuka pengguna berbasis web (UI/UX) |
| Kebutuhan Non-Fungsional | `NFR-###` | `NFR-001` | Kualitas sistem, SLA, performa, ketersediaan |
| Kontrol Keamanan & Privasi | `SEC-###` | `SEC-001` | Mitigasi risiko, proteksi data, pembatasan akses |
| Keputusan Arsitektur | `ADR-###` | `ADR-001` | Catatan keputusan teknis arsitektur |
| Kasus Uji (Test Case) | `TC-###` | `TC-001` | Rencana dan skenario pengujian verifikasi |
| Risiko | `RISK-###` | `RISK-001` | Risiko proyek/teknis dalam register risiko |
| Pertanyaan Terbuka | `Q-###` | `Q-001` | Isu atau pertanyaan yang belum teresolusi |
| Keputusan Tata Kelola | `DEC-###` | `DEC-001` | Keputusan manajerial/tata kelola dokumentasi |

---

## 3. Matriks Keterlacakan Utama (Forward Traceability Matrix)
Tabel berikut memetakan keterlacakan dari Kebutuhan Tingkat Tinggi hingga Eksekusi dan Verifikasi.

| Sasaran Piagam (`GOAL`) | Kebutuhan Bisnis (`BR`) | Kebutuhan Fungsional / Modul (`FR`/`MOD`) | Kebutuhan Non-Fungsional (`NFR`) | Kontrol Keamanan (`SEC`) | Dasar Riset / Masukan | Arsitektur Terkait (`ADR`) | Rencana Uji (`TC`) | Rencana Delivery (Epic / Story Jira) | Status Bukti & Ketergantungan |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **GOAL-001**: Penyediaan platform mailbox mandiri & multi-domain fleksibel | **BR-001**: Pengguna dapat mengelola alamat email sementara dan permanen dengan domain kustom | **FR-001** / **DOM-001**: Konfigurasi & verifikasi kepemilikan domain kustom (DNS MX/TXT) | **NFR-001**: Ketersediaan layanan verifikasi domain (SLO TBD) | **SEC-001**: Validasi ketat kepemilikan domain guna mencegah domain spoofing | `docs/09-research/mail-infrastructure-suitability.md` | `ADR-001` (Pending) | `TC-001` (Pending) | Epic: `EPIC-DOM` / Story: `DBX-STORY-TBD-01` | `PROPOSED` (Tergantung penyelesaian `Q-003`) |
| **GOAL-001**: Penyediaan platform mailbox mandiri & multi-domain fleksibel | **BR-001**: Pengguna dapat mengelola alamat email sementara dan permanen dengan domain kustom | **FR-002** / **MBX-001**: Pembuatan mailbox sementara dengan masa aktif berbasis durasi (TTL) | **NFR-002**: Latensi pembuatan mailbox ≤ 1.5 detik | **SEC-002**: Isolasi akses mailbox antar sesi atau token | `docs/09-research/ux-pattern-benchmark.md` | `ADR-002` (Pending) | `TC-002` (Pending) | Epic: `EPIC-MBX` / Story: `DBX-STORY-TBD-02` | `PROPOSED` (Asumsi: `A-001`, isu `Q-003`) |
| **GOAL-001**: Penyediaan platform mailbox mandiri & multi-domain fleksibel | **BR-001**: Pengguna dapat mengelola alamat email sementara dan permanen dengan domain kustom | **FR-003** / **MBX-003**: Pengelolaan mailbox permanen dan konversi alias email persisten | **NFR-003**: Integritas penyimpanan data email jangka panjang | **SEC-003**: Autentikasi kuat & pembatasan kuota penyimpanan | `docs/09-research/problem-value-research.md` (Gap: `Q-001`) | `ADR-002` (Pending) | `TC-003` (Pending) | Epic: `EPIC-MBX` / Story: `DBX-STORY-TBD-03` | `PROPOSED` (Membutuhkan validasi riset `Q-001`) |
| **GOAL-002**: Penerimaan dan ekstraksi email masuk secara cepat dan aman | **BR-002**: Pemrosesan email masuk real-time dengan ekstraksi kode verifikasi / OTP | **FR-004** / **INB-001**: Penerimaan email masuk via protokol SMTP/Inbound Pipe | **NFR-004**: Latensi pemrosesan email masuk ≤ 3 detik | **SEC-004**: Pemeriksaan reputasi pengirim, SPF/DKIM/DMARC pass/fail | `docs/09-research/mail-infrastructure-suitability.md` | `ADR-003` (Pending) | `TC-004` (Pending) | Epic: `EPIC-INB` / Story: `DBX-STORY-TBD-04` | `VERIFIED` (Kesesuaian protokol pos) |
| **GOAL-002**: Penerimaan dan ekstraksi email masuk secara cepat dan aman | **BR-002**: Pemrosesan email masuk real-time dengan ekstraksi kode verifikasi / OTP | **FR-005** / **OTP-001**: Parser otomatis untuk ekstraksi kode OTP dan magic link | **NFR-005**: Akurasi deteksi pola OTP ≥ 95% | **SEC-005**: Sanitasi konten email, proteksi dari payload phishing/XSS | `docs/09-research/ux-pattern-benchmark.md` | `ADR-004` (Pending) | `TC-005` (Pending) | Epic: `EPIC-OTP` / Story: `DBX-STORY-TBD-05` | `PROPOSED` (Pola regex heuristik) |
| **GOAL-003**: Kemudahan akses multi-kanal (Web & Telegram Bot) | **BR-003**: Interaksi multi-channel untuk akses cepat kode dan isi pesan | **FR-006** / **BOT-001**: Pengiriman pesan ringkasan dan kode OTP via Telegram Bot | **NFR-006**: Waktu pengiriman notifikasi bot ≤ 2 detik dari inbound | **SEC-006**: Autentikasi pairing chat ID Telegram dengan akun pengguna | `docs/09-research/ux-pattern-benchmark.md` | `ADR-005` (Pending) | `TC-006` (Pending) | Epic: `EPIC-BOT` / Story: `DBX-STORY-TBD-06` | `PROPOSED` (Tergantung autentikasi `Q-004`) |
| **GOAL-003**: Kemudahan akses multi-kanal (Web & Telegram Bot) | **BR-003**: Interaksi multi-channel untuk akses cepat kode dan isi pesan | **FR-007** / **WEB-001**: Antarmuka web responsif untuk inbox, pembacaan email, dan manajemen domain | **NFR-007**: Waktu muat awal halaman web ≤ 2.0 detik | **SEC-007**: Proteksi CSRF, Content Security Policy (CSP), proteksi XSS | `docs/09-research/ux-pattern-benchmark.md` | `ADR-006` (Pending) | `TC-007` (Pending) | Epic: `EPIC-WEB` / Story: `DBX-STORY-TBD-07` | `PROPOSED` (Desain UX benchmark) |
| **GOAL-004**: Tata kelola operasional dan audit yang transparan | **BR-004**: Auditabilitas dan manajemen kepatuhan operasional sistem | **FR-008** / **OPS-001..005**: Autentikasi master admin (`OPS-001`), scheduler auto-purge (`OPS-002`), health checks (`OPS-003`), rate limiting (`OPS-004`), audit trail aktivitas (`OPS-005`) | **NFR-008** (auto-purge), **NFR-009** (health/readiness), **NFR-012** (rate limiting) | **SEC-002** (admin auth), **SEC-008** (audit trail), **SEC-009** (rate limiting) | `docs/00-governance/documentation-standards.md`, `docs/02-requirements/functional-specs/07-admin-operations.md` | `ADR-007`, `ADR-011` (Pending) | `TC-008` (Pending) | Epic: `EPIC-OPS` / Story: `DBX-STORY-TBD-08` | `VERIFIED` (Prinsip kepatuhan data & operasional; `F4`) |

---

## 4. Pemetaan Kebutuhan ke Risiko & Pertanyaan Terbuka (Risk & Open Question Mapping)

| Kebutuhan / Modul | Risiko Terkait (`RISK-*`) | Pertanyaan Terbuka (`Q-*`) | Keputusan Tata Kelola (`DEC-*`) | Status Mitigasi |
| --- | --- | --- | --- | --- |
| `BR-001` / `DOM-001` | `RISK-001` (Kelemahan bukti riset) | `Q-001`, `Q-002` | `DEC-003` | Menandai asumsi dan celah bukti riset secara transparan |
| `MBX-001`, `MBX-002` | `RISK-004` (Penyalahgunaan mailbox sementara / spam abuse) | `Q-003` (Batas cakupan MVP) | `DEC-001` | Membutuhkan perumusan batasan MVP yang tegas sebelum rilis |
| `INB-001`, `OTP-001` | `RISK-005` (Injeksi kode jahat via email HTML/XSS) | `Q-004` (Model autentikasi/identitas) | `DEC-001` | Spesifikasi sanitasi HTML ketat dan rendering terisolasi |
| `BOT-001`, `WEB-001` | `RISK-006` (Kebocoran data pesan via saluran notifikasi pihak ketiga) | `Q-004` (Model autentikasi/identitas) | `DEC-001` | Membatasi payload notifikasi (hanya OTP/ringkasan) dan token pairing |
| Kebutuhan Global | `RISK-002` (Hambatan integrasi tooling GitHub/Jira) | `Q-005`, `Q-006` | `DEC-001` | Pendekatan dokumentasi mandiri dan sync berbasis bukti |
| Kebutuhan Global | `RISK-003` (Ketidakkonsistenan antar dokumen) | — | `DEC-001`, `DEC-002` | RTM canonical sebagai rujukan audit silang |

---

## 5. Pemetaan ID Warisan / Template ke Skema ID Kanonikal (Legacy ID Mapping)
Guna menjaga konsistensi dengan rujukan dokumen awal yang menggunakan format `PREFIX-N` (seperti pada template PRD awal):

| ID Warisan / Konseptual | ID Kanonikal Baru | Nama Modul / Fitur | Alasan Penyelarasan |
| --- | --- | --- | --- |
| `AUTH-1` (Konseptual) | `SEC-002` / `SEC-006` | Autentikasi Akun & Akses Sesi | Penyesuaian ke skema kontrol keamanan standar `SEC-*` |
| `DOM-1` (Konseptual) | `DOM-001` | Manajemen & Verifikasi Domain | Standarisasi format 3-digit `DOM-001` |
| `MBX-1` (Konseptual) | `MBX-001` | Pembuatan Mailbox Sementara | Standarisasi format 3-digit `MBX-001` |
| `MBX-2` (Konseptual) | `MBX-003` | Pengelolaan Mailbox Permanen | Penyelarasan format kanonikal `MBX-003` (`MBX-002` = perpanjangan durasi TTL) |
| `INB-1` (Konseptual) | `INB-001` | Penerimaan Email Masuk (SMTP/Pipe) | Standarisasi format 3-digit `INB-001` |
| `OTP-1` (Konseptual) | `OTP-001` | Ekstraksi Kode OTP & Magic Link | Standarisasi format 3-digit `OTP-001` |
| `NOTIF-1` (Konseptual) | `BOT-001` | Notifikasi Bot Telegram | Penyesuaian ke modul bot telegram `BOT-001` |
| `UI-1` (Konseptual) | `WEB-001` | Web Dashboard Inbox & Viewer | Standarisasi antarmuka web `WEB-001` |
| `LOG-1` (Konseptual) | `OPS-002` / `OPS-005` | Auto-Purge Scheduler & Audit Trail | Pemisahan kanonikal: `OPS-002` = pembersihan otomatis (`NFR-008`), `OPS-005` = jejak audit (`SEC-008`); `OPS-001` = autentikasi master admin |

---

## 6. Kerangka Verifikasi Kebutuhan (Verification & Coverage Status)

```mermaid
flowchart TD
    Charter[Project Charter Goals: GOAL-001..004] --> BR[Business Requirements: BR-001..004]
    BR --> FR[Functional Modules: DOM, MBX, INB, OTP, BOT, WEB, OPS]
    BR --> NFR[Non-Functional Requirements: NFR-001..012]
    FR --> SEC[Security Controls: SEC-001..012]
    NFR --> SEC
    FR --> ADR[Architecture Decisions: ADR-001..TBD]
    SEC --> ADR
    FR --> TC[Test Cases: TC-001..008 PENDING]
    SEC --> TC
    FR --> Delivery[Jira DBX Epics & Stories: PENDING SYNC]
```

### Ringkasan Cakupan (Coverage Summary)
- **Total Sasaran Teridentifikasi:** 4 (`GOAL-001` s/d `GOAL-004`)
- **Total Kebutuhan Bisnis:** 4 (`BR-001` s/d `BR-004`)
- **Total Kebutuhan Fungsional Pokok:** 8 (`FR-001` s/d `FR-008` terdistribusi dalam 7 modul)
- **Total Kebutuhan Non-Fungsional Pokok:** 12 (`NFR-001` s/d `NFR-012` per `nfr-spec.md`)
- **Total Kontrol Keamanan Terpetakan:** 12 (`SEC-001` s/d `SEC-012` per `security-privacy-requirements.md`)
- **Kasus Uji Terkait:** 8 Placeholder Terdefinisi (`TC-001` s/d `TC-008`, status `PENDING`)
- **Item Delivery Terkait:** 8 Placeholder Epic/Story Terdefinisi (status `PENDING SYNC`)

---

## 7. Aturan Perubahan & Pemeliharaan (Change & Maintenance Rules)
1. Penambahan kebutuhan fungsional baru wajib menambahkan baris pemetaan baru pada RTM dengan status awal `PROPOSED`.
2. Setiap pengubahan status implementasi atau pengujian harus diverifikasi sebelum mengubah status dari `PENDING` menjadi `VERIFIED`.
3. Jika ada item yang dihapus atau dipindahkan ke Fase 2, ID tidak boleh digunakan ulang (*no ID reuse*).
