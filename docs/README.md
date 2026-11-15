# DomiBox Documentation Index

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.2 | 2026-11-15 | omp-orchestrator/DocIndex | `docs/00-governance/project-charter.md`<br>`docs/00-governance/document-control-register.md` |

---

## 1. Tujuan Dokumen (Purpose)
Dokumen ini merupakan indeks kanonikal (*Master Documentation Index*) untuk seluruh artefak rekayasa, produk, arsitektur, spesifikasi teknis, keamanan, kualitas, operasional, dan tata kelola rilis platform **DomiBox** (*Self-Hosted Multi-Domain Email Management Platform*).

---

## 2. Peta Navigasi Struktur Dokumentasi (Documentation Directory Map)

```
docs/
├── 00-governance/                     # Piagam, tata kelola, keputusan, & kontrol dokumen
│   ├── project-charter.md             # Piagam proyek & sasaran strategis (GOAL-001..004)
│   ├── documentation-standards.md     # Standar penamaan, metadata, & skema ID kanonikal
│   ├── document-control-register.md   # Register kontrol versi & riwayat dokumen
│   ├── decision-log.md                # Log keputusan tata kelola (DEC-001..003)
│   ├── open-questions.md              # Register pertanyaan terbuka & celah bukti (Q-001..006)
│   ├── risk-register.md               # Register risiko proyek & teknis (RISK-001..007)
│   ├── raci-matrix.md                 # Matriks akuntabilitas & peran pemangku kepentingan
│   ├── communication-plan.md          # Rencana komunikasi berkala
│   ├── revision-and-approval-policy.md# Kebijakan perubahan & persetujuan
│   ├── glossary.md                    # Glosarium terminologi rekayasa email
│   ├── tool-capability-audit.md       # Audit kapabilitas MCP & lingkungan eksekusi
│   └── prd-template-audit.md          # Audit kesesuaian template PRD awal
├── 01-product/                        # Visi, cakupan, personas, & persyaratan produk
│   ├── product-vision.md              # Visi produk & pilar nilai
│   ├── mvp-scope.md                   # Batasan cakupan MVP vs Fase 2
│   ├── value-proposition.md           # Analisis proposisi nilai
│   ├── personas-and-user-segments.md  # Definisi pengguna target (STK-001..004)
│   ├── stakeholder-map.md             # Pemetaan pemangku kepentingan
│   ├── ux-principles.md               # Prinsip desain antarmuka
│   ├── ia-and-interaction-spec.md     # Arsitektur informasi & spesifikasi interaksi
│   ├── prototype-notes.md             # Catatan purwarupa & pengujian konsep
│   └── prd/
│       ├── product-requirements-document.md # Dokumen Persyaratan Produk kanonikal (PRD v0.1)
│       └── TEMPLATE_PRD_IMPROVED.md   # Template PRD terstandardisasi ISO/IEC/IEEE 29148
├── 02-requirements/                   # Spesifikasi kebutuhan teknis & fungsional
│   ├── brd.md                         # Business Requirements Document (BR-001..004)
│   ├── srs.md                         # Software Requirements Specification (FR-001..008)
│   ├── nfr-spec.md                    # Non-Functional Requirements (NFR-001..012)
│   ├── security-privacy-requirements.md # Persyaratan keamanan & privasi (SEC-001..012)
│   ├── requirements-assumptions-register.md # Register asumsi kebutuhan (A-001..005)
│   ├── scope-and-change-control.md    # Mekanisme kontrol perubahan ruang lingkup
│   ├── traceability/
│   │   └── traceability-matrix.md     # Matriks keterlacakan kebutuhan (RTM kanonikal)
│   └── functional-specs/              # Spesifikasi rinci per modul fungsional
│       ├── 01-domain-management.md    # Modul DOM-001..005
│       ├── 02-mailbox-lifecycle.md    # Modul MBX-001..005
│       ├── 03-inbox-management.md     # Modul INB-001..005
│       ├── 04-otp-center.md           # Modul OTP-001..005
│       ├── 05-telegram-bot.md         # Modul BOT-001..005
│       ├── 06-web-dashboard.md        # Modul WEB-001..005
│       └── 07-admin-operations.md     # Modul OPS-001..005
├── 03-architecture/                   # Desain arsitektur sistem & keputusan teknis
│   ├── architecture-overview.md       # Ringkasan arsitektur modular monolith
│   ├── tech-evaluation-matrix.md      # Matriks perbandingan teknologi
│   ├── capacity-planning.md           # Anggaran sumber daya VPS & estimasi kapasitas
│   ├── failure-mode-analysis.md       # FMEA analisis mode kegagalan sistem
│   ├── adr/                           # Architecture Decision Records (ADR-001..012)
│   └── diagrams/                      # Diagram arsitektur & sequence (Mermaid)
│       ├── c4-system-context.md       # C4 Level 1: System Context
│       ├── c4-container.md            # C4 Level 2: Container
│       ├── component-diagram.md       # C4 Level 3: Backend Core Component
│       ├── deployment-diagram.md      # Topologi kontainer Docker fisik
│       ├── email-flow-sequence.md     # Alur penerimaan inbound & ekstraksi
│       ├── domain-onboarding-flow.md  # Alur registrasi & verifikasi DNS
│       ├── mailbox-lifecycle-state-machine.md # State machine siklus mailbox
│       ├── expiration-deletion-flow.md# Alur pembersihan TTL & auto-purge
│       └── network-port-matrix.md     # Matriks jaringan, port, & firewall UFW
├── 04-technical/                      # Spesifikasi teknis implementasi
│   ├── data-model.md                  # Spesifikasi model data logis & fisik
│   ├── database-schema.md             # Skema DDL PostgreSQL 16 & Drizzle ORM
│   ├── api-specification.md           # Ikhtisar arsitektur REST API & rute
│   ├── telegram-bot-specification.md  # Spesifikasi teknis bot Telegram (grammY)
│   ├── mail-flow-specification.md     # Spesifikasi pipeline pemrosesan email masuk
│   ├── otp-extraction-specification.md # Spesifikasi heuristik & regex ekstraksi OTP
│   ├── deployment-specification.md    # Spesifikasi orkestrasi Docker Compose produksi
│   ├── error-catalogue.md             # Katalog kode kesalahan & standard envelope
│   └── api/
│       └── openapi.yaml               # Spesifikasi REST API OpenAPI 3.1.0
├── 05-security/                       # Pemodelan ancaman & kontrol mitigasi
│   └── threat-model.md                # Pemodelan ancaman STRIDE & mitigasi SEC-*
├── 06-quality/                        # Rencana & strategi pengujian
│   └── test-strategy.md               # Master Test Plan & matriks kasus uji (TC-001..008)
├── 07-operations/                     # Strategi deployment & pengoperasian
│   └── deployment-architecture.md     # Topologi Docker Compose & runbook operasional
├── 08-delivery/                       # Rencana rilis & pemetaan backlog Jira
│   └── epic-catalogue.md              # 14 Epic kanonikal Jira (DBX) & katalog user story
└── 09-research/                       # Dokumen riset primer & bukti empiris
    ├── mail-infrastructure-feasibility.md # Riset kelayakan infrastruktur mail (F1-F6)
    ├── mail-infrastructure-suitability.md # Studi kelayakan engine email Stalwart
    ├── ux-pattern-research.md         # Riset pola antarmuka pengguna
    ├── ux-pattern-benchmark.md        # Benchmark pola UX disposable mailbox
    ├── tech-stack-evaluation.md       # Evaluasi tumpukan teknologi backend/frontend
    ├── security-controls-research.md  # Riset kontrol keamanan email self-hosted
    ├── problem-value-research.md      # Riset nilai masalah (placeholder gap Q-001)
    └── competitive-comparative-research.md # Riset kompetitor (placeholder gap Q-002)
```

