# Assumption Log — Consolidated Project Assumptions (DomiBox)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Governance / Product / Architecture (shared)`  
**Related Documents:**
- `docs/00-governance/project-charter.md`
- `docs/00-governance/open-questions.md`
- `docs/00-governance/decision-log.md`
- `docs/00-governance/documentation-standards.md`
- `docs/09-research/mail-infrastructure-suitability.md`

---

## 1. Purpose & Principles
Log ini mengonsolidasikan seluruh asumsi dasar (*baseline assumptions*) yang melandasi perancangan produk, arsitektur, keamanan, operasional, dan pengiriman proyek DomiBox. Sesuai dengan prinsip tata kelola pada `documentation-standards.md`:
1. **Pemisahan Tegas:** Asumsi tidak boleh disamarkan sebagai fakta terverifikasi (*verified facts*). Setiap asumsi diberi label status bukti `ASSUMPTION` atau `PROPOSED`.
2. **Keterkaitan Risiko & Pertanyaan:** Asumsi yang memiliki tingkat ketidakpastian tinggi atau dampak signifikan wajib memiliki pasangan mitigasi dalam bentuk pertanyaan terbuka (`Q-*`), risiko (`RISK-*`), atau investigasi teknis (*spike*).
3. **Validasi Berkala:** Setiap asumsi ditinjau secara berkala. Begitu terbukti benar melalui pengujian atau keputusan bisnis, statusnya dimutakhirkan menjadi `VALIDATED`, atau `INVALIDATED` jika terbukti keliru.

---

## 2. Master Assumption Table

| ID | Kategori | Deskripsi Asumsi | Dampak Terhadap Desain / Scope | Status Bukti | Rujukan Terkait / Blocker | Rencana Validasi / Tindak Lanjut |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **A-001** | **Product Scope** | DomiBox mencakup kebutuhan kombinasi mailbox sementara (*disposable/temporary*) dan mailbox permanen (*persistent*). | Mempengaruhi partisi basis data, alur otentikasi, retensi pesan, dan UI. | `ASSUMPTION` | `project-charter.md`, `Q-003` | Validasi pada fase penyusunan PRD (`docs/01-product/prd.md`) dan kesepakatan batasan MVP. |
| **A-002** | **Delivery Tooling** | Proyek Jira dengan kunci `DBX` adalah target resmi untuk pelacakan *epic*, *story*, dan tugas bootstrap DomiBox. | Menjadi dasar pembuatan artefak sinkronisasi delivery dan penulisan deskripsi issue. | `PROPOSED` | `project-charter.md`, `Q-005` | Validasi konektivitas Atlassian MCP pada Phase 12 sebelum mutasi massal. |
| **A-003** | **Governance** | Pendekatan *documentation-first bootstrap* dapat diterima dan diprioritaskan sebelum kode aplikasi diimplementasikan. | Seluruh upaya bootstrap difokuskan pada kelengkapan spesifikasi dan penelusuran. | `ASSUMPTION` | `project-charter.md` | Dikonfirmasi melalui persetujuan PR dokumentasi oleh pemilik proyek. |
| **A-004** | **Infrastructure** | Layanan email *open-source* Stalwart (MTA/JMAP/IMAP) dapat di-host secara mandiri (*self-hosted*) pada VPS Linux berbasis Docker. | Arsitektur inti email mengandalkan Stalwart daripada server email konvensional (Postfix/Dovecot). | `ASSUMPTION` (analisis sekunder mendukung) | `docs/09-research/mail-infrastructure-suitability.md` | Uji coba instalasi kontainer (*spike container*) pada lingkungan non-produksi. |
| **A-005** | **Security / Abuse** | Mailbox sementara menarik potensi penyalahgunaan tinggi (spam receiving, abuse, bot harvesting) sehingga memerlukan mekanisme rate-limiting dan CAPTCHA/PoW. | Spesifikasi teknis wajib memasukkan kontrol keamanan ketat (`SEC-*`) dan proteksi abuse API. | `PROPOSED` | `docs/05-security/`, `docs/00-governance/glossary.md` | Penyusunan bab proteksi penyalahgunaan pada Threat Model & Security Requirements. |
| **A-006** | **Identity / Auth** | Mailbox sementara dapat diakses dengan model *token/session-based* anonim atau semi-terautentikasi, sedangkan mailbox permanen memerlukan autentikasi kuat (MFA/RBAC). | Menentukan arsitektur otentikasi, skema relasi pengguna, dan otorisasi API. | `PROPOSED` | `Q-004`, `docs/04-technical/` | Perlu keputusan arsitektur definitif (`ADR-004` / `ADR-005`). |
| **A-007** | **DNS & Domain** | Pengguna/operator DomiBox memiliki kendali penuh atas konfigurasi DNS domain (MX, SPF, DKIM, DMARC, CNAME) yang dihubungkan ke platform. | Kemampuan penerimaan email inbound bergantung pada delegasi DNS yang valid. | `ASSUMPTION` | `docs/03-architecture/`, `docs/07-operations/` | Panduan orientasi domain (*domain onboarding runbook*) wajib mencakup verifikasi rekaman DNS. |
| **A-008** | **Environment Scope** | Target deployment awal adalah lingkungan single-node atau VPS terkelola sebelum ekspansi ke multi-node/cluster. | Konfigurasi Docker Compose dan penyimpanan persisten volume disk lokal cukup untuk MVP. | `PROPOSED` | `docs/07-operations/` | Verifikasi kapasitas beban dan spesifikasi VPS pada rencana operasional. |
| **A-009** | **Data Retention** | Pesan pada mailbox sementara akan dihapus secara otomatis berdasarkan kebijakan waktu kedaluwarsa (TTL), sedangkan mailbox permanen mengikuti kuota kapasitas. | Mengharuskan adanya background worker / cleanup job berkala pada arsitektur sistem. | `PROPOSED` | `docs/03-architecture/`, `docs/05-security/` | Spesifikasi job scheduler dan retensi data pada dokumen teknis. |

