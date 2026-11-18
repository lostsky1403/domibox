# OTP & Magic Link Extraction Specification — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/TechSpec | `docs/02-requirements/functional-specs/04-otp-center.md`<br>`docs/04-technical/api/openapi.yaml`<br>`docs/02-requirements/srs.md` |

---

## 1. Ikhtisar Mesin Ekstraksi OTP
Pusat ekstraksi OTP (`OTP-001` s/d `OTP-005`) dirancang untuk meminimalkan friksi pengguna dalam proses verifikasi identitas pendaftaran atau login. Alih-alih mengharuskan pengguna membaca keseluruhan email yang panjang dan sarat elemen visual, sistem mengekstrak kode verifikasi numerik/alfanumerik atau tautan verifikasi instan secara otomatis dengan tingkat akurasi target ≥ 95% (`NFR-005`).

---

## 2. Pola Heuristik & Aturan Regular Expression (Regex Matrix)

### 2.1 Ekstraksi Kode Numerik (`OTP-001`)
Kode OTP numerik standar terdiri dari 4 hingga 8 digit angka yang dikelilingi oleh kata kunci kontekstual:
- **Regex Pola Kontekstual Utama:**
  ```regex
  (?:code|kode|otp|verification|verifikasi|pin|password|sandi|token)[^\d\r\n]{1,30}\b(\d{4,8})\b
  ```
- **Regex Subjek Email:**
  ```regex
  \b(\d{4,8})\b.*(?:code|kode|otp|verification|verifikasi)
  ```

### 2.2 Ekstraksi Kode Alfanumerik (`OTP-002`)
Kode alfanumerik (mis. token aktivasi huruf-angka kombinasi 6–12 karakter tanpa karakter ambigu):
- **Regex Pola Alfanumerik:**
  ```regex
  (?:code|kode|token|verification)[^a-zA-Z0-9\r\n]{1,25}\b([A-Z0-9]{6,10})\b
  ```

### 2.3 Ekstraksi Magic Link / Tautan Aktivasi (`OTP-003`)
Tautan verifikasi satu-klik yang ditemukan dalam elemen anchor HTML (`<a href="...">`) atau teks murni:
- **Pola Kata Kunci URL / Teks Anchor:**
  - `verify`, `activate`, `confirm`, `konfirmasi`, `verifikasi`, `login`, `magic-link`.
- **Sanitasi URL:** Seluruh skema selain `http://` dan `https://` ditolak secara ketat (`SEC-005`). Karakter berbahaya di-escape sebelum disimpan pada kolom `extracted_link`.

---

## 3. Resolusi Ambiguitas & Pembobotan Skor Kepercayaan (`OTP-004`)
Jika ditemukan lebih dari satu pola angka dalam badan email (misalnya nomor telepon kontak pengirim, tahun hak cipta, atau ID transaksi):
1. **Pemberian Bobot Skor (Confidence Scoring):**
   - Muncul pada baris subjek: `+50 poin`.
   - Terletak tepat di samping kata kunci (`code`, `otp`, `verifikasi`): `+40 poin`.
   - Menggunakan tag HTML penekanan (`<strong>`, `<h1>`, `font-size > 18px`): `+30 poin`.
   - Panjang string tepat 6 digit (panjang paling umum OTP standar): `+20 poin`.
   - Diawali kata tahun (`2024`, `2025`, `2026`) atau didahului format mata uang (`Rp`, `$`, `USD`): `-80 poin` (Didiskualifikasi).
2. **Kandidat Terpilih:** Kandidat dengan skor tertinggi ditetapkan sebagai `extracted_otp`. Jika skor tertinggi di bawah ambang batas (ambang batas: 40 poin), kolom `extracted_otp` dibiarkan `NULL` dan pengguna diarahkan membaca teks email murni.
