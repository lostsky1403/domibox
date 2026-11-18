# Document Control Register (DomiBox)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Governance / Orchestrator`  
**Related Documents:**
- `docs/00-governance/documentation-standards.md`
- `docs/00-governance/revision-and-approval-policy.md`
- `docs/00-governance/raci-matrix.md`
- `docs/README.md`

---

## 1. Purpose & Management Rules
Register Kontrol Dokumen ini memetakan seluruh dokumen terkendali (*controlled documents*) dalam proyek DomiBox, mencatat status siklus hidup, versi, tanggal pembaruan terakhir, penanggung jawab (*owner*), dan kategori fase.

### Aturan Pembaruan:
- Setiap dokumen baru yang dibuat dalam repositori wajib didaftarkan di sini.
- Perubahan status (misal dari `PROPOSED` menjadi `APPROVED` atau `SUPERSEDED`) wajib dimutakhirkan pada tabel di bawah.
- Dokumen dilarang ditandai `APPROVED` tanpa adanya bukti peninjauan dan persetujuan formal sesuai `revision-and-approval-policy.md`.

---

## 2. Master Register Dokumen Terkendali

| Domain / ID | Path Dokumen | Judul / Deskripsi Singkat | Status | Versi | Tanggal | Pemilik (Owner) | Bukti / Catatan |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **GOV-01** | `docs/00-governance/project-charter.md` | Project Charter DomiBox Bootstrap | `PROPOSED` | 0.2 | 2026-11-15 | Orchestrator | Draft inisiasi awal bootstrap |
| **GOV-02** | `docs/00-governance/documentation-standards.md` | Standar Dokumentasi, Metadata, & ID Canonical | `PROPOSED` | 0.2 | 2026-11-15 | Governance | Shared contract seluruh fase |
| **GOV-03** | `docs/00-governance/revision-and-approval-policy.md` | Kebijakan Revisi, Versi, & Persetujuan | `PROPOSED` | 0.2 | 2026-11-15 | Governance | Prosedur kontrol perubahan |
| **GOV-04** | `docs/00-governance/decision-log.md` | Log Keputusan Proyek (`DEC-*`) | `PROPOSED` | 0.2 | 2026-11-15 | Governance | Mencatat DEC-001 s/d DEC-003 |
| **GOV-05** | `docs/00-governance/open-questions.md` | Register Pertanyaan Terbuka (`Q-*`) | `PROPOSED` | 0.2 | 2026-11-15 | Governance / Shared | Mencatat Q-001 s/d Q-006 |
| **GOV-06** | `docs/00-governance/glossary.md` | Glosarium Istilah & Singkatan DomiBox | `PROPOSED` | 0.2 | 2026-11-15 | Governance | Definisi istilah teknis dan domain |
| **GOV-07** | `docs/00-governance/tool-capability-audit.md` | Audit Kemampuan Lingkungan, MCP, & Tooling | `PROPOSED` | 0.2 | 2026-11-15 | Orchestrator | Fakta terverifikasi pra-terbang |
| **GOV-08** | `docs/00-governance/prd-template-audit.md` | Audit Template PRD Asli vs Standar | `PROPOSED` | 0.2 | 2026-11-15 | Product Governance | Evaluasi GAP template PRD |
| **GOV-09** | `docs/00-governance/raci-matrix.md` | Matriks RACI Tata Kelola & Siklus Dokumen | `PROPOSED` | 0.2 | 2026-11-15 | Governance | Pembagian peran tingkat tata kelola |
| **GOV-10** | `docs/00-governance/communication-plan.md` | Rencana Komunikasi, Review, & Eskalasi | `PROPOSED` | 0.2 | 2026-11-15 | Governance | Saluran & ritme komunikasi |
| **GOV-11** | `docs/00-governance/document-control-register.md` | Register Kontrol Dokumen Master | `PROPOSED` | 0.2 | 2026-11-15 | Governance | Dokumen ini |
| **GOV-12** | `docs/00-governance/assumption-log.md` | Log Asumsi Proyek Terkonsolidasi (`A-*`) | `PROPOSED` | 0.2 | 2026-11-15 | Governance / Product | Konsolidasi asumsi lintas domain |
| **GOV-13** | `docs/00-governance/risk-register.md` | Register Risiko Proyek (`RISK-*`) | `PROPOSED` | 0.2 | 2026-11-15 | Governance / Risk | Risiko bootstrap dan lintas domain |
| **PRD-01** | `docs/TEMPLATE_PRD.md` | Template PRD Asli (Dipertahankan Verbatim) | `PROPOSED` | 0.2 | 2026-11-15 | Product | Template bawaan sebelum bootstrap |
| **PRD-02** | `docs/01-product/prd/TEMPLATE_PRD_IMPROVED.md` | Template PRD Disempurnakan (Traceable) | `PROPOSED` | 0.2 | 2026-11-15 | Product | Rekomendasi audit PRD template |
| **PRD-03** | `docs/01-product/prd/product-requirements-document.md` | Product Requirements Document DomiBox | `PROPOSED` | 0.2 | 2026-11-15 | ProductDocs | Draft Phase 3 (agent-authored) |
| **PROD-01** | `docs/01-product/product-vision.md` | Visi Produk & Proposisi Nilai | `PROPOSED` | 0.2 | 2026-11-15 | ProductDocs | Draft Phase 3 |
| **PROD-02** | `docs/01-product/personas-and-user-segments.md` | Persona & Segmentasi Pengguna | `PROPOSED` | 0.2 | 2026-11-15 | ProductDocs | Draft Phase 3 |
| **PROD-03** | `docs/01-product/mvp-scope.md` | Cakupan MVP & Batasan Rilis | `PROPOSED` | 0.2 | 2026-11-15 | ProductDocs | Draft Phase 3 |
| **PROD-04** | `docs/01-product/stakeholder-map.md` | Peta Pemangku Kepentingan | `PROPOSED` | 0.2 | 2026-11-15 | ProductDocs | Draft Phase 3 |
| **REQ-01** | `docs/02-requirements/traceability/traceability-matrix.md` | Requirements Traceability Matrix (RTM) | `PROPOSED` | 0.2 | 2026-11-15 | ReqTrace | Draft kanonikal Phase 3 |
| **REQ-02** | `docs/02-requirements/requirements-assumptions-register.md` | Register Asumsi & Evidence Gaps Kebutuhan | `PROPOSED` | 0.2 | 2026-11-15 | ReqTrace | Draft Phase 3 |
| **ARCH-00** | `docs/03-architecture/architecture-overview.md` | Ringkasan Arsitektur Sistem (Draft Skeleton) | `PROPOSED` | 0.2 | 2026-11-15 | Architecture | Skeleton; detail Phase 4 |
| **ARCH-ADR** | `docs/03-architecture/adr/ADR-001.md` … `ADR-012.md` | Architecture Decision Records (Skeletons) | `PROPOSED` | 0.2 | 2026-11-15 | Architecture | Skeletons; detail Phase 4 |
| **RES-01** | `docs/09-research/mail-infrastructure-suitability.md` | Riset Kelayakan Infrastruktur Email | `PROPOSED` | 0.2 | 2026-11-15 | Research | Terverifikasi: sumber sesi didekode |
| **RES-02** | `docs/09-research/ux-pattern-benchmark.md` | Riset UX Pattern & Benchmark Mailbox | `PROPOSED` | 0.2 | 2026-11-15 | Research | Terverifikasi: rekonstruksi sesi |
| **RES-03** | `docs/09-research/problem-value-research.md` | Riset Nilai Masalah Pengguna (Placeholder) | `PROPOSED` | 0.2 | 2026-11-15 | Research | Bukti asli belum ditemukan (`Q-001`) |
| **RES-04** | `docs/09-research/competitive-comparative-research.md`| Riset Komparasi Kompetitif (Placeholder) | `PROPOSED` | 0.2 | 2026-11-15 | Research | Bukti asli belum ditemukan (`Q-002`) |
| **DOC-IDX**| `docs/README.md` | Indeks Navigasi & Peta Dokumentasi Master | `PROPOSED` | 0.2 | 2026-11-15 | Orchestrator | Snapshot progres bootstrap |

