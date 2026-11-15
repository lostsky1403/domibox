# Master Test Plan & Quality Strategy (DomiBox)

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/QualityDocs | `docs/02-requirements/srs.md`<br>`docs/02-requirements/traceability/traceability-matrix.md` |

---

## 1. Strategi Kualitas & Piramida Pengujian
Platform DomiBox mengadopsi piramida pengujian otomatis untuk menjamin stabilitas fungsional, integritas isolasi keamanan, dan ketahanan operasional:
1. **Unit Tests (Vitest):** Pengujian terisolasi fungsi parsing MIME, logika ekstraksi OTP, validasi format domain/email, enkripsi token, dan kalkulasi batas kedaluwarsa TTL. Cakupan target: >=85% branch coverage.
2. **Integration Tests (Supertest + Testcontainers PostgreSQL & Mock SMTP):** Pengujian integrasi rute API Fastify, transaksi basis data, penanganan konkurensi, dan komunikasi HTTP/JMAP.
3. **End-to-End Tests (Playwright):** Skenario penjelajahan Web Dashboard (login, pembuatan mailbox, penerimaan email simulasi, pratinjau pesan, penyalinan OTP otomatis).

---

## 2. Katalog Kasus Uji Utama (`TC-*` Traceability Matrix)

| ID Uji | Modul / Kebutuhan | Deskripsi Kasus Uji | Tipe Pengujian | Kriteria Keberhasilan (*Expected Result*) | Status |
| :--- | :--- | :--- | :---: | --- | :---: |
| `TC-001` | `DOM-001` | Pendaftaran domain baru dan pengecekan verifikasi DNS TXT/MX. | Integrasi | Status domain berubah menjadi `ACTIVE` saat rekaman DNS terdeteksi valid. | `PROPOSED` |
| `TC-002` | `MBX-001` | Pembuatan temporary mailbox acak dengan durasi TTL 30 menit. | Integrasi | Mailbox terbuat, alias terdaftar di Stalwart, waktu kedaluwarsa `expires_at` tepat. | `PROPOSED` |
| `TC-003` | `MBX-003` | Pembuatan permanent mailbox atau konversi permanen dengan kustom local part. | Integrasi | Mailbox terbuat tanpa `expires_at`, alias permanen terdaftar di Stalwart. | `PROPOSED` |
| `TC-004` | `INB-001` | Penerimaan email masuk via pipeline SMTP port 25 (`F1`). | E2E / Integrasi | Pesan masuk disimpan di DB, muncul di inbox Web Dashboard dalam <2 detik. | `PROPOSED` |
| `TC-005` | `OTP-001` | Ekstraksi kode OTP 6-digit dari subjek dan isi email HTML. | Unit / Integrasi| Nilai `extracted_otp` bernilai string angka 6-digit yang akurat. | `PROPOSED` |
| `TC-006` | `BOT-001` | Pengiriman notifikasi OTP instan ke Telegram Bot via webhook. | Integrasi | Pesan Telegram terkirim ke chat ID terhubung dengan tombol salin cepat. | `PROPOSED` |
| `TC-007` | `SEC-005` | Sanitasi email HTML yang memuat skrip berbahaya `<script>alert(1)</script>`.| Keamanan (Unit) | Skrip berbahaya terhapus, rendering dalam iframe aman tanpa eksekusi kode (`SEC-005`). | `PROPOSED` |
| `TC-008` | `OPS-002` | Eksekusi penjadwal auto-purge untuk mailbox dan email kedaluwarsa (`MBX-005`, `F4`). | Integrasi / Cron | Mailbox berstatus `expired`, pesan email terhapus, jejak audit log tercatat. | `PROPOSED` |

---

## 3. Ambang Batas Gerbang Kualitas (Quality Gates)
- **Definition of Ready (DoR):** Kebutuhan memiliki ID kanonikal, kriteria penerimaan Gherkin terdefinisi, pemetaan keterlacakan ke RTM lengkap.
- **Definition of Done (DoD):** Kode lulus linting ESLint/TypeScript, tes unit dan integrasi lulus 100%, dokumentasi API diperbarui, tidak ada celah keamanan kritis dalam pemindaian dependensi.
