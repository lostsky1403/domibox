# Security & Privacy Requirements Specification - DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/ReqCore | `docs/00-governance/project-charter.md`<br>`docs/00-governance/documentation-standards.md`<br>`docs/00-governance/open-questions.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/01-product/mvp-scope.md`<br>`docs/02-requirements/brd.md`<br>`docs/02-requirements/srs.md`<br>`docs/02-requirements/traceability/traceability-matrix.md` |

---

## 1. Pendahuluan & Prinsip Keamanan Sistem (Security Principles)

Platform **DomiBox** menangani aliran data pesan email yang berpotensi mengandung informasi sensitif, seperti kode verifikasi otentikasi (*One-Time Password* / OTP), tautan aktivasi akun (*magic link*), dan data pribadi pengirim. Oleh karena itu, arsitektur DomiBox dibangun di atas prinsip-prinsip dasar keamanan rekayasa perangkat lunak:
1. **Pemisahan Hak Istimewa (*Principle of Least Privilege*):** Hak akses administratif domain dipisahkan secara tegas dari akses pengguna mailbox sementara.
2. **Pertahanan Berlapis (*Defense-in-Depth*):** Validasi dilakukan di setiap lapisan sistem, mulai dari batas jaringan SMTP, parser MIME, lapisan API, hingga peramban klien.
3. **Privasi Berdasarkan Rancangan (*Privacy by Design & Default*):** Pesan email sementara bersifat fana (*ephemeral*), otomatis dibersihkan (*auto-purged*), dan tidak disimpan lebih lama dari yang dibutuhkan pengguna.
4. **Isolasi Konten Berbahaya (*Zero-Trust Content Handling*):** Seluruh konten email HTML dari pihak luar dianggap berbahaya (*untrusted payload*) dan harus disanitasi serta diisolasi sebelum disajikan.

---

## 2. Keterkaitan dengan Isu Tata Kelola & Batasan MVP (`Q-003`, `Q-004`)

Penyusunan kebutuhan keamanan ini secara sadar menavigasi dua pertanyaan terbuka utama:
- **`Q-003` (Batas Cakupan MVP):** Sistem keamanan difokuskan pada mitigasi eksploitasi penerimaan email masuk (*inbound abuse*) dan pemaparan data mailbox sementara. Pencegahan penyalahgunaan email keluar (*outbound spam relaying*) diselesaikan secara radikal pada rilis MVP dengan menonaktifkan kapabilitas pengiriman email keluar secara total (`F1` / `ADR-0010`).
- **`Q-004` (Model Otentikasi & Identitas):** Mengingat model identitas formal masih dalam evaluasi arsitektur, kebutuhan keamanan membagi kontrol otentikasi menjadi:
  - *Admin Master Access:* Kunci rahasia/token administrator untuk pengelolaan domain dan konfigurasi sistem.
  - *Ephemeral Token Isolation:* Token akses acak unik berkekuatan kriptografis (*cryptographically secure random token*) untuk setiap mailbox sementara yang dihasilkan.

---

## 3. Matriks Kebutuhan Keamanan & Kontrol Privasi (`SEC-*`)

