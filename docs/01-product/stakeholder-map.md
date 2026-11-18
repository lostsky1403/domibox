# Stakeholder & Interest Map

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Product Lead / Orchestrator (ReqTrace)`  
**Related Documents:**
- `docs/00-governance/project-charter.md`
- `docs/00-governance/documentation-standards.md`
- `docs/00-governance/open-questions.md`
- `docs/01-product/prd/TEMPLATE_PRD_IMPROVED.md`
- `docs/02-requirements/traceability/traceability-matrix.md`

---

## 1. Tujuan (Purpose)
Dokumen ini mendefinisikan pemangku kepentingan (*stakeholders*), peran (*roles*), tingkat pengaruh (*power/influence*), tingkat kepentingan (*interest*), serta matriks akuntabilitas tata kelola (*RACI Matrix*) untuk proyek **DomiBox**. Pemetaan ini menjamin kejelasan tanggung jawab dan alur koordinasi mulai dari fase pendefinisian produk, tata kelola arsitektur, hingga implementasi dan operasional.

---

## 2. Identifikasi Pemangku Kepentingan (Stakeholder Inventory)

| ID Peran | Nama Peran / Pemangku Kepentingan | Kategori | Deskripsi Tanggung Jawab Utama | Tingkat Pengaruh (Power) | Tingkat Kepentingan (Interest) |
| --- | --- | --- | --- | --- | --- |
| **STK-001** | **Project Sponsor / Product Owner** | Internal (Governance) | Pemilik inisiatif, penentu arah strategis produk, pemberi persetujuan akhir cakupan MVP, pengambil keputusan bisnis (`DEC-*`, `Q-*`). | Tinggi | Tinggi |
| **STK-002** | **Product & Requirements Lead** | Internal (Product) | Penyusun PRD, penanggung jawab keterlacakan kebutuhan (`BR`, `FR`, `NFR`), penentu prioritas fitur, dan penjaga konsistensi fungsional. | Tinggi | Tinggi |
| **STK-003** | **Architecture & Tech Lead** | Internal (Engineering) | Penanggung jawab perancangan sistem, ADR (`ADR-*`), keputusan tumpukan teknologi (*tech stack*), dan kelayakan infrastruktur mail engine. | Tinggi | Tinggi |
| **STK-004** | **Security & Privacy Lead** | Internal (Security) | Penelaah model ancaman (*threat modeling*), perumus kontrol keamanan (`SEC-*`), penanggung jawab kepatuhan privasi data dan mitigasi risiko. | Sedang | Tinggi |
| **STK-005** | **Quality & Test Lead** | Internal (QA) | Penyusun strategi pengujian, perancang kasus uji (`TC-*`), penjamin kualitas rilis, dan validasi kriteria penerimaan (*Acceptance Criteria*). | Sedang | Tinggi |
| **STK-006** | **DevOps & Infrastructure Lead** | Internal (Operations) | Pengelola server hosting (VPS), konfigurasi Docker/Compose, otomatisasi CI/CD, manajemen DNS domain, dan pemantauan sistem (`OPS-*`). | Sedang | Sedang |
| **STK-007** | **End-User (Technical / Power User)** | Eksternal / Target User | Pengguna yang mengoperasikan dashboard web dan Telegram bot untuk penerimaan email sementara/permanen, pengetesan aplikasi, atau registrasi layanan. | Rendah | Tinggi |
| **STK-008** | **Upstream Domain & Mail Infrastructure Providers** | Eksternal (Vendor) | Penyedia DNS (misal: Cloudflare, Registrar) dan jaringan cloud VPS (misal: Tencent Cloud) yang mempengaruhi kelancaran inbound SMTP. | Tinggi | Rendah |

---

## 3. Matriks Kepentingan vs Pengaruh (Power-Interest Grid)

```
        Tinggi ▲
               │  [Manage Closely]                      [Manage Closely]
               │  STK-008 (Upstream Providers/DNS)      STK-001 (Project Sponsor / Owner)
               │                                        STK-002 (Product & Req Lead)
               │                                        STK-003 (Architecture Lead)
  Pengaruh     │
  (Power)      │  [Monitor / Inform]                    [Keep Informed & Consult]
               │                                        STK-004 (Security Lead)
               │                                        STK-005 (Quality Lead)
               │                                        STK-006 (DevOps Lead)
               │                                        STK-007 (End-Users)
        Rendah ▼────────────────────────────────────────────────────────────►
               Rendah                                  Tinggi
                                Kepentingan (Interest)
