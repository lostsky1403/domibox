# RACI Matrix — Governance & Documentation Lifecycle (DomiBox)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Governance / Orchestrator`  
**Related Documents:**
- `docs/00-governance/project-charter.md`
- `docs/00-governance/revision-and-approval-policy.md`
- `docs/00-governance/documentation-standards.md`
- `docs/00-governance/communication-plan.md`
- `docs/08-delivery/` (Delivery-level RACI refinement target)

---

## 1. Purpose & Scope
Dokumen ini mendefinisikan matriks **RACI** (*Responsible, Accountable, Consulted, Informed*) pada level tata kelola (*governance level*) untuk siklus hidup dokumentasi dan *workstream* bootstrap DomiBox. 

Matriks ini berfungsi sebagai acuan pembagian peran awal selama fase inisiasi dan bootstrap (Phase 0–13), serta menjadi dasar yang akan disempurnakan lebih lanjut pada *delivery-level RACI* di `docs/08-delivery/raci.md`.

---

## 2. Definisi Peran RACI

| Kode | Peran | Definisi |
| :---: | :--- | :--- |
| **R** | **Responsible** | Pihak yang secara aktif menyusun, merevisi, menguji, atau mengeksekusi artefak/tugas. |
| **A** | **Accountable** | Pemilik tunggal yang bertanggung jawab atas hasil akhir, kebenaran, dan persetujuan formal (*decision authority*). |
| **C** | **Consulted** | Pihak yang wajib dimintai masukan teknis, keamanan, bisnis, atau operasional sebelum keputusan/dokumen difinalisasi (komunikasi dua arah). |
| **I** | **Informed** | Pihak yang menerima pemberitahuan hasil, status, atau perubahan dokumen (komunikasi satu arah). |

---

## 3. Identifikasi Pemangku Kepentingan (Stakeholder Roles)

| ID Peran | Nama Peran | Cakupan Tanggung Jawab dalam Bootstrap | Status Konfirmasi |
| :--- | :--- | :--- | :--- |
| `ROLE-PO` | **Product Owner / Sponsor** | Persetujuan ruang lingkup produk, prioritas MVP, keputusan bisnis, dan charter. | `ASSUMPTION` (belum ditugaskan personalia definitif) |
| `ROLE-ARCH` | **Lead Architect** | Keputusan arsitektur (ADR), evaluasi teknologi, model data, dan batas sistem. | `PROPOSED` |
| `ROLE-SEC` | **Security & Compliance Lead** | Kebutuhan keamanan/privasi (`SEC-*`), threat modeling, audit secret, kebijakan retensi. | `PROPOSED` |
| `ROLE-DEV` | **Tech Lead / Engineering** | Spesifikasi teknis (TSD), OpenAPI, pipeline CI/CD, dan kontrak integrasi. | `PROPOSED` |
| `ROLE-QA` | **QA / Test Lead** | Test strategy, test case catalog (`TC-*`), quality gates, kriteria keberterimaan (AC). | `PROPOSED` |
| `ROLE-OPS` | **DevOps / Site Reliability** | Strategi deployment VPS, port matrix, backup/restore, observabilitas, dan runbook. | `PROPOSED` |
| `ROLE-GOV` | **Orchestrator / Governance** | Standar dokumentasi, penelusuran (RTM), integrasi GitHub/Jira, koordinasi bootstrap. | `VERIFIED` (aktif dalam sesi bootstrap) |

---

## 4. Matriks RACI: Siklus Hidup Dokumentasi (Doc Lifecycle)

| Kategori / Aktivitas | Artifact / Path | ROLE-PO | ROLE-ARCH | ROLE-SEC | ROLE-DEV | ROLE-QA | ROLE-OPS | ROLE-GOV |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Governance Baseline** | `docs/00-governance/*` | **A** | C | C | C | I | I | **R** |
| **Product & PRD Baseline** | `docs/01-product/*` | **A** | C | C | C | C | I | **R** |
| **Requirements (SRS, BRD, RTM)** | `docs/02-requirements/*` | C | C | C | C | C | I | **A / R** |
| **Architecture & ADRs** | `docs/03-architecture/*` | I | **A** | C | **R** | I | C | C |
| **Technical Specifications & API** | `docs/04-technical/*` | I | C | C | **A / R** | C | C | C |
| **Security, Privacy & Threat Model** | `docs/05-security/*` | I | C | **A / R** | C | C | C | C |
| **Quality & Test Strategy** | `docs/06-quality/*` | I | I | C | C | **A / R** | I | C |
| **Operations & Deployment Strategy**| `docs/07-operations/*` | I | C | C | C | I | **A / R** | C |
| **Delivery Planning & Jira Map** | `docs/08-delivery/*` | C | I | I | C | I | I | **A / R** |
| **Research Synthesis & Evidence Gaps**| `docs/09-research/*` | I | C | C | C | I | I | **A / R** |
| **UI/UX & Information Architecture**| `docs/10-ux/*` / `01-product/ui-ux/`| **A** | C | I | C | C | I | **R** |

---

## 5. Matriks RACI: Workstream Bootstrap Teknis

| Workstream Bootstrap | Deliverable Utama | ROLE-PO | ROLE-ARCH | ROLE-SEC | ROLE-DEV | ROLE-QA | ROLE-OPS | ROLE-GOV |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Audit Kemampuan Tooling & MCP** | `tool-capability-audit.md` | I | C | I | C | I | C | **A / R** |
| **Materialisasi & Repair Riset** | `docs/09-research/*.md` | I | C | C | C | I | I | **A / R** |
| **Penyusunan Open Questions & DEC** | `open-questions.md`, `decision-log.md` | C | C | C | C | C | C | **A / R** |
| **Pembuatan Git Baseline & Draft PR**| Branch `docs/project-init`, PR | I | I | I | I | I | I | **A / R** |
| **Sinkronisasi Jira Epics & Stories**| DBX Epics, Tasks, Stories | C | I | I | I | I | I | **A / R** |
| **Audit Kepatuhan & Rahasia (Secrets)**| Zero secret leak & broken links | I | I | **A** | I | C | I | **R** |

---

## 6. Aturan Transisi & Persetujuan
1. **Persetujuan Bersama (Sign-Off):** Perubahan status dokumen dari `PROPOSED` menjadi `APPROVED` membutuhkan persetujuan dari pemegang peran **Accountable (A)** setelah berkonsultasi dengan pihak **Consulted (C)** terkait.
2. **Eskalasi Ketidaksepakatan:** Jika terdapat konflik antar peran teknis (misal antara Arsitektur dan Keamanan terkait model autentikasi), eskalasi diserahkan kepada `ROLE-PO` / Sponsor Proyek dengan mencatat *trade-off* ke dalam `open-questions.md` (`Q-*`) atau `decision-log.md` (`DEC-*`).
3. **Penyempurnaan Fase Delivery:** Saat memasuki fase implementasi perangkat lunak (Phase 8+), matriks ini akan diperluas mencakup sprint planning, code review, deployment gating, dan incident management pada `docs/08-delivery/raci.md`.
