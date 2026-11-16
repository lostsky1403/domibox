# Risk Register (DomiBox)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Governance / Project Lead (ReqTrace)`  
**Related Documents:**
- `docs/00-governance/project-charter.md`
- `docs/00-governance/open-questions.md`
- `docs/00-governance/decision-log.md`
- `docs/02-requirements/traceability/traceability-matrix.md`
- `docs/02-requirements/requirements-assumptions-register.md`

---

## 1. Tujuan & Metodologi (Purpose & Methodology)
Dokumen ini mengonsolidasikan seluruh risiko proyek, produk, teknis, operasional, dan tata kelola untuk inisiatif platform **DomiBox**. Identifikasi risiko mencakup risiko bawaan dari piagam proyek (*Project Charter*), pertanyaan terbuka (*Open Questions*), serta celah bukti riset (*Evidence Gaps*).

### Skala Penilaian Risiko (Risk Scoring Scale)
- **Kemungkinan (Probability / P):** `1` (Sangat Rendah), `2` (Rendah), `3` (Sedang), `4` (Tinggi), `5` (Sangat Tinggi)
- **Dampak (Impact / I):** `1` (Dapat Diabaikan), `2` (Minor), `3` (Moderat), `4` (Mayor), `5` (Bencana / Kritis)
- **Tingkat Keparahan (Severity = P × I):**
  - **`1 - 4`**: Rendah (*Low*) — Dapat diterima, pemantauan berkala.
  - **`5 - 9`**: Sedang (*Medium*) — Diperlukan rencana mitigasi terdefinisi.
  - **`10 - 15`**: Tinggi (*High*) — Perhatian aktif, tindakan preventif wajib sebelum rilis.
  - **`16 - 25`**: Kritis (*Critical*) — Menghambat proyek (*blocker*), eskalasi langsung ke Sponsor.

---

## 2. Register Risiko Terkonsolidasi (Consolidated Risk Register)

