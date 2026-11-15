# Riset Kontrol Keamanan & Privasi (Security Controls Research) — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/SecCore | `docs/00-governance/project-charter.md`<br>`docs/02-requirements/security-privacy-requirements.md`<br>`docs/05-security/threat-model.md`<br>`docs/03-architecture/adr/ADR-009.md` |

---

## 1. Tujuan Riset & Sasaran Perlindungan
Riset ini mendefinisikan dan mengkaji kontrol keamanan, mitigasi vektor serangan email, dan mekanisme proteksi privasi untuk platform **DomiBox**. Sebagai platform penerima email publik, DomiBox terekspos langsung terhadap ancaman eksekusi kode berbahaya (XSS), pelacakan privasi (*tracking beacons*), serangan kehabisan sumber daya (*resource exhaustion*), dan kebocoran kode verifikasi otentikasi (OTP).

---

## 2. Register Kontrol Keamanan & Mitigasi Ancaman (Security Controls Matrix)

| ID Kontrol | Domain Keamanan | Pernyataan Kontrol & Mitigasi Teknis | Mitigasi Ancaman (STRIDE) | Status Bukti | Rujukan Standar / Dokumen |
| :---: | --- | --- | --- | :---: | --- |
| **SEC-001** | Validasi Kepemilikan Domain | Validasi rekaman DNS TXT acak unik dengan entropi $\ge 128$ bit sebelum domain kustom diizinkan menerima email masuk. | *Spoofing / Domain Hijacking:* Pihak tak berwenang mendaftarkan domain milik orang lain. | `VERIFIED` | `SEC-REQ-001`, `ADR-010` |
| **SEC-002** | Isolasi Token Akses Mailbox | Penyerahan token akses berkekuatan kriptografis (`crypto.randomBytes(24).toString('base64url')`) per mailbox sementara. Akses membaca pesan wajib menyertakan token ini via header `X-Mailbox-Token`. | *Information Disclosure / IDOR:* Penyerang menebak alamat email acak untuk menyadap kode OTP. | `VERIFIED` | `SEC-REQ-002`, `ADR-009` |
| **SEC-003** | Kuota & Batas Sumber Daya | Pembatasan ketat: maksimal 50 pesan masuk atau total 10 MB per mailbox sementara. Transaksi SMTP baru ditolak dengan kode respon SMTP 552 jika kuota terlampaui. | *Denial of Service (DoS):* Serangan pemborosan ruang penyimpanan VPS (*Disk Exhaustion*). | `PROPOSED` | `SEC-REQ-003`, `NFR-001` |
| **SEC-004** | Validasi Reputasi Pengirim | Penerapan verifikasi otomatis SPF, DKIM, dan DMARC oleh engine Stalwart pada saat koneksi SMTP inbound. Pesan yang gagal verifikasi ditandai status peringatan pada antarmuka. | *Spoofing / Phishing:* Penyerang memalsukan pengirim email institusi finansial/SaaS. | `VERIFIED` | `SEC-REQ-004`, `ADR-002` |
| **SEC-005** | Sanitasi HTML & Isolasi XSS | Seluruh badan email HTML dibersihkan menggunakan DOMPurify (menghapus `<script>`, atribut `on*`, tag `object`/`embed`) dan dirender di dalam `<iframe sandbox="allow-same-origin">` tanpa izin eksekusi skrip. | *Elevation of Privilege / Stored XSS:* Penyerang menyisipkan muatan JavaScript jahat pada email masuk. | `VERIFIED` | `SEC-REQ-005`, `threat-model.md` |
| **SEC-006** | Pembatasan Akses Bot Telegram | Bot hanya memproses perintah dari Telegram Chat ID yang telah terdaftar dalam tabel allowlist terverifikasi milik pemilik (*Admin Pairing via One-Time Token*). | *Unauthorized Access:* Pihak luar berinteraksi dengan bot untuk melihat pesan atau mengelola domain. | `VERIFIED` | `SEC-REQ-006`, `ADR-008` |
| **SEC-007** | Kebijakan Header Keamanan Web | Caddy Server menyuntikkan header keamanan ketat: `Content-Security-Policy: default-src 'self'`, `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, dan `Strict-Transport-Security`. | *Tampering / Clickjacking / MIME Sniffing:* Eksploitasi kelemahan browser klien. | `VERIFIED` | `SEC-REQ-007`, `ADR-001` |
| **SEC-008** | Penonaktifan Outbound SMTP Total | Memastikan port 25/465/587 keluar ditutup total di tingkat konfigurasi Stalwart dan firewall UFW pada fase MVP. | *Reputation Loss / Outbound Abuse:* Kompromi sistem yang mengubah VPS menjadi sumber pengirim spam global. | `VERIFIED` | `F1`, `SEC-REQ-008`, `ADR-010` |
| **SEC-009** | Rate Limiting Lapisan API | Pembatasan laju panggilan REST API publik: maksimal 100 permintaan/menit per alamat IP menggunakan algoritma sliding window memory di Fastify. | *Denial of Service / Brute Force:* Upaya flooding permintaan pembuatan mailbox atau polling inbox. | `PROPOSED` | `SEC-REQ-009`, `NFR-004` |
| **SEC-010** | Pemusnahan Data Permanen (*Purge*) | Eksekusi pembersihan terjadwal yang menghapus baris database, berkas MIME blob dari disk, dan alias routing JMAP tanpa meninggalkan jejak pemulihan (*irreversible deletion*). | *Information Disclosure:* Pesan sementara yang telah kedaluwarsa tetap tersimpan di server. | `VERIFIED` | `F4`, `SEC-REQ-010`, `ADR-011` |

---

## 3. Spesifikasi Kontrol Privasi Khusus (Targeted Privacy Specification)

### 3.1 Pencegahan Pelacakan Pixel (*Anti-Beacon Tracking*)
Email pemasaran sering kali menyematkan elemen gambar berukuran $1 \times 1$ piksel transparan dengan URL berparameter unik untuk melacak waktu pembacaan email, lokasi geografis, dan alamat IP peramban penerima.
- **Kebijakan DomiBox:**
  1. Seluruh tag `<img src="...">` eksternal diganti sementara dengan atribut `data-src` saat sanitasi.
  2. Gambar eksternal diblokir secara default (*Blocked by Default*).
  3. Antarmuka web menyajikan tombol interaktif: *"Tampilkan Gambar Eksternal"* yang memuat gambar hanya jika diklik secara sadar oleh pengguna.

### 3.2 Penyamaran Alamat IP Pengguna Sementara (*IP Masking*)
Pada log akses reverse proxy (Caddy) dan audit trail, alamat IP dari permintaan publik yang mengakses mailbox sementara disamarkan (misalnya `103.21.244.xxx`) untuk mencegah korelasi identitas penjelajahan pengguna dengan alamat email yang dibuat.

---

## 4. Kesimpulan & Status Validasi
Kontrol keamanan DomiBox dirancang dengan arsitektur pertahanan berlapis (*Defense-in-Depth*). Aspek sanitasi XSS (`SEC-005`) dan isolasi token (`SEC-002`) telah memiliki dasar implementasi terverifikasi pada pustaka open-source standar industri, sedangkan parameter kuota (`SEC-003`) dan rate limit (`SEC-009`) berstatus `PROPOSED` hingga pengujian beban riil dilakukan.