```

### Strategi Manajemen Pemangku Kepentingan:
1. **Kelola Secara Ketat (*Manage Closely*):**
   - **STK-001 (Owner/Sponsor):** Wajib dikonsultasikan untuk setiap perubahan cakupan MVP (`Q-003`), keputusan arsitektur utama, dan penutupan dokumen tata kelola.
   - **STK-002 (Product Lead) & STK-003 (Tech Lead):** Kolaborasi intensif harian untuk memastikan kebutuhan produk terpetakan secara realistis ke dalam desain teknis.
2. **Jaga Tetap Terinformasi & Konsultasikan (*Keep Informed & Consult*):**
   - **STK-004 (Security), STK-005 (QA), STK-006 (DevOps):** Melibatkan mereka secara proaktif dalam tinjauan silang dokumen (*cross-document review*) untuk memvalidasi kepatuhan kontrol teknis dan kesiapan operasional.
   - **STK-007 (End-Users):** Kumpulkan umpan balik pola antarmuka dan alur ekstraksi kode OTP guna menyempurnakan kegunaan sistem.
3. **Pantau Kendala Lingkungan (*Monitor*):**
   - **STK-008 (Upstream DNS & VPS Providers):** Pantau status port jaringan (terutama port 25), kebijakan anti-spam penyedia cloud, dan mekanisme perambatan DNS.

---

## 4. Matriks RACI Tata Kelola Dokumentasi & Produk (Governance RACI Matrix)

Definisi RACI:
- **R (Responsible):** Pihak yang bertanggung jawab menyusun dan menyelesaikan artefak.
- **A (Accountable):** Pihak yang memiliki wewenang akhir atas kebenaran hasil (hanya boleh 1 peran per artefak).
- **C (Consulted):** Pihak yang dimintai masukan atau pandangan teknis dua arah.
- **I (Informed):** Pihak yang diberikan laporan atau pembaruan satu arah setelah artefak selesai.

| Area / Artefak Dokumentasi | STK-001 (Owner) | STK-002 (Product) | STK-003 (Tech) | STK-004 (Security) | STK-005 (QA) | STK-006 (DevOps) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Project Charter & Kebijakan Tata Kelola** (`docs/00-governance/*`) | **A** | C | C | I | I | I |
| **Dokumen Kebutuhan Produk (PRD/BRD)** (`docs/01-product/*`) | A | **R** | C | C | C | I |
| **Kebutuhan Teknis & SRS** (`docs/02-requirements/*`) | I | A | **R** | C | C | C |
| **Matriks Keterlacakan Kebutuhan (RTM)** (`docs/02-requirements/traceability/*`) | I | **A** | R | C | R | I |
| **Arsitektur Sistem & ADR** (`docs/03-architecture/*`) | C | I | **A / R** | C | I | C |
| **Spesifikasi Teknis & API Contract** (`docs/04-technical/*`) | I | I | **A / R** | C | C | C |
| **Spesifikasi Keamanan & Privasi** (`docs/05-security/*`) | I | I | C | **A / R** | C | C |
| **Rencana Pengujian & Kriteria Uji** (`docs/06-quality/*`) | I | C | C | C | **A / R** | I |
| **Strategi Operasional & CI/CD** (`docs/07-operations/*`) | I | I | C | I | I | **A / R** |
| **Penyelarasan Backlog Jira & Rilis** (`docs/08-delivery/*`) | A | **R** | C | I | C | C |

---

## 5. Saluran Komunikasi & Eskalasi (Communication & Escalation Paths)
- **Keputusan Produk & Cakupan Bisnis:** Diputuskan melalui peninjauan perubahan PRD dan dicatat dalam `docs/00-governance/decision-log.md` (`DEC-*`).
- **Isu/Pertanyaan Terbuka:** Didaftarkan dalam `docs/00-governance/open-questions.md` (`Q-*`) dan dieskalasi kepada STK-001 atau STK-002 sesuai domain masalah.
- **Risiko Proyek & Hambatan Teknis:** Dilaporkan dalam `docs/00-governance/risk-register.md` (`RISK-*`) dengan rencana mitigasi terukur.