| ID Risiko | Deskripsi Risiko | Kategori | P (1-5) | I (1-5) | Tingkat Keparahan | Sumber / Pemicu Terkait | Strategi Mitigasi Terencana | Pemilik Risiko (Owner) | Status Penanganan |
| --- | --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| **RISK-001** | Ketiadaan bukti riset primer (*Problem-Value* & *Competitive Research*) menyebabkan basis kebutuhan dibangun di atas asumsi yang belum divalidasi pengguna. | Produk / Riset | 4 | 3 | **12 (Tinggi)** | Piagam Proyek §8, `Q-001`, `Q-002`, `GAP-001`, `GAP-002` | Memberi label eksplisit `PROPOSED` dan `GAP` pada dokumen riset; menjadwalkan validasi pengguna/kompetitor independen sebelum finalisasi rilis MVP. | Product Lead | **Terbuka (Open)** |
| **RISK-002** | Kendala autentikasi atau perizinan pada integrasi GitHub (push/PR) dan Jira (DBX sync) menghambat otomatisasi delivery baseline. | Tata Kelola / Tooling | 3 | 4 | **12 (Tinggi)** | Piagam Proyek §8, `Q-005`, `Q-006` | Menyiapkan seluruh artefak dokumentasi dan rencana sinkronisasi secara lokal terlebih dahulu; mencatat hasil riil eksekusi tanpa fabrikasi. | Orchestrator | **Terbuka (Open)** |
| **RISK-003** | Inkonsistensi format, terminologi, atau referensi ID antar dokumen akibat pembuatan artefak dalam skala besar. | Kualitas / Tata Kelola | 3 | 3 | **9 (Sedang)** | Piagam Proyek §8, `DEC-001`, `DEC-002` | Menerapkan RTM kanonikal (`traceability-matrix.md`), konvensi ID 3-digit ketat, dan fase tinjauan silang dokumen (*cross-document review*). | Quality / Governance | **Dalam Mitigasi (In Progress)** |
| **RISK-004** | Penyalahgunaan sistem mailbox sementara oleh pihak tak bertanggung jawab untuk aktivitas spam atau registrasi otomatis ilegal (*abuse*). | Keamanan / Operasional | 4 | 4 | **16 (Kritis)** | Analisis Kebutuhan `MBX-001`, `Q-003` | Penerapan pembatasan laju (*rate limiting*), verifikasi CAPTCHA pada antarmuka publik, isolasi domain pengirim, dan mekanisme *auto-purge* agresif. | Security Lead | **Terbuka (Open)** |
| **RISK-005** | Kerentanan injeksi kode jahat (*Cross-Site Scripting* / HTML injection) melalui payload email masuk yang ditampilkan pada dashboard web. | Keamanan Aplikasi | 4 | 4 | **16 (Kritis)** | Analisis Kebutuhan `INB-001`, `WEB-001` | Melakukan sanitasi konten HTML secara menyeluruh (*DOMPurify/sanitize-html*), merender isi email dalam iframe terisolasi dengan atribut `sandbox` ketat. | Tech / Security Lead | **Terbuka (Open)** |
| **RISK-006** | Kebocoran data sensitif atau kode OTP melalui kanal notifikasi bot Telegram jika terjadi kesalahan pairing akun atau kompromi webhook. | Privasi / Keamanan | 3 | 4 | **12 (Tinggi)** | Analisis Kebutuhan `BOT-001`, `Q-004` | Mewajibkan verifikasi token rahasia satu kali pakai (*one-time pairing code*), membatasi isi pesan bot hanya pada kode OTP tanpa menampilkan identitas lengkap pengirim. | Security Lead | **Terbuka (Open)** |
| **RISK-007** | Pemblokiran port 25 inbound oleh penyedia jaringan hosting (cloud/ISP) yang menyebabkan kegagalan penerimaan email masuk via SMTP. | Infrastruktur | 3 | 5 | **15 (Tinggi)** | Asumsi `A-REQ-003`, `mail-infrastructure-suitability.md` | Melakukan audit kelayakan port jaringan VPS sejak fase awal; menyediakan opsi arsitektur alternatif berbasis webhook email relay / API parser jika port 25 terblokir. | DevOps Lead | **Dalam Penyelidikan (Under Investigation)** |
| **RISK-008** | Ketidakjelasan model autentikasi antarmuka dashboard memicu keterlambatan perancangan skema basis data dan antarmuka otorisasi. | Arsitektur / Teknis | 3 | 3 | **9 (Sedang)** | `Q-004`, `GAP-004` | Mengusulkan model autentikasi berbasis Master API Key/Token untuk MVP, sembari merancang skema extensible untuk dukungan multi-user di Fase 2. | Architecture Lead | **Terbuka (Open)** |
| **RISK-009** | Stalwart Management API endpoints/permissions not verified from official documentation; §13 claims may be inaccurate. | Teknis / API | 3 | 3 | **9 (Sedang)** | `docs/08-delivery/plans/phase1-poc-execution-plan.md` §13 | PoC execution MUST validate Management API endpoints, authentication, and permissions against actual Stalwart v1.0.3 behavior before implementation; mark all §13 claims as NOT VERIFIED until validated. | Tech Lead | **Terbuka (Open)** |

---

## 3. Matriks Distribusi Risiko (Risk Heatmap)

```
        Tinggi ▲
               │
             5 │                       [RISK-007]
  Dampak     4 │            [RISK-002] [RISK-001]   [RISK-004]
  (Impact)     │                       [RISK-006]   [RISK-005]
             3 │                       [RISK-003]
               │                       [RISK-008]
             2 │
             1 │
        Rendah ▼───────────────────────────────────────────────►
                 1          2          3            4          5
               Rendah                           Tinggi
                         Kemungkinan (Probability)
```

---

## 4. Alur Pemantauan & Peninjauan Risiko (Review & Governance Cadence)
1. **Pembaruan Berkala:** Register risiko ini ditinjau pada setiap pergantian fase proyek atau jika terdapat resolusi atas pertanyaan terbuka (`Q-*`).
2. **Kriteria Penutupan Risiko:** Risiko dinyatakan *Closed* jika tindakan mitigasi telah diimplementasikan penuh, terverifikasi melalui pengujian (`TC-*`), dan tidak ada lagi dampak signifikan yang tersisa.
3. **Eskalasi:** Risiko dengan nilai keparahan $\ge 15$ wajib dilaporkan kepada Project Sponsor sebagai *top priority attention item*.