| ID Kontrol | Aspek Keamanan / Kategori | Pernyataan Kebutuhan Keamanan & Kontrol Teknis | Mitigasi Ancaman (Threat Mitigated) | Prioritas | Induk Kebutuhan | Status Bukti |
| --- | --- | --- | --- | :---: | :---: | :---: |
| **SEC-001** | Validasi Domain & Anti-Spoofing | Sistem harus memvalidasi kepemilikan domain kustom melalui rekaman DNS TXT acak yang unik sebelum domain diizinkan aktif menerima pesan email. | *Domain Hijacking / Unauthorized Domain Claim:* Pihak tak berwenang mendaftarkan domain milik orang lain untuk menyadap email. | **Wajib** | `BR-001`, `DOM-001` | `VERIFIED` |
| **SEC-002** | Isolasi Akses Mailbox Sementara | Setiap pembuatan mailbox sementara harus menghasilkan token akses acak URL-safe (panjang minimal 32 karakter, entropi tinggi). Akses membaca pesan wajib menyertakan token ini (via Header HTTP atau Parameter Otentikasi). | *Unauthorized Mailbox Snooping / Insecure Direct Object References (IDOR):* Penyerang menebak alamat mailbox untuk membaca kode OTP orang lain. | **Wajib** | `BR-004`, `MBX-001` | `VERIFIED` |
| **SEC-003** | Pembatasan Kuota & Anti-Exhaustion | Sistem harus menerapkan batasan ketat pada mailbox sementara: maksimal 50 pesan masuk atau total ukuran 10 MB per mailbox; pesan baru yang melebihi batas ini ditolak secara otomatis. | *Denial of Service (DoS) via Storage Exhaustion:* Pengirim jahat membombardir satu alamat hingga disk VPS penuh. | **Wajib** | `BR-004`, `MBX-001` | `PROPOSED` |
| **SEC-004** | Validasi Reputasi Pengirim (SPF/DKIM/DMARC) | Sistem harus mengevaluasi status otentikasi pengirim (SPF, DKIM, DMARC) dan menandai pesan yang gagal verifikasi dengan penanda peringatan visual (*warning badge*) pada antarmuka pengguna. | *Email Spoofing & Phishing:* Penyerang memalsukan alamat pengirim dari institusi resmi (misal: bank/SaaS) untuk mengelabui pengguna. | **Wajib** | `BR-004`, `INB-001` | `VERIFIED` |
| **SEC-005** | Sanitasi Konten Email & Anti-XSS | Sistem wajib melakukan sanitasi ketat terhadap konten email HTML menggunakan pustaka parser aman (seperti *ammonia* atau *DOMPurify*), menonaktifkan seluruh tag `<script>`, `<iframe>`, `<object>`, event handler inline (`onerror`, `onclick`), serta memblokir pelacak gambar (*tracking pixels*) eksternal secara default. | *Stored Cross-Site Scripting (XSS) & Cross-Site Tracking:* Penyerang menyisipkan muatan JavaScript jahat ke badan email untuk mencuri token sesi atau memprofilkan IP pengguna. | **Wajib** | `BR-004`, `WEB-001` | `VERIFIED` |
| **SEC-006** | Otentikasi Penautan Bot Telegram | Interaksi bot Telegram wajib diawali proses penautan (*pairing*) satu kali menggunakan token berbatas waktu dari antarmuka Web Admin. Seluruh pesan/perintah dari Chat ID yang tidak terdaftar harus diabaikan seketika. | *Unauthorized Bot Control / Information Leakage:* Pengguna Telegram lain mencoba mengirim perintah ke bot untuk mencuri pesan atau membuat alamat liar. | **Wajib** | `BR-003`, `BOT-001` | `PROPOSED` |
| **SEC-007** | Proteksi Antarmuka Web (CSP & CSRF) | Web Dashboard harus menerapkan header keamanan HTTP ketat: `Content-Security-Policy` (CSP), `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, serta proteksi CSRF berbasis token ganda (*Double Submit Cookie*) atau header custom. | *Clickjacking, MIME-Sniffing, & Cross-Site Request Forgery (CSRF).* | **Wajib** | `BR-004`, `WEB-001` | `VERIFIED` |
| **SEC-008** | Audit Trail & Log Anti-Manipulasi | Log mutasi sistem (pendaftaran domain, penghapusan data, perubahan konfigurasi, kegagalan otentikasi) harus dicatat pada file append-only lokal dengan format terstruktur, disertai metadata IP penyeru dan waktu presisi tinggi. | *Repudiation & Covert Sabotage:* Pelaku penyalahgunaan mencoba menghapus jejak aktivitas dari sistem. | **Penting** | `BR-004`, `OPS-001` | `VERIFIED` |
| **SEC-009** | Pembatasan Laju Pembuatan Mailbox (*Rate Limiting*) | Sistem harus membatasi frekuensi pembuatan mailbox sementara dari satu alamat IP asal (misal: maksimum 10 mailbox per menit per IP) dan mendukung integrasi CAPTCHA ringan/PoW jika terdeteksi anomali lonjakan. | *Automated Bot Abuse & Harvesting:* Script otomatis mengeksploitasi API untuk membuat jutaan mailbox dalam hitungan detik. | **Wajib** | `BR-004`, `MBX-001` | `PROPOSED` |
| **SEC-010** | Kebijakan Retensi Data & Hak Dilupakan (*Data Retention & Purge*) | Pesan pada mailbox sementara wajib dihapus secara permanen (*hard delete*, termasuk metadata pesan dan lampiran terkait) segera setelah waktu kedaluwarsa tercapai atau atas permintaan pengguna. Sistem dilarang menyimpan riwayat pesan pasca-kedaluwarsa. | *Data Leakage from Abandoned Accounts / Privacy Non-Compliance:* Sisa-sisa pesan sensitif tertinggal di basis data dan berpotensi terakses kembali. | **Wajib** | `BR-004`, `OPS-001` | `VERIFIED` |
| **SEC-011** | Pembatasan Akses Jaringan Lokal (*Network Isolation*) | Seluruh kontainer aplikasi internal DomiBox dilarang mengekspos port basis data atau antarmuka internal ke alamat IP publik `0.0.0.0`; port internal hanya terikat pada loopback (`127.0.0.1`) atau jaringan internal Docker bridge. | *Unauthorized External Database Access / Port Scanning:* Pihak eksternal mengakses langsung port PostgreSQL atau cache internal dari internet. | **Wajib** | `BR-004`, `OPS-001` | `VERIFIED` |
| **SEC-012** | Isolasi Lampiran Berbahaya (*Attachment Handling*) | Sistem tidak boleh mengizinkan eksekusi langsung berkas lampiran dari peramban web. Lampiran yang disajikan untuk diunduh wajib menyertakan header `Content-Disposition: attachment; filename="..."` dan dipindai ekstensi terlarang (misal: `.exe`, `.bat`, `.scr`, `.vbs`). | *Drive-By Malware Download & Execution:* Pengguna tanpa sengaja mengeksekusi lampiran virus dari email spam. | **Penting** | `BR-004`, `INB-001` | `PROPOSED` |

---

## 4. Spesifikasi Kontrol Privasi Khusus (Targeted Privacy Controls)

### 4.1 Anonimisasi Log Akses (Access Log Sanitization)
- **Penyamaran Alamat IP:** Dalam pencatatan log akses HTTP publik untuk antarmuka pembacaan mailbox sementara, oktet terakhir alamat IPv4 (atau 80 bit terakhir IPv6) disamarkan (*masked*, misal: `192.168.1.xxx`) guna melindungi privasi penjelajahan pengguna sementara.
- **Pembersihan Parameter Sensitif:** Token akses rahasia tidak boleh dicatat dalam berkas akses log peramban web/reverse proxy (harus dikirim melalui Header HTTP `X-Mailbox-Token`, bukan URL query parameter).

### 4.2 Pemblokiran Pelacak Eksternal (*Anti-Tracking Beacon Protection*)
- Email pemasaran sering kali menyematkan elemen gambar berukuran 1x1 piksel (*tracking pixel*) untuk mengetahui waktu pembacaan email dan alamat IP penerima.
- Kontrol `SEC-005` mewajibkan pemblokiran pemuatan gambar eksternal secara default. Pengguna diberikan tombol eksplisit *"Tampilkan Gambar Eksternal"* jika mereka secara sadar ingin memuat elemen gambar tersebut.

---

## 5. Rencana Pengujian Keamanan & Validasi (Security Verification Plan)

Setiap kontrol keamanan `SEC-*` dipetakan ke dalam skenario pengujian keamanan (*Security Test Plan*) pada fase pengujian:
- `SEC-001`: Diuji melalui skenario verifikasi DNS spoofing injection.
- `SEC-002`, `SEC-003`, `SEC-009`: Diuji melalui pengujian penetrasi API IDOR, batas kuota, dan flooding attack.
- `SEC-004`: Diuji dengan pengiriman email uji coba bertanda tangan SPF/DKIM tidak valid.
- `SEC-005`, `SEC-007`: Diuji menggunakan suite pengujian XSS (*XSS Cheat Sheet payloads*) pada viewer HTML dan audit header HTTP.
- `SEC-006`: Diuji dengan upaya injeksi perintah Telegram dari akun Chat ID tak terdaftar.
- `SEC-010`: Diuji dengan audit konsistensi basis data pasca eksekusi pembersihan otomatis.
