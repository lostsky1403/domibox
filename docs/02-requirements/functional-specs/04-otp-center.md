# Spesifikasi Fungsional: Pusat Ekstraksi OTP (OTP Center) — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/ReqCore | `docs/00-governance/project-charter.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/02-requirements/srs.md`<br>`docs/04-technical/otp-extraction-specification.md` |

---

## 1. Ringkasan Modul
Modul Pusat Ekstraksi OTP (`OTP-###`) adalah komponen pembeda utama DomiBox yang bertugas mengidentifikasi, mengekstrak, dan menyajikan kode verifikasi numerik/alfanumerik (4–8 karakter) serta tautan konfirmasi (*magic link*) dari badan email masuk menggunakan algoritma heuristik berbasis regex teruji.

---

## 2. Rincian Kebutuhan Fungsional Ekstraksi OTP

| ID Kebutuhan | Nama Kebutuhan | Deskripsi Fungsional & Aturan Bisnis | Kriteria Penerimaan (Acceptance Criteria) | Prioritas | Status Bukti |
| :---: | --- | --- | --- | :---: | :---: |
| **OTP-001** | Deteksi & Ekstraksi Kode OTP Numerik | Sistem memindai subjek dan badan teks email untuk menemukan pola kode angka 4 hingga 8 digit yang berdekatan dengan kata kunci verifikasi (*verification code, OTP, PIN, token, kode konfirmasi*). | Kode numerik diekstraksi dengan benar dan disimpan pada kolom `otp_code`. | **Wajib** | `VERIFIED` |
| **OTP-002** | Deteksi Kode Alfanumerik | Sistem mengekstrak kode verifikasi alfanumerik (misal format `AB-1234` atau `9X2A8B`) yang terikat pada kata kunci otentikasi. | Format alfanumerik dikenali tanpa salah mendeteksi hash sistem atau ID transaksi. | **Penting** | `PROPOSED` |
| **OTP-003** | Identifikasi Tautan Verifikasi (*Magic Link*) | Sistem mengekstrak URL konfirmasi aktivasi akun dari tautan anchor teks umum (*Verify Email, Confirm Registration, Activate Account*). | URL tersimpan pada kolom `magic_link` dan disajikan sebagai tombol navigasi langsung. | **Penting** | `PROPOSED` |
| **OTP-004** | Penanganan Ambiguitas & Kode Ganda | Jika dalam satu pesan terdeteksi lebih dari satu kandidat kode angka (misalnya nomor telepon CS vs kode OTP), algoritma memberi skor pembobotan berbasis kedekatan kata kunci. | Kandidat dengan skor heuristik tertinggi disajikan sebagai kode utama; sisanya dicatat sebagai kandidat alternatif. | **Penting** | `PROPOSED` |
| **OTP-005** | Penyajian Responsif & Tombol Salin 1-Klik | Setiap kode OTP yang berhasil diekstraksi wajib disajikan pada banner atas penampil pesan (Web) dan tombol inline pesan Telegram. | Mengklik tombol langsung menyalin kode ke clipboard sistem operasi. | **Wajib** | `VERIFIED` |

---

## 3. Matriks Pola Heuristik Regex Ekstraksi

```text
1. Pola Standar Numerik (4-8 Digit):
   /(?:code|otp|pin|verification|verifikasi|token)[\s:=]+([0-9]{4,8})\b/i

2. Pola Berpemisah Strip (Hyphenated):
   /(?:code|otp|pin)[\s:=]+([0-9]{3}-[0-9]{3})\b/i

3. Pola Subjek Email Langsung:
   /^[0-9]{4,8}\s+(?:is your|adalah kode)/i
```