---

## 3. Matriks Status Dokumen Utama (Document Status Register)

| Wilayah / Kategori | Dokumen Kunci | Status | Catatan Validasi / Bukti |
| --- | --- | :---: | --- |
| **00 Governance** | `project-charter.md`, `documentation-standards.md` | `VERIFIED` | Fondasi tata kelola & standar metadata. |
| **01 Product** | `prd/product-requirements-document.md`, `mvp-scope.md` | `PROPOSED` | Berpijak pada batasan terverifikasi VPS `vps-tencent3b`. |
| **02 Requirements** | `brd.md`, `srs.md`, `nfr-spec.md`, `functional-specs/*` | `PROPOSED` | 35 spesifikasi fungsional terpetakan (`DOM`, `MBX`, `INB`, `OTP`, `BOT`, `WEB`, `OPS`). |
| **03 Architecture** | `architecture-overview.md`, `adr/ADR-001..012.md` | `PROPOSED` | Arsitektur modular monolith Fastify + Stalwart + PostgreSQL. |
| **04 Technical** | `database-schema.md`, `api/openapi.yaml`, `error-catalogue.md` | `PROPOSED` | Skema relasional & kontrak antarmuka OpenAPI 3.1. |
| **05 Security** | `threat-model.md` | `PROPOSED` | Pemodelan ancaman STRIDE & mitigasi `SEC-001..012`. |
| **06 Quality** | `test-strategy.md` | `PROPOSED` | Rencana pengujian piramida Vitest + Playwright (`TC-001..008`). |
| **07 Operations** | `deployment-architecture.md` | `PROPOSED` | Topologi Docker Compose pada node VPS Tencent Cloud. |
| **08 Delivery** | `epic-catalogue.md` | `PROPOSED` | 14 Epic terstruktur siap sinkronisasi Jira DBX. |
| **09 Research** | `mail-infrastructure-feasibility.md`, `ux-pattern-research.md` | `VERIFIED` | Bukti empiris inspeksi infrastruktur VPS 2026-11-14 (`F1..F6`). |