---

## 3. Matriks Ketergantungan Asumsi ke Pertanyaan Terbuka & Risiko

| ID Asumsi | Terkait Pertanyaan Terbuka (`Q-*`) | Terkait Risiko Proyek (`RISK-*`) | Rencana Aksi jika Asumsi Tidak Valid (Invalidated) |
| :--- | :--- | :--- | :--- |
| **A-001** | `Q-003` | `RISK-001` | Pangkas cakupan MVP hanya pada mailbox sementara, tunda mailbox permanen ke Fase 2. |
| **A-002** | `Q-005` | `RISK-002` | Buat pemetaan lokal mandiri dalam format Markdown/JSON tanpa bergantung pada integrasi Jira cloud. |
| **A-003** | — | `RISK-003` | Lakukan penyesuaian iteratif langsung bersamaan dengan implementasi prototipe tipis (*spike*). |
| **A-004** | — | `RISK-001` | Siapkan rancangan alternatif menggunakan Mailcow, WildDuck, atau relay pihak ketiga. |
| **A-005** | `Q-004` | `RISK-001` | Perketat akses pembuatan mailbox sementara hanya untuk klien yang terdaftar/memiliki kunci API. |
| **A-006** | `Q-004` | — | Standarisasi seluruh akses menggunakan akun terdaftar penuh (*unified user account*). |
| **A-007** | — | — | Terapkan skema sub-domain otomatis yang dikelola langsung oleh platform DomiBox. |
| **A-008** | — | — | Migrasikan konfigurasi orchestrator ke Kubernetes/Nomad jika skalabilitas horizontal langsung dibutuhkan. |
| **A-009** | `Q-003` | — | Terapkan hard-delete instan saat sesi browser ditutup jika background job tidak memungkinkan. |

---

## 4. Prosedur Pembaruan Status Asumsi
1. **Validasi (Assumption → Validated):** Terjadi ketika keputusan owner telah dicatat di `decision-log.md` atau hasil spike teknis membuktikan asumsi tersebut benar. Status diubah menjadi `VALIDATED` dengan mencantumkan tautan bukti.
2. **Pembatalan (Assumption → Invalidated):** Terjadi jika asumsi terbukti keliru atau tidak dapat diterapkan. Dampak pembatalan harus diidentifikasi dan ditindaklanjuti dengan merevisi dokumen arsitektur/spesifikasi terkait.
3. **Penambahan Asumsi Baru:** Asumsi baru yang muncul selama perancangan fase 3–10 wajib ditambahkan ke log ini dengan nomor urut berikutnya (`A-010`, dst) untuk mempertahankan catatan terpusat.