---

## 3. Matriks Perencanaan Dokumen Fase Mendatang (Downstream Placeholders)

Dokumen-dokumen berikut dijadwalkan untuk disusun pada fase turunan (Phase 3–10). Register ini mencatat ekspektasi path dan pemilik untuk menjaga konsistensi penelusuran. Status diperbarui berdasarkan artefak yang sudah ada di disk (snapshot 2026-11-14).

| Domain Fase | Ekspektasi Path | Rencana Judul / Isi Dokumen | Status Rencana | Target Fase |
| :--- | :--- | :--- | :---: | :---: |
| **01-Product** | `docs/01-product/prd/product-requirements-document.md` | Product Requirements Document DomiBox | `PROPOSED (created)` | Phase 3 |
| **01-Product** | `docs/01-product/mvp-scope.md` | Definisi Batasan Ruang Lingkup MVP | `PROPOSED (created)` | Phase 3 |
| **02-Requirements** | `docs/02-requirements/srs.md` | Software Requirements Specification (`FR-*`, `NFR-*`)| `IN PROGRESS (ReqCore)` | Phase 3 |
| **02-Requirements** | `docs/02-requirements/traceability/traceability-matrix.md` | Requirements Traceability Matrix (RTM) Master | `PROPOSED (created)` | Phase 3 |
| **02-Requirements** | `docs/02-requirements/business-requirements.md` | Business Requirements Document (`BR-*`) | `IN PROGRESS (ReqCore)` | Phase 3 |
| **02-Requirements** | `docs/02-requirements/functional-requirements.md` | Spesifikasi Kebutuhan Fungsional (`FR-*`) | `IN PROGRESS (ReqCore)` | Phase 3 |
| **02-Requirements** | `docs/02-requirements/non-functional-requirements.md` | Spesifikasi Kebutuhan Non-Fungsional (`NFR-*`/`SEC-*`) | `IN PROGRESS (ReqCore)` | Phase 3 |
| **03-Architecture** | `docs/03-architecture/architecture-overview.md` | Ringkasan Arsitektur Sistem | `PROPOSED (skeleton)` | Phase 4 |
| **03-Architecture** | `docs/03-architecture/adr/` | Kumpulan Architecture Decision Records (`ADR-001` dst) | `PROPOSED (skeletons)` | Phase 4 |
| **04-Technical** | `docs/04-technical/api/openapi.yaml` | Spesifikasi API RESTful DomiBox (OpenAPI 3.1) | `PROPOSED` | Phase 7 |
| **04-Technical** | `docs/04-technical/api-specification.md` | Arsitektur REST API & Rute Endpoint | `PROPOSED` | Phase 7 |
| **04-Technical** | `docs/04-technical/database-schema.md` | Skema Database DDL & Kamus Data | `PROPOSED` | Phase 7 |
| **04-Technical** | `docs/04-technical/data-model.md` | Spesifikasi Model Data & Entitas Relasional | `PROPOSED` | Phase 7 |
| **04-Technical** | `docs/04-technical/telegram-bot-specification.md` | Spesifikasi Teknis Bot Telegram (grammY) | `PROPOSED` | Phase 7 |
| **04-Technical** | `docs/04-technical/mail-flow-specification.md` | Pipeline Pemrosesan Email & Ingest Inbound | `PROPOSED` | Phase 7 |
| **04-Technical** | `docs/04-technical/otp-extraction-specification.md` | Ekstraksi Heuristik & Regex OTP / Magic Link | `PROPOSED` | Phase 7 |
| **04-Technical** | `docs/04-technical/deployment-specification.md` | Orkestrasi Docker Compose & Alokasi Resource | `PROPOSED` | Phase 7 |
| **04-Technical** | `docs/04-technical/error-catalogue.md` | Katalog Kode Kesalahan & Format Envelope | `PROPOSED` | Phase 7 |
| **05-Security** | `docs/05-security/threat-model.md` | Model Ancaman (Threat Model & STRIDE) | `PLANNED` | Phase 6 |
| **05-Security** | `docs/05-security/security-requirements.md` | Kontrol Keamanan & Privasi (`SEC-*`) | `PLANNED` | Phase 6 |
| **06-Quality** | `docs/06-quality/test-strategy.md` | Strategi Pengujian & Quality Gate | `PLANNED` | Phase 6 |
| **06-Quality** | `docs/06-quality/test-cases/` | Katalog Kasus Uji (`TC-*`) | `PLANNED` | Phase 6 |
| **07-Operations** | `docs/07-operations/deployment-guide.md` | Panduan Deployment & Konfigurasi VPS | `PLANNED` | Phase 7 |
| **07-Operations** | `docs/07-operations/monitoring-runbook.md` | Runbook Pemantauan & Observabilitas | `PLANNED` | Phase 7 |
| **08-Delivery** | `docs/08-delivery/epic-backlog.md` | Backlog 14 Epics, Stories, & Tasks Jira | `PLANNED` | Phase 8 |
| **08-Delivery** | `docs/08-delivery/jira-sync-map.json` | Peta Sinkronisasi ID Lokal ke Kunci Jira DBX | `PLANNED` | Phase 12 |
| **10-UX** | `docs/10-ux/information-architecture.md` | Arsitektur Informasi & Alur Pengguna | `PLANNED` | Phase 9 |

---

## 4. Riwayat Perubahan Register
| Versi | Tanggal | Deskripsi Perubahan | Penanggung Jawab |
| :---: | :---: | :--- | :--- |
| `0.1` | 2026-11-14 | Inisialisasi awal register kontrol dokumen untuk artefak Phase 1 & 2 beserta placeholder fase turunan. | Governance / Orchestrator |
| `0.2` | 2026-11-15 | Rekonsiliasi lengkap seluruh artefak Fase 1 s/d 8: spesifikasi fungsional 01..07, diagram arsitektur, spesifikasi teknis, keamanan, kualitas, dan delivery backlog. | Governance / Orchestrator |
