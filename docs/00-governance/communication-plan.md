# Communication Plan — Review, Approval & Governance Cadence (DomiBox)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Governance / Orchestrator`  
**Related Documents:**
- `docs/00-governance/revision-and-approval-policy.md`
- `docs/00-governance/raci-matrix.md`
- `docs/00-governance/open-questions.md`
- `docs/00-governance/decision-log.md`
- `docs/08-delivery/`

---

## 1. Purpose & Objectives
Rencana komunikasi ini merinci saluran komunikasi, frekuensi pertemuan, alur peninjauan (*review*), dan mekanisme eskalasi untuk tata kelola dokumentasi serta inisiasi proyek DomiBox. Tujuannya adalah memastikan transparansi keputusan, akurasi pelacakan (*traceability*), dan keterlibatan pihak yang tepat tanpa menciptakan friksi berlebih.

---

## 2. Saluran Komunikasi (Proposed Channels)

| Saluran | Tujuan / Penggunaan | Audiens / Partisipan | Frekuensi / Waktu | Status |
| :--- | :--- | :--- | :--- | :--- |
| **GitHub Issues & PRs** | Peninjauan formal dokumen, diff tracking, komentar baris (*line comments*), dan persetujuan merge. | Pengembang, Reviewer, Approver | Asinkron / Berbasis Event (*per PR*) | `PROPOSED` |
| **Jira Software (DBX Board)** | Pelacakan progres tugas, backlog grooming, status sprint, blocker flag, dan ketergantungan. | Tim Inti Proyek, Product Owner | Kontinu / Real-time | `PROPOSED` |
| **Weekly Architecture & Tech Sync** | Sinkronisasi keputusan arsitektur (ADR), evaluasi teknologi, keamanan, dan pembahasan `Q-*` terbuka. | Architect, Tech Lead, Security, Ops | Mingguan (45–60 menit) | `PROPOSED` |
| **Documentation Review Gate** | Tinjauan tonggak capaian (*milestone review*) untuk menyetujui baseline dokumentasi (`PROPOSED` → `APPROVED`). | Semua Pemilik Dokumen, PO | Akhir setiap Milestone (M1, M2, M3) | `PROPOSED` |
| **Ad-hoc Blocker Escalation** | Eskalasi hambatan kritis (misal: otentikasi eksternal, izin infrastruktur, kontradiksi dokumen). | Orchestrator, Lead terkait, PO | Kapan pun diperlukan (< 24 jam respons) | `PROPOSED` |

---

## 3. Matriks Komunikasi Berdasarkan Fase Proyek

| Fase / Tonggak | Sasaran Komunikasi | Format / Saluran | Pihak Bertanggung Jawab | Penerima Laporan |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0–2: Governance & Preflight** | Laporan kesiapan tooling, identifikasi celah riset, standar dokumentasi awal. | PR Summary, Audit Register | Orchestrator | Tim Pengembang, Sponsor |
| **Phase 3–4: Requirements & Arch** | Penyelarasan kebutuhan bisnis (`BR-*`), spesifikasi teknis, ADR draft, verifikasi batasan sistem. | GitHub PR draft, Architecture Review | Product Lead, Architect | Tim Teknis, QA, Security |
| **Phase 5–7: Tech, Sec & Ops** | Tinjauan kontrak API, threat model, pipeline CI/CD, kesiapan operasional server. | Spec walkthrough, Issue comments | Tech Lead, Security Lead | DevOps, QA, Lead Arch |
| **Phase 8–10: Delivery & Review** | Prioritas backlog Jira, cross-document contradiction check, resolusi temuan tinjauan. | Jira Dashboard, Review Matrix | Delivery Lead, Reviewer | Seluruh Tim Proyek |
| **Phase 11–13: Sync & Baseline** | Laporan final audit, sinkronisasi Jira, status draft PR, ringkasan bukti nyata. | Final Audit Summary, PR Description | Orchestrator | Project Sponsor |

---

## 4. Alur Kerja Peninjauan Dokumen (Review Workflow)

```mermaid
flowchart TD
    A[Penulis Membuat / Mengubah Dokumen (PROPOSED)] --> B[Buka GitHub Draft PR / Review Request]
    B --> C{Peninjau Memeriksa Kepatuhan Standar}
    C -->|Ada Pelanggaran Standar / Fakta Mengada-ada| D[Beri Komentar & Kembalikan ke Penulis]
    D --> A
    C -->|Lolos Standar & Metadata Valid| E{Pemeriksaan Substantif Teknis & Keamanan}
    E -->|Butuh Perubahan Teknis / Klarifikasi| F[Catat ke open-questions.md / PR Comments]
    F --> A
    E -->|Disetujui oleh Pemegang Peran Accountable| G[Status Dokumen Menjadi APPROVED]
    G --> H[Catat Keputusan ke decision-log.md jika Signifikan]
    H --> I[Update Document Control Register & RTM]
```

---

## 5. Protokol Eskalasi & Resolusi Pertanyaan Terbuka

1. **Pencatatan Awal:** Setiap ketidakpastian atau ketiadaan bukti pendukung wajib segera dicatat di `docs/00-governance/open-questions.md` dengan ID unik `Q-###`.
2. **Kategori Pertanyaan:**
   - **Tinggi (High / Blocker):** Menghambat kemajuan fase berjalan (misal: ketiadaan batasan MVP, otentikasi repo). Wajib dibahas dalam waktu 1x24 jam.
   - **Sedang (Medium):** Mempengaruhi detail spesifikasi tetapi tidak menghentikan draf keseluruhan. Dibahas pada sesi mingguan.
   - **Rendah (Low):** Pertanyaan penyempurnaan gaya bahasa atau format opsional.
3. **Penyelesaian:** Ketika jawaban definitif disepakati, status `Q-###` diubah menjadi `Closed`, keputusan dicatat pada `decision-log.md` (`DEC-###`) atau `docs/03-architecture/adr/`, dan dokumen yang terdampak diperbarui.

---

## 6. Tata Tertib Pelaporan Status
- **Transparansi Bukti:** Status tidak boleh ditandai `APPROVED` atau `VERIFIED` tanpa bukti nyata (link, hash commit, atau catatan verifikasi teknis).
- **Format Catatan Pertemuan (MoM):** Setiap keputusan substantif dari rapat asinkron maupun sinkron harus didokumentasikan dalam format standar ringkas (Tanggal, Partisipan, Keputusan, Tindak Lanjut).
- **Bahasa Komunikasi:** Komunikasi formal dokumentasi dan laporan menggunakan Bahasa Indonesia baku, dengan istilah teknis bahasa Inggris tetap dipertahankan untuk presisi teknik.
