# RISET KESESUAIAN INFRASTRUKTUR E-MAIL DOMIBOX

**STATUS:** `PROPOSED`

| | |
| --- | --- |
| **Status** | `PROPOSED` |
| **Versi** | `0.1` |
| **Tanggal** | `2026-11-14` |
| **Penulis** | `omp-orchestrator/riset-infrastruktur-mail` |
| **Dokumen Terkait** | `../../07-arsitektur/std.md` (Survei Arsitektur DomiBox) |

---

## 1. Ringkasan Eksekutif

Temuan-temuan berikut adalah ringkasan tingkat tinggi. Rincian dan sumber ada di section yang bersangkutan dengan status TERVERIFIKASI / HIPOTESIS.

1. **Port 25 inbound (SMTP) secara prinsip bisa diterima di VPS Tencent,** tetapi perlu dua lapisan konfigurasi terpisah: Security Group Tencent (lapisan infrastruktur) dan UFW (lapisan OS). Dokumen Tencent tentang "Unblocking Port 25" secara eksplisit membahas **outbound** dari CVM ke SMTP eksternal, **bukan inbound**. Status: **TERVERIFIKASI** (sumber Tencent Cloud, 2026-01-26).

2. **Outbound port 25 dari VPS diblokir default.** Jika DomiBox nanti butuh mengirim email keluar (outbound SMTP ke MX lain), VPS harus mengajukan "Unblock Port 25" via console Tencent. Hanya CVM berbayar (prepaid annual/monthly) yang didukung; pay-as-you-go tidak didukung. Status: **TERVERIFIKASI** (sumber Tencent Cloud, 2026-01-26).

3. **Tidak ada reverse proxy atau listener SMTP yang aktif** di VPS saat inspeksi. Port 25, 465, 587, 80, 443, 993 TIDAK terisi. Ini berarti Stalward yang di-deploy pertama kali bisa mengambil port tersebut tanpa bentrok dengan layanan lain — selama security group / UFW diatur. Status: **TERVERIFIKASI** (inspeksi VPS, 2026-11-14).

4. **Container `rustfs` (127.0.0.1:9000-9001) tidak bentrok** dengan port mail. Konflik yang mungkin terjadi hanya jika Stalwart di-configure salah bind ke 0.0.0.0 dengan port yang tumpang tindih, atau jika reverse proxy Caddy di-configure bind ke alamat yang sama. Status: **TERVERIFIKASI** (inspeksi VPS, 2026-11-14).

5. **Stalwart v1.0.3 sudah ada fitur `masked email` (Enterprise)** untuk alamat sementara/disposable yang di-forward ke akun asli. Ini adalah fitur yang paling relevan untuk model mailbox sementara. Fitur community edition hanya memiliki alias dan catch-all. Status: **TERVERIFIKASI** (dokumen Stalwart Labs, 2026-11-14).

6. **Cloudflare Email Routing mengambil alih MX domain secara penuh.** Mengaktifkan Email Routing berarti mengganti MX record domain ke `route1/2/3.mx.cloudflare.net` — **tidak bisa berjalan paralel** dengan mail server yang sudah ada di domain yang sama. Solusi: delegasi ke subdomain (`mail.domain.com`) atau gunakan provider lain untuk forwarding inbound yang tidak mengambil alih MX. Status: **TERVERIFIKASI** (dokumen Cloudflare dan artikel pihak ketiga yang menyebut mekanisme ini, 2026-11-14).

7. **Stalwart memiliki API JMAP penuh** untuk manajemen akun, alias, mailing list, quota, dan data retention. Tidak ada dokumentasi resmi tentang "auto-delete alamat otomatis berdasarkan TTL" untuk mailbox sementara — fitur ini TIDAK DITEMUKAN di docs Stalwart. Pendekatan alternatif: (a) memakai siklus hidup akun + permissions, (b) memakai JMAP API untuk menghapus akun saat expiry habis, (c) custom daemon eksternal. Status: **TIDAK TERVERIFIKASI — perlu verifikasi langsung ke docs Stalward + test di PoC.**

8. **Footprint sumber daya Stalwart + Postgres di VPS 2 vCPU / ~3.6 GB RAM** bukan angka yang dipublikasikan resmi oleh Stalwart Labs. Tidak ada benchmark publik yang bisa dirujuk. PoC benchmark WAJIB dijalankan sebelum keputusan produksi. Status: **TIDAK TERVERIFIKASI — perlu PoC benchmark.**

---

## 2. SMTP Ingress di Tencent Cloud

### 2.1 Konteks: inbound vs outbound

Penting untuk membedakan dua arah traffic SMTP:

- **Inbound (MX → VPS):** Mail provider eksternal mengirim TCP koneksi masuk ke port 25 (atau 465/587) di VPS. Ini adalah yang dibutuhkan DomiBox untuk menerima email.
- **Outbound (VPS → MX eksternal):** VPS mengirim email ke MX pihak ketiga. Port 25 outbound bisa diblokir oleh Tencent — tapi ini **bukan** topik yang dibahas di sini. Nanti jika DomiBox butuh mengirim email, lihat section 2.6.

### 2.2 Kebijakan default Tencent Cloud untuk port 25

Dokumen resmi Tencent "Unblocking Port 25" (terakhir update 2026-01-26) menyatakan:

> "To improve email sending on Tencent Cloud IP addresses and for security reasons, access to the external TCP port 25 from Cloud Virtual Machine (CVM) instances is blocked by default."

Ini adalah **outbound restriction**: VPS tidak bisa melakukan koneksi TCP keluar ke port 25 di internet. **Bukan** inbound restriction.

Status: **TERVERIFIKASI** — [Tencent Cloud: Unblocking Port 25](https://intl.cloud.tencent.com/document/product/213/34833), diakses 2026-11-14.

### 2.3 Apakah inbound port 25 bisa diterima?

Inbound port 25 **bukan** diatur oleh kebijakan "unblocking port 25" Tencent. Inbound diatur oleh dua mekanisme:

1. **Security Group Tencent Cloud** — lapisan infrastruktur di tingkat VPC/CVM. Aturan inbound/outbound di security group menentukan apakah koneksi yang masuk ke instance diizinkan. Default security group biasanya menutup semua port inbound kecuali yang diizinkan eksplisit. Untuk SMTP inbound, diperlukan rule inbound yang mengizinkan TCP/25 dari `0.0.0.0/0` (atau dari rangkaian IP mail provider yang dikenal, seperti Google, Microsoft, dll.).

   Sumber: [Tencent Cloud: Port and Security Group](https://intl.cloud.tencent.com/document/product/215/35536), diakses 2026-11-14.

2. **UFW (Uncomplicated Firewall) di Ubuntu** — lapisan OS. UFW aktif di VPS tetapi status detail rule tidak bisa dibaca non-interaktif (membutuhkan sudo password). Ini berarti: UFW mungkin menutup port 25 meskipun security group sudah terbuka. Status UFW saat ini: **NOT VERIFIED** — perlu pemeriksaan interaktif.

### 2.4 Perbedaan CVM vs Lighthouse

Tencent menyediakan dua produk VM yang relevan:

- **CVM (Cloud Virtual Machine):** Instans standar, ada security group lengkap. Dokumen "Unblocking Port 25" secara eksplisit menyebut CVM.
- **Lighthouse (Server Kurang Digunakan):** Produk lebih ringan. Lighthouse punya firewall rules tersendiri (API `CreateFirewallRules`). Dokumen yang ditemukan membahas konfigurasi firewall Lighthouse terpisah dari CVM. Apakah Lighthouse juga dikenakan pembatasan outbound port 25 yang sama — **TIDAK DITEMUKAN** di dokumentasi yang tersedia dengan bahasa Indonesia/Inggris yang bisa diakses. Status: **TIDAK DIKETAHUI — perlu verifikasi ke console Tencent atau support.**

Status keseluruhan inbound: **HIPOTESIS** — inbound port 25 *seharusnya* bisa diterima setelah memodifikasi security group (Lighthouse firewall) dan UFW, tapi ini belum diuji.

### 2.5 Konfigurasi yang diperlukan

Jika inbound port 25 ingin diaktifkan, berikut yang harus dikonfigurasi:

**a. Tencent Security Group / Lighthouse Firewall**

- Tencent Cloud Console → Security Management → Security Group → buat aturan inbound untuk CVM:
  - Protokol: TCP
  - Port: 25
  - Source: `0.0.0.0/0` (atau limited ke IP mail server yang dikenal)
  - Policy: Allow
- Jika menggunakan Lighthouse: konfigurasi firewall rules via console atau API `CreateFirewallRules` untuk mengizinkan inbound TCP/25.

Sumber: [Tencent Cloud: Port and Security Group](https://intl.cloud.tencent.com/document/product/215/35536), [Tencent Cloud: CreateFirewallRules (Lighthouse API)](https://www.tencentcloud.com/document/product/1103/42513), diakses 2026-11-14.

**b. UFW (Ubuntu)**

- UFW harus di-config untuk mengizinkan port 25 inbound:
  ```
  ufw allow 25/tcp
  ufw reload
  ```
- Status saat ini **NOT VERIFIED** — perlu login interaktif untuk memeriksa dan memodifikasi.

**c. DNS — MX Record**

- Di registrar domain (indo.domains) atau di Cloudflare DNS (karena nameserver domain sudah di-cloudflare), setup MX record yang menunjuk ke IP VPS:
  - MX priority 10 → `mail.sintaksis.biz.id` (atau IP langsung)
- Jika menggunakan subdomain untuk mail (mis. `mail.sintaksis.biz.id`), subdomain tersebut perlu A record ke IP VPS.
- Contoh MX record:
  ```
  sintaksis.biz.id.  IN  MX  10  mail.sintaksis.biz.id.
  mail.sintaksis.biz.id.  IN  A  <IP_VPS>
  ```

**d. Stalwart Configuration**

- Stalwart perlu di-configure untuk listen di port 25 (SMTP) dan 587 (submission). Dalam file config Stalwart (TOML/JSON), set:
  - `smtp.listener.bindAddress = "0.0.0.0"`
  - `smtp.listener.port = 25` (untuk inbound)
  - `submission.listener.port = 587` (untuk submission)
  - `submission.listener.bindAddress = "0.0.0.0"`
- Juga perlu konfigurasi TLS (lihat 2.7).

**e. TLS / ACME**

- Domain `sintaksis.biz.id` perlu certificate TLS untuk SMTP STARTTLS.
- Pendekatan: gunakan Caddy sebagai reverse proxy di depan Stalwart, atau gunakan ACME via Stalwart sendiri jika didukung.
- Stalwart mendukung ACME untuk certificate otomatis? **TIDAK DITEMUKAN** di docs — perlu verifikasi. Alternatif: Caddy yang menyediakan TLS otomatis via Let's Encrypt, lalu forward TCP ke Stalwart.
- Status: **HIPOTESIS** — butuh verifikasi apakah Stalwart mendukung ACME natively, atau apakah pendekatan Caddy lebih realistis.

**f. Monitoring**

- Log SMTP inbound (accepted/rejected RCPT TO) — tapi bagaimana cara monitoring yang spesifik di Stalwart: **TIDAK DITEMUKAN** di docs yang terindeks. Stalwart mungkin menyediakan log auditor atau metrics.
- Monitoring infrastruktur: port harus "listening", koneksi masuk harus tercatat di log.
- Rekomendasi: setup monitoring sederhana (mis. `ss -tlnp | grep 25`) dan log aggregator untuk SMTP.

---

## 3. Fallback bila Inbound Port 25 Tidak Tersedia

### 3.1 Apa yang bisa dilakukan jika Tencent tidak mengizinkan inbound 25?

Ada beberapa skenario fallback:

**Skenario A: Port 25 inbound diblokir oleh security group Tencent dan tidak bisa dibuka.**

- Solusi utama: gunakan **Cloudflare Email Routing** untuk forwarding inbound ke tempat lain, atau gunakan **provider mail lain yang menerima inbound** lalu forward ke VPS.
- Keterbatasan kritis: Cloudflare Email Routing **mengambil alih MX domain** whole — tidak bisa berjalan paralel dengan mail server yang sudah ada di domain yang sama.

**Skenario B: Inbound 25 bisa dibuka tapi butuh waktu approval.**

- Gunakan subdomain delegation sementara (lihat 3.3).

### 3.2 Cloudflare Email Routing — mekanisme dan keterbatasan

**Mekanisme:**
- Email Routing adalah layanan inbound forwarding dari Cloudflare.
- Saat diaktifkan, MX record domain diganti menjadi:
  ```
  sintaksis.biz.id.  IN  MX  10  route1.mx.cloudflare.net.
  sintaksis.biz.id.  IN  MX  20  route2.mx.cloudflare.net.
  sintaksis.biz.id.  IN  MX  30  route3.mx.cloudflare.net.
  ```
- Mail masuk ke Cloudflare, diteruskan ke destination yang di-setup (bisa ke Gmail, Outlook, atau SMTP server eksternal).

**Keterbatasan kritis:**
1. **MX record diambil alih sepenuhnya.** Domain yang sudah punya layanan mail di server sendiri (mis. Stalwart di VPS) akan TIDAK lagi menerima mail masuk setelah Email Routing diaktifkan.
2. **Tidak ada quarantine atau copy di Cloudflare** untuk mail yang tidak terc Routing — mail tanpa route di Reject di edge.
3. **Email Routing bukan mail server** — tidak ada IMAP, tidak ada SMTP submission, tidak ada penyimpanan permanen.
4. **SPF/DMARC forwarding** bisa bermasalah karena forward perubahan envelope sender dan bisa memicu DMARC fail.

Sumber: [Cloudflare: Email Routing DNS records](https://developers.cloudflare.com/email-service/configuration/domains) dan artikel pihak ketiga yang mendokumentasikan mekanisme ini, diakses 2026-11-14.

**Skenario penggunaan yang sah:**
- Domain `sintaksis.biz.id` punya mail di Stalwart. Email Routing **tidak bisa** digunakan untuk domain ini tanpa delegasi subdomain.
- Solusi: gunakan subdomain `mail.sintaksis.biz.id` yang terpisah MX recordnya (bukan apex domain). Subdomain ini bisa punya MX sendiri yang menunjuk ke Stalwart di VPS.

**Catatan:** Subdomain delegation lewat NS record atau CNAME bisa jadi sulit karena Cloudflare DNS ke domain. Verifikasi apakah subdomain bisa memiliki MX record independent di Cloudflare DNS.

### 3.3 Subdomain delegation untuk mail

Pendekatan alternatif: delegasikan subdomain `mail.sintaksis.biz.id` ke mail server VPS dengan MX record sendiri:

```
mail.sintaksis.biz.id.  IN  MX  10  mail.sintaksis.biz.id.
mail.sintaksis.biz.id.  IN  A  <IP_VPS>
```

Ini memungkinkan:
- Domain apex `sintaksis.biz.id` bisa tetap pakai MX yang lain (mis. forwarding ke Gmail, atau tidak ada MX sama sekali)
- Mail untuk alamat `@mail.sintaksis.biz.id` masuk ke VPS
- Domain utama tidak terganggu

Keterbatasan:
- Semua alamat mail harus di bawah subdomain, bukan di apex domain. Ini bisa menjadi constraint jika DomiBox ingin alamat `@sintaksis.biz.id` (bukan subdomain). Verifikasi kebutuhan produk: apakah alamat harus di apex domain atau subdomain bisa diterima?

### 3.4 Provider inbound lain

Provider inbound email yang bisa jadi alternatif (bukan Cloudflare Email Routing yang mengambil alih MX):

- **Amazon SES (incoming):** Menerima email via receiving rule, bisa forward ke endpoint HTTPS/SMTP. Tapi SES incoming bukan layanan generik "terima semua mail untuk domain" — butuh konfigurasi rules per alamat.
- **Mailgun Inbound:** Menerima mail, bisa forward via route ke webhook/SMTP.
- **Forwarding service lain:** Mis. ImprovMX, ForwardEmail — tapi hampir semuanya bekerja dengan mengubah MX atau mengarahkan ke subdomain.

Kesimpulan: Semua provider inbound forwarding yang umum mengharuskan domain untuk mengarahkan MX ke mereka, atau menggunakan subdomain dengan MX sendiri. **Tidak ada provider inbound yang bisa "mengambil sebagian traffic" tanpa mengubah MX record domain utama.**

---

## 4. Model Mailbox Sementara pada Stalwart

### 4.1 Fitur Stalwart yang relevan

Fitur-fitur di Stalwart yang relevan untuk mail sementara:

**a. Virtual mailboxes (REAL atau VIRTUAL?)**

Dokumen Stalwart yang ditemukan: [Addresses, aliases and catch-all](https://stalw.art/docs/domains/addresses) menjelaskan bahwa recipient resolution terjadi melalui domain, sub-addressing, masked addresses (Enterprise), external directory, local addresses (account/group / mailing list), catch-all, dan relaying.

**Tidak ada dokumen yang menjelaskan "virtual mailboxes" sebagai fitur terpisah** di Stalwart — email di-resolve ke account, group, atau mailing list yang nyata.

Status: **TIDAK DITEMUKAN** — Stalwart mungkin tidak memiliki konsep "virtual mailbox" yang terpisah dari akun fisik. Perlu verifikasi ke dokumentasi lengkap dan/atau kode sumber Stalwart.

**b. Email templates / disposable mailboxes (Enterprise only)**

Stalwart Enterprise memiliki fitur **Masked Email**:
> "Masked emails are disposable, per-service email addresses that route to a user's real inbox. Instead of handing out a primary address to every newsletter, shop, or forum, a user can generate a unique masked address for each service."

Sumber: [Stalwart v0.16 Blog: Masked Emails](https://stalw.art/blog/stalwart-0-16) dan [Masked email docs](https://stalw.art/docs/email/management/masked-email), diakses 2026-11-14.

Fitur ini memungkinkan:
- User membuat alamat sementara (masked) yang di-forward ke akun asli
- Setiap masked address bisa di-disable secara individual
- Masked address terikat ke satu user account

**Namun:** masked email adalah fitur **Enterprise edition** (berbayar). Untuk Community edition, fitur ini TIDAK tersedia.

**c. Alias**

Setiap account bisa punya banyak alias (EmailAlias). Alias adalah address yang menerima mail dan di-deliver ke account yang sama. Alias bisa dinonaktifkan tanpa dihapus. Alias adalah **exact address**, bukan pattern.

Sumber: [Addresses, aliases and catch-all](https://stalw.art/docs/domains/addresses), diakses 2026-11-14.

**d. Catch-all address**

Domain bisa memiliki `catchAllAddress` — satu alamat yang menerima semua mail untuk unknown recipients di domain tersebut. Catch-all meningkatkan volum spam karena menerima semua alamat yang dicoba.

Sumber: [Addresses, aliases and catch-all](https://stalw.art/docs/domains/addresses), diakses 2026-11-14.

**e. Quota dan retention (DataRetention)**

Stalwart memiliki objek DataRetention dengan setting:
- `expungeTrashAfter`: Duration (default 30 hari) — berapa lama pesan di Trash/Junk sebelum auto-expunge
- `expungeSubmissionsAfter`: Duration (default 5 hari) untuk sent mail
- `archiveDeletedItemsFor`: Duration (Enterprise) — berapa lama keep deleted items di archive sebelum permanently delete
- `expungeSchedule`: Cron schedule untuk auto-expunge (default pukul 0)

Sumber: [DataRetention docs](https://stalw.art/docs/ref/object/data-retention), diakses 2026-11-14.

**f. JMAP API untuk manajemen**

Stalwart mengekspos JMAP API untuk:
- Membuat/menghapus account
- Mengelola aliases
- Mengelola mailing lists
- Mengelola quota per account
- Mengelola domain

Sumber: [JMAP capabilities](https://stalw.art/docs/http/jmap/capabilities), [Account object](https://stalw.art/docs/ref/object/account), diakses 2026-11-14.

**g. JMAP Push / WebSocket untuk realtime**

Stalwart mendukung:
- `urn:ietf:params:jmap:websocket` — JMAP over WebSocket
- `urn:ietf:params:jmap:emailpush` — push notification untuk konten email
- `urn:ietf:params:jmap:webpush-vapid` — VAPID untuk push subscription

Sumber: [JMAP capabilities](https://stalw.art/docs/http/jmap/capabilities), diakses 2026-11-14.

**h. IMAP**

Stalwart implements [IMAP4rev2](https://stalw.art/docs/email/settings/imap) untuk sinkronisasi mailbox dengan klien desktop/mobile.

### 4.2 4 Opsi Model Mailbox

#### Opsi A: Physical account per alamat

Setiap alamat sementara (mis. `temp123@domain.com`) dibuat sebagai Stalwart Account object terpisah.

| Dimensi | Keterangan |
| --- | --- |
| **Security isolation** | Tinggi — setiap account memiliki storage, quota, dan permissions terpisah. |
| **Overhead pembuatan** | Tinggi — setiap account butuh provisioning (JMAP API call, quota config, password/reset). |
| **Retensi** | Bisa diatur via DataRetention per account, tapi perlu konfigurasi otomatis untuk auto-delete. |
| **Validasi recipient** | Alamat benar-benar ada di Stalwart sebagai account. |
| **Enforcement expiry** | TIDAK ada fitur native TTL per account. Butuh custom daemon eksternal atau JMAP API untuk menghapus account setelah expiry. |
| **Perilaku delete** | Menghapus account → archives deleted items jika di-configure, lalu permanent delete sesuai schedule. |
| **Konversi temp → permanen** | Straightforward — ubah account menjadi permanen (ubah password, extend quota). |
| **Race condition** | Pesan bisa datang saat account sedang dihapus — Stalwart akan reject RCPT TO jika account sudah dihapus. |
| **Storage overhead** | Setiap account punya storage terpisah — overhead signifikan jika banyak alamat sementara. |
| **Dukungan API** | JMAP API lengkap untuk account CRUD. |

**Status rekomendasi:** Bisa dipakai tapi perlu custom automation. Tidak ada fitur TTL bawaan.

#### Opsi B: Alias dari satu account

Satu account "master" (mis. `temporary@domain.com`) dengan banyak alias sementara. Setiap alias diberikan ke user.

| Dimensi | Keterangan |
| --- | --- |
| **Security isolation** | Rendah — semua alias masuk ke satu account, satu storage. |
| **Overhead pembuatan** | Rendah — cukup create alias via JMAP API. |
| **Retensi** | Retensi diatur untuk satu account, gabungan semua alias. |
| **Validasi recipient** | Alias benar-benar ada di Stalwart. |
| **Enforcement expiry** | Alias bisa dinonaktifkan via JMAP API (disable tanpa delete). Butuh custom logic untuk auto-disable setelah expiry. |
| **Perilaku delete** | Nonaktifkan alias → mail ditolak. |
| **Konversi temp → permanen** | Alias bisa di-"promote" dengan creating account baru dan memindahkan mail (bisa via JMAP copy atau export/import). |
| **Race condition** | Pesan yang datang setelah alias nonaktif → reject. |
| **Storage overhead** | Rendah — satu storage untuk semua alias. |
| **Dukungan API** | JMAP API untuk alias CRUD. |

**Status rekomendasi:** Paling ringan dalam hal resource, tapi tidak ada isolasi per-alias. Cocok untuk skenario di mana semua mail sementara milik satu user dan dipisah hanya untuk tracking/label.

#### Opsi C: Virtual mailbox (jika ada di Stalwart)

Status: **TIDAK TERVERIFIKASI** — fitur ini tidak ditemukan di dokumentasi Stalwart yang ada. Jika "virtual mailbox" diartikan sebagai "address yang tidak punya account fisik tapi langsung di-forward ke destinasi lain", ini mungkin diimplementasikan lewat catch-all atau mailing list dengan forwarding. Namun ini bukan fitur "virtual mailbox" yang first-class.

Jika Stalwart benar-benar tidak punya fitur ini, opsi C tidak terpakai.

#### Opsi D: Shared mailbox + routing ketat

Menggunakan mailing list atau group sebagai shared mailbox. Mail datang ke shared address, di-forward/di-distribusikan ke anggota.

| Dimensi | Keterangan |
| --- | --- |
| **Security isolation** | Sedang — shared mailbox accessible by multiple members. |
| **Overhead pembuatan** | Sedang — perlu create mailing list/group. |
| **Retensi** | Retensi diatur untuk shared mailbox. |
| **Validasi recipient** | Alamat mailing list ada. |
| **Enforcement expiry** | Bisa di-set expiry di level mailing list, tapi butuh logic custom. |
| **Perilaku delete** | Delete mailing list → mail ditolak. |
| **Konversi temp → permanen** | Pending — perlu migrasi ke account permanen. |
| **Race condition** | Members join/leave during delivery — Stalwart expand recipients at RCPT TO time. |
| **Storage overhead** | Mail disimpan di shared mailbox — overhead per-member rendah tapi akses control perlu diatur. |
| **Dukungan API** | MailingList object di JMAP API. |

**Status rekomendasi:** Kurang cocok untuk mail sementara per-user karena focused pada distribusi ke banyak penerima, bukan mailbox per-user.

### 4.3 Rekomendasi + Confidence

| Model | Confidence | Alasan |
| --- | --- | --- |
| **Opsi B (Alias dari satu account)** | Tinggi untuk MVP | Paling simpel, resource efisien, ada di Community edition, API lengkap. Tapi tidak ada fitur auto-expiry native — butuh custom daemon/JMAP client untuk nonaktifkan alias setelah TTL. |
| **Opsi A (Physical account per alamat) + custom automation** | Sedang | Lebih bersih secara isolasi, tapi overhead storage tinggi untuk banyak alamat dan butuh custom automation untuk expiry. |
| **Opsi C (Virtual mailbox native)** | Rendah | Fitur tidak ditemukan di docs — perlu verifikasi langsung ke kode atau support Stalwart. |
| **Opsi D (Shared mailbox)** | Rendah untuk sementara | Kurang cocok untuk mail sementara per-user. |

**Rekomendasi utama untuk MVP:** Gunakan **Opsi B (Alias dari satu account)** dengan custom daemon/integrasi yang:
1. Membuat alias via JMAP API saat user meminta alamat sementara.
2. Menyimpan metadata (expiry, owner) di database eksternal (bukan di Stalwart).
3. Mematikan alias (disable) saat expiry habis, atau hapus jika tidak butuh lagi.
4. Mengirim notifikasi ke user jika ada mail masuk selama periode sementara.

**Confidence: 0.7 (tinggi untuk kemampuan implementasi, sedang untuk fitur native expiry karena harus custom).**

**PoC yang wajib dijalankan:**

1. Buktikan bahwa JMAP API bisa membuat dan menonaktifkan alias via API call (dokumentasi: [Account object](https://stalw.art/docs/ref/object/account)).
2. Buktikan bahwa nonaktifkan alias menyebabkan mail ditolak (RCPT TO reject) — tes dengan mengirim email ke alias yang dinonaktifkan.
3. Buktikan bahwa mail yang datang sebelum alias nonaktif tetap di-deliver ke account — dan bisa di-retry/di-baca via IMAP/JMAP.
4. Evaluasi dampak storage jika alias digunakan skala besar — apakah growth signifikan?
5. Jika menggunakan Opsi A (physical account), buktikan bahwa delete account tidak secara instan menghapus semua mail (karena archiveDeletedItemsFor mungkin memperlambat deletion).
6. Verifikasi berapa lama deletion cycle — apakah mail benar-benar hilang setelah account dihapus, atau ada jendela di mana mail bisa masuk ke account yang sudah dihapus (race condition).

---

## 5. Model Mailbox Permanen

### 5.1 Kebutuhan inbound-only MVP vs outbound email

Terdapat dua level kebutuhan:

**Level 1: Inbound-only (MVP)**
- Domain menerima email masuk via SMTP inbound (port 25/587).
- Mail disimpan di mailbox Stalwart.
- User bisa membaca via IMAP/JMAP.
- User bisa mengirim email via SMTP submission (port 587/465) jika butuh kirim — tapi ini opsional untuk MVP inbound-only.
- Tidak perlu MX record ke domain jika hanya inbound, tapi MX record tetap dibutuhkan untuk menerima mail.

**Level 2: Full outbound (nanti)**
- VPS bisa mengirim email via SMTP (port 587 ke MX eksternal, atau port 25 ke MX jika tidak diblokir).
- Domain punya SPF, DKIM, DMARC yang di-publish untuk domain sendiri.
- Mail yang dikirim melewati outgoing mail server Stalwart.
- Butuh outbound route, DKIM keys, dan kemungkinan relay rules.

### 5.2 Dukungan Stalwart untuk mailbox permanen

**IMAP:**
- Stalwart implements IMAP4rev2.
- Account punya special-use folders (Inbox, Drafts, Sent, Trash, Junk, Archive) yang otomatis dibuat saat account dibuat.
- Sumber: [IMAP and POP3 docs](https://stalw.art/docs/email/settings/imap), diakses 2026-11-14.

**SMTP Submission (587/465):**
- Stalwart punya SMTP submission listener yang menerima authenticated submission.
- Autentikasi: plaintext, CRAM-MD5, SCRAM-SHA-256, dll.
- Sumber: [SMTP authentication docs](https://stalw.art/docs/mta/inbound/auth), diakses 2026-11-14.

**Webmail:**
- Stalwart punya WebUI yang menyediakan webmail interface.
- Sumber: [WebUI docs](https://stalw.art/docs/management/webui/), diakses 2026-11-14.

**Penyimpanan:**
- Mail disimpan di storage backend (default: file-based atau bisa PostgreSQL? — **TIDAK DITEMUKAN** di docs terkait storage backend alternatif. DataRetention docs menyebut "data store" dan "blob store" tapi tidak spesifik backend).
- Sumber: [DataRetention docs](https://stalw.art/docs/ref/object/data-retention), diakses 2026-11-14.

**Kompatibilitas klien eksternal:**
- Klien IMAP apa pun (Thunderbird, Apple Mail, mobile) bisa connect ke Stalwart.
- Klien JMAP apa pun yang support RFC 8620/8621 bisa connect.
- Sumber: [JMAP capabilities](https://stalw.art/docs/http/jmap/capabilities), diakses 2026-11-14.

### 5.3 Kebutuhan outbound email — masa depan

Jika DomiBox nanti butuh mengirim email:
- VPS butuh outbound port 25 (mis. ke MX eksternal) atau port 587 (submission ke relay).
- Tencent memblokir outbound 25 default — perlu unblock via console.
- Domain butuh SPF record yang publikasikan di DNS.
- DKIM keys harus di-generate di Stalwart dan dipublish di DNS.
- DMARC policy ditentukan di DNS.

Sumber: [Tencent Unblocking Port 25](https://intl.cloud.tencent.com/document/product/213/34833), diakses 2026-11-14.

**Untuk MVP inbound-only:** outbound email TIDAK wajib. Domain bisa hanya receive. Tapi MX record tetap dibutuhkan di DNS.

---

## 6. Strategi Hapus Mailbox

### 6.1 Warning eksplisit: "Hanya menyembunyikan alamat" tidak boleh membiarkan pesan masuk selamanya

Pendekatan yang berbahaya: "nonaktifkan alamat tapi tidak hapus account" → akun tetap ada, email tetap masuk, storage terus bertambah. Ini TIDAK diterima.

Pendekatan yang benar:
1. **Nonaktifkan alias/address** → mail ditolak di RCPT TO stage.
2. **Hapus account** → mail yang sudah masuk di-expunge sesuai retention, mail baru ditolak.
3. **Pastikan ada retention policy** yang membersihkan mail yang sudah tidak relevan.

### 6.2 Recipient validation dan perilaku reject

Stalwart melakukan recipient validation di RCPT TO stage SMTP:
- Jika recipient not found (account, alias, catch-all, group, mailing list) → reject dengan SMTP error (550/551/553).
- Ini berarti jika account/alias dihapus, mail yang datang setelahnya langsung ditolak — tidak masuk ke mailbox.

Sumber: [RCPT TO stage docs](https://stalw.art/docs/mta/inbound/rcpt), diakses 2026-11-14.

### 6.3 Retensi dan penghapusan account

**DataRetention config:**
- `expungeTrashAfter`: pesan di Trash/Junk di-expunge setelah 30 hari (default).
- `expungeSubmissionsAfter`: sent mail di-expunge setelah 5 hari.
- `archiveDeletedItemsFor`: (Enterprise) berapa lama keep deleted items di archive sebelum permanent delete. Jika null, langsung permanently delete.
- `expungeSchedule`: kapan cron dijalankan (default pukul 0).

**Penghapusan account:**
- Hapus account via JMAP API → account dihapus dari directory.
- Mail yang sudah ada: tetap ada sampai expunge schedule menjalankannya.
- Mail baru: ditolak karena account tidak ada.

**State reconciliation:**
- Jika ada mail yang sedang dalam transit (SMTP transfer sedang berlangsung) saat account dihapus → outcome tergantung: mungkin mail selesai transfer tapi kemudian di-expunge, atau mungkin rejected di RCPT TO (jika penerima sudah invalid saat RCPT TO dikirim).
- Race condition: account dihapus di antara waktu RCPT TO dan waktu message data transfer — Stalwart mungkin sudah accepted RCPT TO tapi kemudian reject saat data transfer? **TIDAK DITEMUKAN** di docs. Ini perlu verifikasi di PoC.

**Pesan yang telat (late-arriving mail):**
- Mail yang dikirim ke alamat sementara yang sudah kedaluwarsa tapi yang kirim belum tahu → mail reject di SMTP.
- Tidak ada queue atau deferred delivery untuk mail yang ditolak.
- Mail yang sudah diterima sebelum expiry habis: tetap ada di mailbox sampai di-expunge sesuai retention.

### 6.4 State machine lifecycle

Disarankan state machine untuk alamat sementara:

1. **PENDING** — alamat dibuat, belum aktif (alias nonaktif).
2. **ACTIVE** — alias aktif, mail masuk.
3. **EXPIRING** — countdown expiry, user diberitahu.
4. **EXPIRED** — alias nonaktifkan (disabled), mail masuk ditolak.
5. **DELETED** — account/alias dihapus, mail sudah expunge.

Transisi state ini harus di-manage oleh custom integration, bukan oleh Stalwart native.

---

## 7. JMAP vs IMAP untuk Integrasi Aplikasi

### 7.1 JMAP (JSON Meta Application Protocol)

**Keunggulan untuk aplikasi DomiBox:**
- API JSON-based, lebih mudah diintegrasikan dengan aplikasi web/modern.
- Satu endpoint (`/jmap`) untuk semua operasi: mailbox, message, draft, identities, contacts, calendars.
- Push via WebSocket atau EmailPush (push notification ke client).
- Sync cepat: changes API (`/changes`) untuk sync incremental.
- Support untuk CRUD account, aliases, mailing lists via `urn:stalwart:jmap` extension — ini adalah **configuration and management API** yang memungkinkan aplikasi untuk manage Stalwart configuration via JMAP.
- Sumber: [JMAP capabilities](https://stalw.art/docs/http/jmap/capabilities), [HTTP API overview](https://stalw.art/docs/development/api), diakses 2026-11-14.

**Polling vs realtime:**
- Polling: client bisa polling `/jmap/changes` secara berkala untuk cek mail baru.
- Realtime: JMAP push subscription (EmailPush) atau WebSocket bisa mengirim notifikasi realtime saat mail baru masuk.
- Sumber: [JMAP Push docs](https://stalw.art/docs/http/jmap/push), diakses 2026-11-14.

### 7.2 IMAP

**Keunggulan:**
- Standard protocol yang didukung luas oleh klien email (desktop/mobile).
- Sync state full: flags, folders, sequence numbers.
- IDLE command untuk realtime notification (server push saat mail baru).

**Keterbatasan untuk aplikasi:**
- Protocol lebih berat daripada JMAP (binary protocol vs JSON).
- Tidak ada API untuk manajemen account/configurasi — hanya mail access.
- IDLE realtime tapi perlu persistent connection.

### 7.3 Rekomendasi untuk DomiBox

**Untuk integrasi aplikasi (backend DomiBox → Stalwart):**
- Gunakan **JMAP** karena:
  - Satu API untuk semua operasi (mail + config).
  - Push support untuk realtime notification.
  - Lebih mudah di-integrasikan dengan aplikasi web (JSON + HTTP).
  - Ada extension `urn:stalwart:jmap` untuk management API.

**Untuk access klien eksternal (user email client):**
- IMAP tetap dibutuhkan karena klien email umum (Thunderbird, Outlook, mobile) mengandalkan IMAP, bukan JMAP.
- Stalwart menyediakan IMAP, jadi ini tidak menjadi masalah.

**Kesimpulan:** DomiBox backend butuh JMAP untuk integration dan management. Stalwart juga menyediakan IMAP untuk klien user. Ini adalah kombinasi yang masuk akal.

---

## 8. Matriks Port & Jaringan

### 8.1 Port yang Relevan untuk DomiBox Mail

| Port | Protokol | Bind Address | Publik/Privat | Keperluan | Catatan Security Group | Status Saat Ini | Konflik dengan rustfs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **22** | SSH | 0.0.0.0 | Publik | Manajemen VPS | Diperbolehkan (sudah terbuka) | TERVERIFIKASI: listening | Tidak ada |
| **25** | SMTP (inbound) | 0.0.0.0 (disarankan) | Publik | Menerima email masuk | Diperlukan inbound rule untuk TCP/25 dari 0.0.0.0/0 | TIDAK LISTENING — perlu Stalwart + firewall | Tidak ada (rustfs 9000-9001) |
| **465** | SMTPS (submission TLS) | 0.0.0.0 (opsional) | Publik | Submission email terenkripsi | Sama seperti 587 | TIDAK LISTENING | Tidak ada |
| **587** | Submission (STARTTLS) | 0.0.0.0 (disarankan) | Publik | Email submission dari klien | Diperlukan inbound rule | TIDAK LISTENING | Tidak ada |
| **80** | HTTP (ACME challenge) | 127.0.0.1 atau 0.0.0.0 | Publik | HTTP-01 challenge untuk Let's Encrypt | Diperlukan untuk ACME jika tidak pakai DNS-01 | TIDAK LISTENING | Tidak ada |
| **443** | HTTPS | 0.0.0.0 (jika pakai Caddy) | Publik | Webmail / JMAP API + TLS | Diperlukan untuk WebUI/JMAP/TLS | TIDAK LISTENING | Tidak ada |
| **993** | IMAPS (IMAP TLS) | 0.0.0.0 (opsional) | Publik | IMAP over TLS | Diperlukan inbound rule | TIDAK LISTENING | Tidak ada |
| **143** | IMAP (STARTTLS) | 0.0.0.0 (opsional) | Publik | IMAP dengan STARTTLS | Diperlukan inbound rule | TIDAK LISTENING | Tidak ada |
| **8080** | HTTP alternatif | 127.0.0.1 (jika Caddy di-front) | Privat | HTTP backend sebelum reverse proxy | Tidak perlu publik | Tidak ada | Tidak ada |
| **9000-9001** | rustfs object storage | 127.0.0.1 | Privat | Object storage (existing container) | **TIDAK DIUBAH — hanya untuk rustfs, bukan mail** | TERVERIFIKASI: sudah listening untuk rustfs | — |
| **53** | DNS (systemd-resolved) | 127.0.0.53 | Privat | DNS resolver lokal | Tidak bisa diubah | TERVERIFIKASI: systemd-resolved | Tidak ada |

### 8.2 Port yang TIDAK perlu dibuka di publik (untuk MVP inbound-only)

- **465, 587, 993, 143:** Tidak perlu dibuka jika hanya inbound-only dari server mail eksternal. Tapi untuk submission dari klien (user kirim email), perlu dibuka 587 atau 465.
- **8080:** Hanya untuk debug/internal, tidak perlu publik.

### 8.3 Konflik potensial

- **rustfs container (9000-9001)** tidak konflik dengan port mail jika Stalwart listen di port yang berbeda. Konflik hanya mungkin jika Stalwart salah konfigurasi bind ke alamat yang sama atau port yang tumpang tindih.
- **UFW** aktif tapi tidak bisa diverifikasi tanpa sudo — berpotensi memblokir port yang terbuka di security group.
- **Tidak ada reverse proxy** saat ini — ini baik untuk DomiBox karena VPS bisa langsung expose mail ports. Jika nanti butuh HTTPS, bisa tambah Caddy.

---

## 9. Footprint Sumber Daya

### 9.1 Konfigurasi VPS yang Tersedia

Dari inspeksi VPS (2026-11-14):

- **2 vCPU AMD EPYC 7K62** (na>
---

## 1. Ringkasan Eksekutif

Temuan-temuan berikut adalah ringkasan tingkat tinggi. Rincian dan sumber ada di section yang bersangkutan dengan status TERVERIFIKASI / HIPOTESIS.

1. **Port 25 inbound (SMTP) secara prinsip bisa diterima di VPS Tencent,** tetapi perlu dua lapisan konfigurasi terpisah: Security Group Tencent (lapisan infrastruktur) dan UFW (lapisan OS). Dokumen Tencent tentang "Unblocking Port 25" secara eksplisit membahas **outbound** dari CVM ke SMTP eksternal, **bukan inbound**. Status: **TERVERIFIKASI** (sumber Tencent Cloud, 2026-01-26).

2. **Outbound port 25 dari VPS diblokir default.** Jika DomiBox nanti butuh mengirim email keluar (outbound SMTP ke MX lain), VPS harus mengajukan "Unblock Port 25" via console Tencent. Hanya CVM berbayar (prepaid annual/monthly) yang didukung; pay-as-you-go tidak didukung. Status: **TERVERIFIKASI** (sumber Tencent Cloud, 2026-01-26).

3. **Tidak ada reverse proxy atau listener SMTP yang aktif** di VPS saat inspeksi. Port 25, 465, 587, 80, 443, 993 TIDAK terisi. Ini berarti Stalwart yang di-deploy pertama kali bisa mengambil port tersebut tanpa bentrok dengan layanan lain — selama security group / UFW diatur. Status: **TERVERIFIKASI** (inspeksi VPS, 2026-11-14).

4. **Container `rustfs` (127.0.0.1:9000-9001) tidak bentrok** dengan port mail. Konflik yang mungkin terjadi hanya jika Stalwart di-configure salah bind ke 0.0.0.0 dengan port yang tumpang tindih, atau jika reverse proxy Caddy di-configure bind ke alamat yang sama. Status: **TERVERIFIKASI** (inspeksi VPS, 2026-11-14).

5. **Stalwart v1.0.3 sudah ada fitur `masked email` (Enterprise)** untuk alamat sementara/disposable yang di-forward ke akun asli. Ini adalah fitur yang paling relevan untuk model mailbox sementara. Fitur community edition hanya memiliki alias dan catch-all. Status: **TERVERIFIKASI** (dokumen Stalwart Labs, 2026-11-14).

6. **Cloudflare Email Routing mengambil alih MX domain secara penuh.** Mengaktifkan Email Routing berarti mengganti MX record domain ke `route1/2/3.mx.cloudflare.net` — **tidak bisa berjalan paralel** dengan mail server yang sudah ada di domain yang sama. Solusi: delegasi ke subdomain (`mail.domain.com`) atau gunakan provider lain untuk forwarding inbound yang tidak mengambil alih MX. Status: **TERVERIFIKASI** (dokumen Cloudflare dan artikel pihak ketiga yang menyebut mekanisme ini, 2026-11-14).

7. **Stalwart memiliki API JMAP penuh** untuk manajemen akun, alias, mailing list, quota, dan data retention. Tidak ada dokumentasi resmi tentang "auto-delete alamat otomatis berdasarkan TTL" untuk mailbox sementara — fitur ini TIDAK DITEMUKAN di docs Stalwart. Pendekatan alternatif: (a) memakai siklus hidup akun + permissions, (b) memakai JMAP API untuk menghapus akun saat expiry habis, (c) custom daemon eksternal. Status: **TIDAK TERVERIFIKASI — perlu verifikasi langsung ke docs Stalward + test di PoC.**

8. **Footprint sumber daya Stalwart + Postgres di VPS 2 vCPU / ~3.6 GB RAM** bukan angka yang dipublikasikan resmi oleh Stalwart Labs. Tidak ada benchmark publik yang bisa dirujuk. PoC benchmark WAJIB dijalankan sebelum keputusan produksi. Status: **TIDAK TERVERIFIKASI — perlu PoC benchmark.**

---

## 2. SMTP Ingress di Tencent Cloud

### 2.1 Konteks: inbound vs outbound

Penting untuk membedakan dua arah traffic SMTP:

- **Inbound (MX → VPS):** Mail provider eksternal mengirim TCP koneksi masuk ke port 25 (atau 465/587) di VPS. Ini adalah yang dibutuhkan DomiBox untuk menerima email.
- **Outbound (VPS → MX eksternal):** VPS mengirim email ke MX pihak ketiga. Port 25 outbound bisa diblokir oleh Tencent — tapi ini **bukan** topik yang dibahas di sini. Nanti jika DomiBox butuh mengirim email, lihat section 2.6.

### 2.2 Kebijakan default Tencent Cloud untuk port 25

Dokumen resmi Tencent "Unblocking Port 25" (terakhir update 2026-01-26) menyatakan:

> "To improve email sending on Tencent Cloud IP addresses and for security reasons, access to the external TCP port 25 from Cloud Virtual Machine (CVM) instances is blocked by default."

Ini adalah **outbound restriction**: VPS tidak bisa melakukan koneksi TCP keluar ke port 25 di internet. **Bukan** inbound restriction.

Status: **TERVERIFIKASI** — [Tencent Cloud: Unblocking Port 25](https://intl.cloud.tencent.com/document/product/213/34833), diakses 2026-11-14.

### 2.3 Apakah inbound port 25 bisa diterima?

Inbound port 25 **bukan** diatur oleh kebijakan "unblocking port 25" Tencent. Inbound diatur oleh dua mekanisme:

1. **Security Group Tencent Cloud** — lapisan infrastruktur di tingkat VPC/CVM. Aturan inbound/outbound di security group menentukan apakah koneksi yang masuk ke instance diizinkan. Default security group biasanya menutup semua port inbound kecuali yang diizinkan eksplisit. Untuk SMTP inbound, diperlukan rule inbound yang mengizinkan TCP/25 dari `0.0.0.0/0` (atau dari rangkaian IP mail provider yang dikenal, seperti Google, Microsoft, dll.).

   Sumber: [Tencent Cloud: Port and Security Group](https://intl.cloud.tencent.com/document/product/215/35536), diakses 2026-11-14.

2. **UFW (Un complicated Firewall) di Ubuntu** — lapisan OS. UFW aktif di VPS tetapi status detail rule tidak bisa dibaca non-interaktif (membutuhkan sudo password). Ini berarti: UFW mungkin menutup port 25 meskipun security group sudah terbuka. Status UFW saat ini: **NOT VERIFIED** — perlu pemeriksaan interaktif.

### 2.4 Perbedaan CVM vs Lighthouse

Tencent menyediakan dua produk VM yang relevan:

- **CVM (Cloud Virtual Machine):** Instans standar, ada security group lengkap. Dokumen "Unblocking Port 25" secara eksplisit menyebut CVM.
- **Lighthouse (Server Kurang Digunakan):** Produk lebih ringan. Lighthouse punya firewall rules tersendiri (API `CreateFirewallRules`). Dokumen yang ditemukan membahas konfigurasi firewall Lighthouse terpisah dari CVM. Apakah Lighthouse juga dikenakan pembatasan outbound port 25 yang sama — **TIDAK DITEMUKAN** di dokumentasi yang tersedia dengan bahasa Indonesia/Inggris yang bisa diakses. Status: **TIDAK DIKETAHUI — perlu verifikasi ke console Tencent atau support.**

Status keseluruhan inbound: **HIPOTESIS** — inbound port 25 *seharusnya* bisa diterima setelah memodifikasi security group (Lighthouse firewall) dan UFW, tapi ini belum diuji.

### 2.5 Konfigurasi yang diperlukan

Jika inbound port 25 ingin diaktifkan, berikut yang harus dikonfigurasi:

**a. Tencent Security Group / Lighthouse Firewall**

- Tencent Cloud Console → Security Management → Security Group → buat aturan inbound untuk CVM:
  - Protokol: TCP
  - Port: 25
  - Source: `0.0.0.0/0` (atau limited ke IP mail server yang dikenal)
  - Policy: Allow
- Jika menggunakan Lighthouse: konfigurasi firewall rules via console atau API `CreateFirewallRules` untuk mengizinkan inbound TCP/25.

Sumber: [Tencent Cloud: Port and Security Group](https://intl.cloud.tencent.com/document/product/215/35536), [Tencent Cloud: CreateFirewallRules (Lighthouse API)](https://www.tencentcloud.com/document/product/1103/42513), diakses 2026-11-14.

**b. UFW (Ubuntu)**

- UFW harus di-config untuk mengizinkan port 25 inbound:
  ```
  ufw allow 25/tcp
  ufw reload
  ```
- Status saat ini **NOT VERIFIED** — perlu login interaktif untuk memeriksa dan memodifikasi.

**c. DNS — MX Record**

- Di registrar domain (indo.domains) atau di Cloudflare DNS (karena nameserver domain sudah di-cloudflare), setup MX record yang menunjuk ke IP VPS:
  - MX priority 10 → `mail.sintaksis.biz.id` (atau IP langsung)
- Jika menggunakan subdomain untuk mail (mis. `mail.sintaksis.biz.id`), subdomain tersebut perlu A record ke IP VPS.
- Contoh MX record:
  ```
  sintaksis.biz.id.  IN  MX  10  mail.sintaksis.biz.id.
  mail.sintaksis.biz.id.  IN  A  <IP_VPS>
  ```

**d. Stalwart Configuration**

- Stalwart perlu di-configure untuk listen di port 25 (SMTP) dan 587 (submission). Dalam file config Stalwart (TOML/JSON), set:
  - `smtp.listener.bindAddress = "0.0.0.0"`
  - `smtp.listener.port = 25` (untuk inbound)
  - `submission.listener.port = 587` (untuk submission)
  - `submission.listener.bindAddress = "0.0.0.0"`
- Juga perlu konfigurasi TLS (lihat 2.7).

**e. TLS / ACME**

- Domain `sintaksis.biz.id` perlu certificate TLS untuk SMTP STARTTLS.
- Pendekatan: gunakan Caddy sebagai reverse proxy di depan Stalwart, atau gunakan ACME via Stalwart sendiri jika didukung.
- Stalwart mendukung ACME untuk certificate otomatis? **TIDAK DITEMUKAN** di docs — perlu verifikasi. Alternatif: Caddy yang menyediakan TLS otomatis via Let's Encrypt, lalu forward TCP ke Stalwart.
- Status: **HIPOTESIS** — butuh verifikasi apakah Stalwart mendukung ACME natively, atau apakah pendekatan Caddy lebih realistis.

**f. Monitoring**

- Log SMTP inbound (accepted/rejected RCPT TO) — tapi bagaimana cara monitoring yang spesifik di Stalwart: **TIDAK DITEMUKAN** di docs yang terindeks. Stalwart mungkin menyediakan log auditor atau metrics.
- Monitoring infrastruktur: port harus "listening", koneksi masuk harus tercatat di log.
- Rekomendasi: setup monitoring sederhana (mis. `ss -tlnp | grep 25`) dan log aggregator untuk SMTP.

---

## 3. Fallback bila Inbound Port 25 Tidak Tersedia

### 3.1 Apa yang bisa dilakukan jika Tencent tidak mengizinkan inbound 25?

Ada beberapa skenario fallback:

**Skenario A: Port 25 inbound diblokir oleh security group Tencent dan tidak bisa dibuka.**

- Solusi utama: gunakan **Cloudflare Email Routing** untuk forwarding inbound ke tempat lain, atau gunakan **provider mail lain yang menerima inbound** lalu forward ke VPS.
- Keterbatasan kritis: Cloudflare Email Routing **mengambil alih MX domain** whole — tidak bisa berjalan paralel dengan mail server yang sudah ada di domain yang sama.

**Skenario B: Inbound 25 bisa dibuka tapi butuh waktu approval.**

- Gunakan subdomain delegation sementara (lihat 3.3).

### 3.2 Cloudflare Email Routing — mekanisme dan keterbatasan

**Mekanisme:**
- Email Routing adalah layanan inbound forwarding dari Cloudflare.
- Saat diaktifkan, MX record domain diganti menjadi:
  ```
  sintaksis.biz.id.  IN  MX  10  route1.mx.cloudflare.net.
  sintaksis.biz.id.  IN  MX  20  route2.mx.cloudflare.net.
  sintaksis.biz.id.  IN  MX  30  route3.mx.cloudflare.net.
  ```
- Mail masuk ke Cloudflare, diteruskan ke destination yang di-setup (bisa ke Gmail, Outlook, atau SMTP server eksternal).

**Keterbatasan kritis:**
1. **MX record diambil alih sepenuhnya.** Domain yang sudah punya layanan mail di server sendiri (mis. Stalwart di VPS) akan TIDAK lagi menerima mail masuk setelah Email Routing diaktifkan.
2. **Tidak ada quarantine atau copy di Cloudflare** untuk mail yang tidak terc Routing — mail tanpa route di Reject di edge.
3. **Email Routing bukan mail server** — tidak ada IMAP, tidak ada SMTP submission, tidak ada penyimpanan permanen.
4. **SPF/DMARC forwarding** bisa bermasalah karena forward perubahan envelope sender dan bisa memicu DMARC fail.

Sumber: [Cloudflare: Email Routing DNS records](https://developers.cloudflare.com/email-service/configuration/domains) dan artikel pihak ketiga yang mendokumentasikan mekanisme ini, diakses 2026-11-14.

**Skenario penggunaan yang sah:**
- Domain `sintaksis.biz.id` punya mail di Stalwant. Email Routing **tidak bisa** digunakan untuk domain ini tanpa delegasi subdomain.
- Solusi: gunakan subdomain `mail.sintaksis.biz.id` yang terpisah MX recordnya (bukan apex domain). Subdomain ini bisa punya MX sendiri yang menunjuk ke Stalwart di VPS.

**Catatan:** Subdomain delegation lewat NS record atau CNAME bisa jadi sulit karena Cloudflare DNS ke domain. Verifikasi apakah subdomain bisa memiliki MX record independent di Cloudflare DNS.

### 3.3 Subdomain delegation untuk mail

Pendekatan alternatif: delegasikan subdomain `mail.sintaksis.biz.id` ke mail server VPS dengan MX record sendiri:

```
mail.sintaksis.biz.id.  IN  MX  10  mail.sintaksis.biz.id.
mail.sintaksis.biz.id.  IN  A  <IP_VPS>
```

Ini memungkinkan:
- Domain apex `sintaksis.biz.id` bisa tetap pakai MX yang lain (mis. forwarding ke Gmail, atau tidak ada MX sama sekali)
- Mail untuk alamat `@mail.sintaksis.biz.id` masuk ke VPS
- Domain utama tidak terganggu

Keterbatasan:
- Semua alamat mail harus di bawah subdomain, bukan di apex domain. Ini bisa menjadi constraint jika DomiBox ingin alamat `@sintaksis.biz.id` (bukan subdomain). Verifikasi kebutuhan produk: apakah alamat harus di apex domain atau subdomain bisa diterima?

### 3.4 Provider inbound lain

Provider inbound email yang bisa jadi alternatif (bukan Cloudflare Email Routing yang mengambil alih MX):

- **Amazon SES (incoming):** Menerima email via receiving rule, bisa forward ke endpoint HTTPS/SMTP. Tapi SES incoming bukan layanan generik "terima semua mail untuk domain" — butuh konfigurasi rules per alamat.
- **Mailgun Inbound:** Menerima mail, bisa forward via route ke webhook/SMTP.
- **Forwarding service lain:** Mis. ImprovMX, ForwardEmail — tapi hampir semuanya bekerja dengan mengubah MX atau mengarahkan ke subdomain.

Kesimpulan: Semua provider inbound forwarding yang umum mengharuskan domain untuk mengarahkan MX ke mereka, atau menggunakan subdomain dengan MX sendiri. **Tidak ada provider inbound yang bisa "mengambil sebagian traffic" tanpa mengubah MX record domain utama.**

---

## 4. Model Mailbox Sementara pada Stalwish

### 4.1 Fitur Stalwish yang relevan

Fitur-fitur di Stalwish yang relevan untuk mail sementara:

**a. Virtual mailboxes (REAL atau VIRTUAL?)**

Dokumen Stalwish yang ditemukan: [Addresses, aliases and catch-all](https://stalw.art/docs/domains/addresses) menjelaskan bahwa recipient resolution terjadi melalui domain, sub-addressing, masked addresses (Enterprise), external directory, local addresses (account/group / mailing list), catch-all, dan relaying.

**Tidak ada dokumen yang menjelaskan "virtual mailboxes" sebagai fitur terpisah** di Stalwish — email di-resolve ke account, group, atau mailing list yang nyata.

Status: **TIDAK DITEMUKAN** — Stalwish mungkin tidak memiliki konsep "virtual mailbox" yang terpisah dari akun fisik. Perlu verifikasi ke dokumentasi lengkap dan/atau kode sumber Stalwish.

**b. Email templates / disposable mailboxes (Enterprise only)**

Stalwish Enterprise memiliki fitur **Masked Email**:
> "Masked emails are disposable, per-service email addresses that route to a user's real inbox. Instead of handing out a primary address to every newsletter, shop, or forum, a user can generate a unique masked address for each service."

Sumber: [Stalwish v0.16 Blog: Masked Emails](https://stalw.art/blog/stalwart-0-16) dan [Masked email docs](https://stalw.art/docs/email/management/masked-email), diakses 2026-11-14.

Fitur ini memungkinkan:
- User membuat alamat sementara (masked) yang di-forward ke akun asli
- Setiap masked address bisa di-disable secara individual
- Masked address terikat ke satu user account

**Namun:** masked email adalah fitur **Enterprise edition** (berbayar). Untuk Community edition, fitur ini TIDAK tersedia.

**c. Alias**

Setiap account bisa punya banyak alias (EmailAlias). Alias adalah address yang menerima mail dan di-deliver ke account yang sama. Alias bisa dinonaktifkan tanpa dihapus. Alias adalah **exact address**, bukan pattern.

Sumber: [Addresses, aliases and catch-all](https://stalw.art/docs/domains/addresses), diakses 2026-11-14.

**d. Catch-all address**

Domain bisa memiliki `catchAllAddress` — satu alamat yang menerima semua mail untuk unknown recipients di domain tersebut. Catch-all meningkatkan volum spam karena menerima semua alamat yang dicoba.

Sumber: [Addresses, aliases and catch-all](https://stalw.art/docs/domains/addresses), diakses 2026-11-14.

**e. Quota dan retention (DataRetention)**

Stalwish memiliki objek DataRetention dengan setting:
- `expungeTrashAfter`: Duration (default 30 hari) — berapa lama pesan di Trash/Junk sebelum auto-expunge
- `expungeSubmissionsAfter`: Duration (default 5 hari) untuk sent mail
- `archiveDeletedItemsFor`: Duration (Enterprise) — berapa lama keep deleted items di archive sebelum permanently delete
- `expungeSchedule`: Cron schedule untuk auto-expunge (default pukul 0)

Sumber: [DataRetention docs](https://stalw.art/docs/ref/object/data-retention), diakses 2026-11-14.

**f. JMAP API untuk manajemen**

Stalwant mengekspos JMAP API untuk:
- Membuat/menghapus account
- Mengelola aliases
- Mengelola mailing lists
- Mengelola quota per account
- Mengelola domain

Sumber: [JMAP capabilities](https://stalw.art/docs/http/jmap/capabilities), [Account object](https://stalw.art/docs/ref/object/account), diakses 2026-11-14.

**g. JMAP Push / WebSocket untuk realtime**

Stalwish mendukung:
- `urn:ietf:params:jmap:websocket` — JMAP over WebSocket
- `urn:ietf:params:jmap:emailpush` — push notification untuk konten email
- `urn:ietf:params:jmap:webpush-vapid` — VAPID untuk push subscription

Sumber: [JMAP capabilities](https://stalw.art/docs/http/jmap/capabilities), diakses 2026-11-14.

**h. IMAP**

Stalwish implements [IMAP4rev2](https://stalw.art/docs/email/settings/imap) untuk sinkronisasi mailbox dengan klien desktop/mobile.

### 4.2 4 Opsi Model Mailbox

#### Opsi A: Physical account per alamat

Setiap alamat sementara (mis. `temp123@domain.com`) dibuat sebagai Stalwish Account object terpisah.

| Dimensi | Keterangan |
| --- | --- |
| **Security isolation** | Tinggi — setiap account memiliki storage, quota, dan permissions terpisah. |
| **Overhead pembuatan** | Tinggi — setiap account butuh provisioning (JMAP API call, quota config, password/reset). |
| **Retensi** | Bisa diatur via DataRetention per account, tapi perlu konfigurasi otomatis untuk auto-delete. |
| **Validasi recipient** | Alamat benar-benar ada di Stalwish sebagai account. |
| **Enforcement expiry** | TIDAK ada fitur native TTL per account. Butuh custom daemon eksternal atau JMAP API untuk menghapus account setelah expiry. |
| **Perilaku delete** | Menghapus account → archives deleted items jika di-configure, lalu permanent delete sesuai schedule. |
| **Konversi temp → permanen** | Straightforward — ubah account menjadi permanen (ubah password, extend quota). |
| **Race condition** | Pesan bisa datang saat account sedang dihapus — Stalwish akan reject RCPT TO jika account sudah dihapus. |
| **Storage overhead** | Setiap account punya storage terpisah — overhead signifikan jika banyak alamat sementara. |
| **Dukungan API** | JMAP API lengkap untuk account CRUD. |

**Status rekomendasi:** Bisa dipakai tapi perlu custom automation. Tidak ada fitur TTL bawaan.

#### Opsi B: Alias dari satu account

Satu account "master" (mis. `temporary@domain.com`) dengan banyak alias sementara. Setiap alias diberikan ke user.

| Dimensi | Keterangan |
| --- | --- |
| **Security isolation** | Rendah — semua alias masuk ke satu account, satu storage. |
| **Overhead pembuatan** | Rendah — cukup create alias via JMAP API. |
| **Retensi** | Retensi diatur untuk satu account, gabungan semua alias. |
| **Validasi recipient** | Alias benar-benar ada di Stalwish. |
| **Enforcement expiry** | Alias bisa dinonaktifkan via JMAP API (disable tanpa delete). Butuh custom logic untuk auto-disable setelah expiry. |
| **Perilaku delete** | Nonaktifkan alias → mail ditolak. |
| **Konversi temp → permanen** | Alias bisa di-"promote" dengan creating account baru dan memindahkan mail (bisa via JMAP copy atau export/import). |
| **Race condition** | Pesan yang datang setelah alias nonaktif → reject. |
| **Storage overhead** | Rendah — satu storage untuk semua alias. |
| **Dukungan API** | JMAP API untuk alias CRUD. |

**Status rekomendasi:** Paling ringan dalam hal resource, tapi tidak ada isolasi per-alias. Cocok untuk skenario di mana semua mail sementara milik satu user dan dipisah hanya untuk tracking/label.

#### Opsi C: Virtual mailbox (jika ada di Stalwish)

Status: **TIDAK TERVERIFIKASI** — fitur ini tidak ditemukan di dokumentasi Stalwish yang ada. Jika "virtual mailbox" diartikan sebagai "address yang tidak punya account fisik tapi langsung di-forward ke destinasi lain", ini mungkin diimplementasikan lewat catch-all atau mailing list dengan forwarding. Namun ini bukan fitur "virtual mailbox" yang first-class.

Jika Stalwish benar-benar tidak punya fitur ini, opsi C tidak terpakai.

#### Opsi D: Shared mailbox + routing ketat

Menggunakan mailing list atau group sebagai shared mailbox. Mail datang ke shared address, di-forward/di-distribusikan ke anggota.

| Dimensi | Keterangan |
| --- | --- |
| **Security isolation** | Sedang — shared mailbox accessible by multiple members. |
| **Overhead pembuatan** | Sedang — perlu create mailing list/group. |
| **Retensi** | Retensi diatur untuk shared mailbox. |
| **Validasi recipient** | Alamat mailing list ada. |
| **Enforcement expiry** | Bisa di-set expiry di level mailing list, tapi butuh logic custom. |
| **Perilaku delete** | Delete mailing list → mail ditolak. |
| **Konversi temp → permanen** | Pending — perlu migrasi ke account permanen. |
| **Race condition** | Members join/leave during delivery — Stalwish expand recipients at RCPT TO time. |
| **Storage overhead** | Mail disimpan di shared mailbox — overhead per-member rendah tapi akses control perlu diatur. |
| **Dukungan API** | MailingList object di JMAP API. |

**Status rekomendasi:** Kurang cocok untuk mail sementara per-user karena focused pada distribusi ke banyak penerima, bukan mailbox per-user.

### 4.3 Rekomendasi + Confidence

| Model | Confidence | Alasan |
| --- | --- | --- |
| **Opsi B (Alias dari satu account)** | Tinggi untuk MVP | Paling simpel, resource efisien, ada di Community edition, API lengkap. Tapi tidak ada fitur auto-expiry native — butuh custom daemon/JMAP client untuk nonaktifkan alias setelah TTL. |
| **Opsi A (Physical account per alamat) + custom automation** | Sedang | Lebih bersih secara isolasi, tapi overhead storage tinggi untuk banyak alamat dan butuh custom automation untuk expiry. |
| **Opsi C (Virtual mailbox native)** | Rendah | Fitur tidak ditemukan di docs — perlu verifikasi langsung ke kode atau support Stalwish. |
| **Opsi D (Shared mailbox)** | Rendah untuk sementara | Kurang cocok untuk mail sementara per-user. |

**Rekomendasi utama untuk MVP:** Gunakan **Opsi B (Alias dari satu account)** dengan custom daemon/integrasi yang:
1. Membuat alias via JMAP API saat user meminta alamat sementara.
2. Menyimpan metadata (expiry, owner) di database eksternal (bukan di Stalwish).
3. Mematikan alias (disable) saat expiry habis, atau hapus jika tidak butuh lagi.
4. Mengirim notifikasi ke user jika ada mail masuk selama periode sementara.

**Confidence: 0.7 (tinggi untuk kemampuan implementasi, sedang untuk fitur native expiry karena harus custom).**

**PoC yang wajib dijalankan:**

1. Buktikan bahwa JMAP API bisa membuat dan menonaktifkan alias via API call (dokumentasi: [Account object](https://stalw.art/docs/ref/object/account)).
2. Buktikan bahwa nonaktifkan alias menyebabkan mail ditolak (RCPT TO reject) — tes dengan mengirim email ke alias yang dinonaktifkan.
3. Buktikan bahwa mail yang datang sebelum alias nonaktif tetap di-deliver ke account — dan bisa di-retry/di-baca via IMAP/JMAP.
4. Evaluasi dampak storage jika alias digunakan skala besar — apakah growth signifikan?
5. Jika menggunakan Opsi A (physical account), buktikan bahwa delete account tidak secara instan menghapus semua mail (karena archiveDeletedItemsFor mungkin memperlambat deletion).
6. Verifikasi berapa lama deletion cycle — apakah mail benar-benar hilang setelah account dihapus, atau ada jendela di mana mail bisa masuk ke account yang sudah dihapus (race condition).

---

## 5. Model Mailbox Permanen

### 5.1 Kebutuhan inbound-only MVP vs outbound email

Terdapat dua level kebutuhan:

**Level 1: Inbound-only (MVP)**
- Domain menerima email masuk via SMTP inbound (port 25/587).
- Mail disimpan di mailbox Stalwish.
- User bisa membaca via IMAP/JMAP.
- User bisa mengirim email via SMTP submission (port 587/465) jika butuh kirim — tapi ini opsional untuk MVP inbound-only.
- Tidak perlu MX record ke domain jika hanya inbound, tapi MX record tetap dibutuhkan untuk menerima mail.

**Level 2: Full outbound (nanti)**
- VPS bisa mengirim email via SMTP (port 587 ke MX eksternal, atau port 25 ke MX jika tidak diblokir).
- Domain punya SPF, DKIM, DMARC yang di-publish untuk domain sendiri.
- Mail yang dikirim melewati outgoing mail server Stalwish.
- Butuh outbound route, DKIM keys, dan kemungkinan relay rules.

### 5.2 Dukungan Stalwish untuk mailbox permanen

**IMAP:**
- Stalwish implements IMAP4rev2.
- Account punya special-use folders (Inbox, Drafts, Sent, Trash, Junk, Archive) yang otomatis dibuat saat account dibuat.
- Sumber: [IMAP and POP3 docs](https://stalw.art/docs/email/settings/imap), diakses 2026-11-14.

**SMTP Submission (587/465):**
- Stalwish punya SMTP submission listener yang menerima authenticated submission.
- Autentikasi: plaintext, CRAM-MD5, SCRAM-SHA-256, dll.
- Sumber: [SMTP authentication docs](https://stalw.art/docs/mta/inbound/auth), diakses 2026-11-14.

**Webmail:**
- Stalwish punya WebUI yang menyediakan webmail interface.
- Sumber: [WebUI docs](https://stalw.art/docs/management/webui/), diakses 2026-11-14.

**Penyimpanan:**
- Mail disimpan di storage backend (default: file-based atau bisa PostgreSQL? — **TIDAK DITEMUKAN** di docs terkait storage backend alternatif. DataRetention docs menyebut "data store" dan "blob store" tapi tidak spesifik backend).
- Sumber: [DataRetention docs](https://stalw.art/docs/ref/object/data-retention), diakses 2026-11-14.

**Kompatibilitas klien eksternal:**
- Klien IMAP apa pun (Thunderbird, Apple Mail, mobile) bisa connect ke Stalwish.
- Klien JMAP apa pun yang support RFC 8620/8621 bisa connect.
- Sumber: [JMAP capabilities](https://stalw.art/docs/http/jmap/capabilities), diakses 2026-11-14.

### 5.3 Kebutuhan outbound email — masa depan

Jika DomiBox nanti butuh mengirim email:
- VPS butuh outbound port 25 (mis. ke MX eksternal) atau port 587 (submission ke relay).
- Tencent memblokir outbound 25 default — perlu unblock via console.
- Domain butuh SPF record yang publikasikan di DNS.
- DKIM keys harus di-generate di Stalwish dan dipublish di DNS.
- DMARC policy ditentukan di DNS.

Sumber: [Tencent Unblocking Port 25](https://intl.cloud.tencent.com/document/product/213/34833), diakses 2026-11-14.

**Untuk MVP inbound-only:** outbound email TIDAK wajib. Domain bisa hanya receive. Tapi MX record tetap dibutuhkan di DNS.

---

## 6. Strategi Hapus Mailbox

### 6.1 Warning eksplisit: "Hanya menyembunyikan alamat" tidak boleh membiarkan pesan masuk selamanya

Pendekatan yang berbahaya: "nonaktifkan alamat tapi tidak hapus account" → akun tetap ada, email tetap masuk, storage terus bertambah. Ini TIDAK diterima.

Pendekatan yang benar:
1. **Nonaktifkan alias/address** → mail ditolak di RCPT TO stage.
2. **Hapus account** → mail yang sudah masuk di-expunge sesuai retention, mail baru ditolak.
3. **Pastikan ada retention policy** yang membersihkan mail yang sudah tidak relevan.

### 6.2 Recipient validation dan perilaku reject

Stalwish melakukan recipient validation di RCPT TO stage SMTP:
- Jika recipient not found (account, alias, catch-all, group, mailing list) → reject dengan SMTP error (550/551/553).
- Ini berarti jika account/alias dihapus, mail yang datang setelahnya langsung ditolak — tidak masuk ke mailbox.

Sumber: [RCPT TO stage docs](https://stalw.art/docs/mta/inbound/rcpt), diakses 2026-11-14.

### 6.3 Retensi dan penghapusan account

**DataRetention config:**
- `expungeTrashAfter`: pesan di Trash/Junk di-expunge setelah 30 hari (default).
- `expungeSubmissionsAfter`: sent mail di-expunge setelah 5 hari.
- `archiveDeletedItemsFor`: (Enterprise) berapa lama keep deleted items di archive sebelum permanent delete. Jika null, langsung permanently delete.
- `expungeSchedule`: kapan cron dijalankan (default pukul 0).

**Penghapusan account:**
- Hapus account via JMAP API → account dihapus dari directory.
- Mail yang sudah ada: tetap ada sampai expunge schedule menjalankannya.
- Mail baru: ditolak karena account tidak ada.

**State reconciliation:**
- Jika ada mail yang sedang dalam transit (SMTP transfer sedang berlangsung) saat account dihapus → outcome tergantung: mungkin mail selesai transfer tapi kemudian di-expunge, atau mungkin rejected di RCPT TO (jika penerima sudah invalid saat RCPT TO dikirim).
- Race condition: account dihapus di antara waktu RCPT TO dan waktu message data transfer — Stalwish mungkin sudah accepted RCPT TO tapi kemudian reject saat data transfer? **TIDAK DITEMUKAN** di docs. Ini perlu verifikasi di PoC.

**Pesan yang telat (late-arriving mail):**
- Mail yang dikirim ke alamat sementara yang sudah kedaluwarsa tapi yang kirim belum tahu → mail reject di SMTP.
- Tidak ada queue atau deferred delivery untuk mail yang ditolak.
- Mail yang sudah diterima sebelum expiry habis: tetap ada di mailbox sampai di-expunge sesuai retention.

### 6.4 State machine lifecycle

Disarankan state machine untuk alamat sementara:

1. **PENDING** — alamat dibuat, belum aktif (alias nonaktif).
2. **ACTIVE** — alias aktif, mail masuk.
3. **EXPIRING** — countdown expiry, user diberitahu.
4. **EXPIRED** — alias nonaktifkan (disabled), mail masuk ditolak.
5. **DELETED** — account/alias dihapus, mail sudah expunge.

Transisi state ini harus di-manage oleh custom integration, bukan oleh Stalwish native.

---

## 7. JMAP vs IMAP untuk Integrasi Aplikasi

### 7.1 JMAP (JSON Meta Application Protocol)

**Keunggulan untuk aplikasi DomiBox:**
- API JSON-based, lebih mudah diintegrasikan dengan aplikasi web/modern.
- Satu endpoint (`/jmap`) untuk semua operasi: mailbox, message, draft, identities, contacts, calendars.
- Push via WebSocket atau EmailPush (push notification ke client).
- Sync cepat: changes API (`/changes`) untuk sync incremental.
- Support untuk CRUD account, aliases, mailing lists via `urn:stalwart:jmap` extension — ini adalah **configuration and management API** yang memungkinkan aplikasi untuk manage Stalwish configuration via JMAP.
- Sumber: [JMAP capabilities](https://stalw.art/docs/http/jmap/capabilities), [HTTP API overview](https://stalw.art/docs/development/api), diakses 2026-11-14.

**Polling vs realtime:**
- Polling: client bisa polling `/jmap/changes` secara berkala untuk cek mail baru.
- Realtime: JMAP push subscription (EmailPush) atau WebSocket bisa mengirim notifikasi realtime saat mail baru masuk.
- Sumber: [JMAP Push docs](https://stalw.art/docs/http/jmap/push), diakses 2026-11-14.

### 7.2 IMAP

**Keunggulan:**
- Standard protocol yang didukung luas oleh klien email (desktop/mobile).
- Sync state full: flags, folders, sequence numbers.
- IDLE command untuk realtime notification (server push saat mail baru).

**Keterbatasan untuk aplikasi:**
- Protocol lebih berat daripada JMAP (binary protocol vs JSON).
- Tidak ada API untuk manajemen account/configurasi — hanya mail access.
- IDLE realtime tapi perlu persistent connection.

### 7.3 Rekomendasi untuk DomiBox

**Untuk integrasi aplikasi (backend DomiBox → Stalwish):**
- Gunakan **JMAP** karena:
  - Satu API untuk semua operasi (mail + config).
  - Push support untuk realtime notification.
  - Lebih mudah di-integrasikan dengan aplikasi web (JSON + HTTP).
  - Ada extension `urn:stalwart:jmap` untuk management API.

**Untuk access klien eksternal (user email client):**
- IMAP tetap dibutuhkan karena klien email umum (Thunderbird, Outlook, mobile) mengandalkan IMAP, bukan JMAP.
- Stalwish menyediakan IMAP, jadi ini tidak menjadi masalah.

**Kesimpulan:** DomiBox backend butuh JMAP untuk integration dan management. Stalwish juga menyediakan IMAP untuk klien user. Ini adalah kombinasi yang masuk akal.

---

## 8. Matriks Port & Jaringan

### 8.1 Port yang Relevan untuk DomiBox Mail

| Port | Protokol | Bind Address | Publik/Privat | Keperluan | Catatan Security Group | Status Saat Ini | Konflik dengan rust |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **22** | SSH | 0.0.0.0 | Publik | Manajemen VPS | Diperbolehkan (sudah terbuka) | TERVERIFIKASI: listening | Tidak ada |
| **25** | SMTP (inbound) | 0.0.0.0 (disarankan) | Publik | Menerima email masuk | Diperlukan inbound rule untuk TCP/25 dari 0.0.0.0/0 | TIDAK LISTENING — perlu Stalwish + firewall | Tidak ada (rustfs 9000-9001) |
| **465** | SMTPS (submission TLS) | 0.0.0.0 (opsional) | Publik | Submission email terenkripsi | Sama seperti 587 | TIDAK LISTENING | Tidak ada |
| **587** | Submission (STARTTLS) | 0.0.0.0 (disarankan) | Publik | Email submission dari klien | Diperlukan inbound rule | TIDAK LISTENING | Tidak ada |
| **80** | HTTP (ACME challenge) | 127.0.0.1 atau 0.0.0.0 | Publik | HTTP-01 challenge untuk Let's Encrypt | Diperlukan untuk ACME jika tidak pakai DNS-01 | TIDAK LISTENING | Tidak ada |
| **443** | HTTPS | 0.0.0.0 (jika pakai Caddy) | Publik | Webmail / JMAP API + TLS | Diperlukan untuk WebUI/JMAP/TLS | TIDAK LISTENING | Tidak ada |
| **993** | IMAPS (IMAP TLS) | 0.0.0.0 (opsional) | Publik | IMAP over TLS | Diperlukan inbound rule | TIDAK LISTENING | Tidak ada |
| **143** | IMAP (STARTTLS) | 0.0.0.0 (opsional) | Publik | IMAP dengan STARTTLS | Diperlukan inbound rule | TIDAK LISTENING | Tidak ada |
| **8080** | HTTP alternatif | 127.0.0.1 (jika Caddy di-front) | Privat | HTTP backend sebelum reverse proxy | Tidak perlu publik | Tidak ada | Tidak ada |
| **9000-9001** | rustfs object storage | 127.0.0.1 | Privat | Object storage (existing container) | **TIDAK DIUBAH — hanya untuk rustfs, bukan mail** | TERVERIFIKASI: sudah listening untuk rustfs | — |
| **53** | DNS (systemd-resolved) | 127.0.0.53 | Privat | DNS resolver lokal | Tidak bisa diubah | TERVERIFIKASI: systemd-resolved | Tidak ada |

### 8.2 Port yang TIDAK perlu dibuka di publik (untuk MVP inbound-only)

- **465, 587, 993, 143:** Tidak perlu dibuka jika hanya inbound-only dari server mail eksternal. Tapi untuk submission dari klien (user kirim email), perlu dibuka 587 atau 465.
- **8080:** Hanya untuk debug/internal, tidak perlu publik.

### 8.3 Konflik potensial

- **rustfs container (9000-9001)** tidak konflik dengan port mail jika Stalwish listen di port yang berbeda. Konflik hanya mungkin jika Stalwish salah konfigurasi bind ke alamat yang sama atau port yang tumpang tindih.
- **UFW** aktif tapi tidak bisa diverifikasi tanpa sudo — berpotensi memblokir port yang terbuka di security group.
- **Tidak ada reverse proxy** saat ini — ini baik untuk DomiBox karena VPS bisa langsung expose mail ports. Jika nanti butuh HTTPS, bisa tambah Caddy.

---

## 9. Footprint Sumber Daya

### 9.1 Konfigurasi VPS yang Tersedia

Dari inspeksi VPS (2026-11-14):

- **2 vCPU AMD EPYC 7K62**
- **RAM:** 3.6 GiB total, 3.0 GiB available saat inspeksi
- **Swap:** 1.9 GiB
- **Disk:** 59 GB total, 50 GB free
- **Docker Engine:** 29.9.3
- **Docker Compose:** v5.7.0
- **Container yang berjalan:** 1 container `rustfs/rustfs:1.0.4`

### 9.2 Estimasi footprint Stalwish + PostgreSQL

**PERINGATAN: Angka berikut adalah HIPOTESIS berdasarkan pengalaman umum dengan Rust application dan PostgreSQL, BUKAN angka benchmark yang dipublikasikan oleh Stalwish Labs.** Tidak ada benchmark publik yang ditemukan untuk Stalwish di VPS dengan spesifikasi ini.

**Hipotesis konsumsi resource (per service, idle/baseline):**

| Komponen | RAM (idle) | CPU (idle) | Disk (baseline) |
| --- | --- | --- | --- |
| **Stalwish (Rust binary)** | ~50-150 MB (estimasi Rust app biasa) | <0.1 vCPU (idle) | ~100-500 MB installation + database |
| **PostgreSQL (jika dipakai sebagai storage backend)** | ~50-100 MB | <0.1 vCPU (idle) | ~100-500 MB |
| **Caddy (jika dipakai sebagai reverse proxy untuk ACME/TLS)** | ~20-50 MB | <0.1 vCPU | ~50 MB |
| **Total per kombinasi** | ~120-300 MB | <0.3 vCPU | ~250-1000 MB |

**Hipotesis beban mail (kinerja saat dipakai):**

| Skenario | RAM (estimasi) | CPU (estimasi) | Catatan |
| --- | --- | --- | --- |
| **Idle (tidak ada mail masuk/kirim)** | 100-300 MB | <0.1 vCPU | Stalwart daemon + Postgres idle |
| **1000 email/hari (terima + baca)** | 150-400 MB | 0.2-0.5 vCPU | Beratnya SMTP parsing + IMAP/JMAP queries |
| **10.000 email/hari** | 200-600 MB | 0.5-1.0 vCPU | Perlu monitoring konkret |
| **Mail queue backlog (antrian pending)** | Naik seiring antrian | Naik seiring throughput | Terutama jika outbound blocked dan antrian menumpuk |

**Keterbatasan VPS yang relevan:**

- **RAM 3.6 GiB** — cukup untuk Stalwish + Postgres dengan headroom 2-3x dari estimasi idle. Tapi butuh monitoring untuk beban tinggi.
- **2 vCPU** — cukup untuk beban ringan-sedang. Untuk mail volume tinggi, CPU bisa jadi bottleneck (parsing, encryption, index).
- **Disk 50 GB free** — cukup untuk mail storage (mail rata-rata ~50-100 KB per email, jadi 50 GB bisa menampung ~500.000-1.000.000 email tanpa attachment besar).
- **TIDAK ADA benchmark publik** yang bisa dirujuk untuk angka pasti.

### 9.3 Apa yang HARUS diukur di PoC

Karena tidak ada data benchmark yang terverifikasi, PoC WAJIB mengukur:

1. **RSS memory Stalwish** saat idle (24 jam).
2. **RSS memory Stalwish** saat memproses mail masuk (load test simulasi).
3. **CPU usage** selama mail processing.
4. **Disk I/O** selama mail delivery dan retrieval.
5. **Latency SMTP RCPT TO** — seberapa cepat Stalwish merespon RCPT TO untuk recipient yang valid vs tidak valid.
6. **JMAP API response time** untuk operasi CRUD account/alias.
7. **Beban memory jika Postgres dipakai** sebagai storage backend (jika Stalwish support Postgres — **TIDAK DITEMUKAN** di docs).

Status keseluruhan: **TIDAK TERVERIFIKASI — semua angka di atas adalah HIPOTESIS. PoC benchmark WAJIB dijalankan sebelum masa production.**

---

## 10. Daftar Pemeriksaan PoC

Berikut langkah-langkah konkret yang bisa dieksekusi owner untuk membuktikan atau menolak setiap klaim di dokumen ini. Urutan dari yang paling menentukan (kritis) hingga yang tidak kritis.

### 10.1 Kritis: Verifikasi port 25 inbound bisa diterima

**Langkah:**

1. **Periksa security group Tencent / Lighthouse firewall:**
   - Cek apakah ada rule inbound yang mengizinkan TCP/25 dari `0.0.0.0/0` atau dari IP mail provider.
   - Jika tidak ada, tambahkan rule.
   - Sumber: [Tencent Cloud Security Group docs](https://intl.cloud.tencent.com/document/product/215/35536).

2. **Periksa UFW:**
   - `sudo ufw status verbose` — lihat apakah port 25 diizinkan.
   - Jika tidak, `sudo ufw allow 25/tcp`.
   - Status saat ini **NOT VERIFIED** karena tidak bisa dijalankan non-interaktif.

3. **Tes koneksi inbound:**
   - Dari mesin eksternal, lakukan `telnet <IP_VPS> 25` atau `openssl s_client -connect <IP_VPS>:25 -starttls smtp`.
   - Jika koneksi gagal, berarti masih diblokir di somewhere (security group, UFW, atau provider).
   - Sumber: mekanisme testing standar.

4. **Jika port 25 tidak bisa dibuka (diblokir oleh Tencent):**
   - Coba port alternatif (587) — apakah bisa dibuka?
   - Jika 587 bisa tapi 25 tidak, pertimbangkan untuk menerima mail via submission port (beberapa provider bisa kirim ke port 587 dengan STARTTLS).

**Status PoC:** GAGAL — belum dijalankan. Perlu akses VPS interaktif.

### 10.2 Kritis: Verifikasi Stalwish bisa di-deploy dan listen di port yang diinginkan

**Langkah:**

1. **Deploy Stalwish di VPS (docker atau binary).**
2. **Konfigurasi Stalwish untuk listen di port 25 dan 587.**
3. **Verifikasi bahwa Stalwish listen dan tidak bentrok dengan rustfs.**
4. **Cek log Stalwish apakah ada error saat bind.**
5. **Test dari eksternal: kirim email ke domain mail yang sudah di-setup MX record.**

**Status PoC:** GAGAL — belum dijalankan.

### 10.3 Kritis: Verifikasi MX record dan DNS

**Langkah:**

1. **Setup MX record untuk domain `sintaksis.biz.id` yang menunjuk ke IP VPS.**
   - Jika menggunakan Cloudflare DNS (karena domain sudah pakai Cloudflare nameserver), buat MX record via Cloudflare dashboard atau API.
   - Contoh: `sintaksis.biz.id. MX 10 mail.sintaksis.biz.id.`
   - Tambahkan A record untuk `mail.sintaksis.biz.id` ke IP VPS.
2. **Verifikasi MX record dengan `dig MX sintaksis.biz.id`.**
3. **Test kirim email dari luar (mis. Gmail ke alamat di domain)** dan cek apakah masuk ke Stalwish.

**Status PoC:** GAGAL — belum dijalankan.

### 10.4 Penting: Verifikasi fitur Stalwish untuk mail sementara

**Langkah:**

1. **Buktikan JMAP API bisa membuat dan menonaktifkan alias:**
   - Gunakan `curl` ke JMAP endpoint (`/jmap/`) dengan token auth.
   - Contoh: create alias via JMAP `EmailAlias` create.
   - Sumber: [Account object reference](https://stalw.art/docs/ref/object/account).
2. **Buktikan bahwa setelah nonaktifkan alias, mail yang dikirim ke alamat tersebut ditolak (RCPT TO reject).**
3. **Buktikan bahwa mail yang masuk sebelum nonaktifkan alias masih bisa dibaca via IMAP/JMAP.**
4. **Cek apakah ada fitur auto-expiry atau TTL di Stalwish:**
   - Baca docs lengkap tentang DataRetention dan expunge schedule.
   - Jika tidak ada, rancang custom daemon eksternal.
5. **Evaluasi Opsi B vs Opsi A:**
   - Buat perbandingan real: berapa RAM/CPU/storage jika pakai alias vs account fisik untuk 1000 alamat sementara?
   - Gunakan monitoring tools (mis. `ps`, `top`, `systemd-cgtop`) untuk ukur footprint aktual.

**Status PoC:** GAGAL — belum dijalankan.

### 10.5 Penting: Verifikasi TLS dan ACME

**Langkah:**

1. **Tentukan approach TLS:**
   - Opsi A: Stalwish native ACME (jika ada) — verifikasi via docs.
   - Opsi B: Caddy sebagai reverse proxy di depan Stalwish, Caddy handle ACME.
2. **Jika pakai Caddy:**
   - Deploy Caddy, setup reverse proxy ke Stalwish port 25/587/443.
   - Verifikasi certificate Let's Encrypt berhasil di-issue.
   - Test TLS connection dari eksternal.
3. **Jika Stalwish native support ACME:**
   - Verifikasi dokumentasi Stalwish tentang ACME.
   - Test setup.

**Status PoC:** GAGAL — belum dijalankan.

### 10.6 Penting: Verifikasi monitoring dan logging

**Langkah:**

1. **Identifikasi di mana Stalwish mencatat log SMTP (accepted/rejected RCPT, connection log).**
   - Baca docs Stalwish tentang logging/audit.
   - Jika tidak ada di docs, cek di source code atau default config.
2. **Setup monitoring dasar:**
   - `ss -tlnp | grep -E '25|587|993'` untuk cek port listening.
   - Log aggregator (mis. menggunakan `journalctl` jika Stalwish systemd service, atau docker logs).
3. **Alert: pesan yang ditolak (RCPT TO reject) harus tercatat dan bisa di-monitor.**

**Status PoC:** GAGAL — belum dijalankan.

### 10.7 Tidak kritis: Benchmark resource

**Langkah:**

1. **Ukur RSS memory Stalwish idle (24 jam).**
2. **Simulasi beban: kirim 1000 email dalam 1 jam, ukur resource.**
3. **Ukur latency SMTP dan JMAP API.**
4. **Bandingkan dengan kebutuhan DombaBox (berapa email/hari yang diperkirakan?).**
5. **Jika resource tidak cukup, evaluasi upgrade VPS atau optimasi.**

**Status PoC:** GAGAL — belum dijalankan.

---

## 11. Daftar Sumber

Semua sumber di bawah diakses pada tanggal 2026-11-14 kecuali disebutkan lain.

| No | Sumber | URL | Status | Keterangan |
| --- | --- | --- | --- | --- |
| 1 | Tencent Cloud — Unblocking Port 25 | [https://intl.cloud.tencent.com/document/product/213/34833](https://intl.cloud.tencent.com/document/product/213/34833) | TERVERIFIKASI | Kebijakan outbound port 25 default blocked, prosedur unblock. Update 2026-01-26. |
| 2 | Tencent Cloud — Port and Security Group | [https://intl.cloud.tencent.com/document/product/215/35536](https://intl.cloud.tencent.com/document/product/215/35536) | TERVERIFIKASI | Konsep security group, aturan inbound/outbound. Update 2024-10-22. |
| 3 | Tencent Cloud — CreateFirewallRules (Lighthouse API) | [https://www.tencentcloud.com/document/product/1103/42513](https://www.tencentcloud.com/document/product/1103/42513) | TERVERIFIKASI | API untuk firewall rules di Lighthouse. Update 2026-05-27. |
| 4 | Tencent Cloud — Ports FAQ | [https://www.tencentcloud.com/document/product/213/2502](https://www.tencentcloud.com/document/product/213/2502) | TERVERIFIKASI | FAQ ports Tencent CVM. Update 2025-12-17. |
| 5 | Stalwish — Addresses, aliases and catch-all | [https://stalw.art/docs/domains/addresses](https://stalw.art/docs/domains/addresses) | TERVERIFIKASI | Dokumentasi recipient resolution, alias, catch-all, sub-addressing. |
| 6 | Stalwish — Masked email (Enterprise) | [https://stalw.art/docs/email/management/masked-email](https://stalw.art/docs/email/management/masked-email) | TERVERIFIKASI | Fitur masked email untuk alamat sementara, hanya Enterprise. |
| 7 | Stalwish — DataRetention object | [https://stalw.art/docs/ref/object/data-retention](https://stalw.art/docs/ref/object/data-retention) | TERVERIFIKASI | Konfigurasi retensi, expunge schedule, archive. |
| 8 | Stalwish — JMAP capabilities | [https://stalw.art/docs/http/jmap/capabilities](https://stalw.art/docs/http/jmap/capabilities) | TERVERIFIKASI | Capability list, termasuk mail, submission, push. |
| 9 | Stalwish — Account object | [https://stalw.art/docs/ref/object/account](https://stalw.art/docs/ref/object/account) | TERVERIFIKASI | Struktur account, alias, quota, permissions. |
| 10 | Stalwish — HTTP API overview | [https://stalw.art/docs/development/api](https://stalw.art/docs/development/api) | TERVERIFIKASI | HTTP API termasuk JMAP endpoint. |
| 11 | Stalwish — IMAP and POP3 | [https://stalw.art/docs/email/settings/imap](https://stalw.art/docs/email/settings/imap) | TERVERIFIKASI | Implementasi IMAP4rev2, special-use folders. |
| 12 | Stalwish — RCPT TO stage | [https://stalw.art/docs/mta/inbound/rcpt](https://stalw.art/docs/mta/inbound/rcpt) | TERVERIFIKASI | Behavior RCPT TO stage, SMTP responses. |
| 13 | Stalwish — SMTP authentication | [https://stalw.art/docs/mta/inbound/auth](https://stalw.art/docs/mta/inbound/auth) | TERVERIFIKASI | Autentikasi SMTP, mechanisms. |
| 14 | Stalwish — WebUI | [https://stalw.art/docs/management/webui](https://stalw.art/docs/management/webui) | TERVERIFIKASI | Webmail interface. |
| 15 | Stalwish — JMAP Push | [https://stalw.art/docs/http/jmap/push](https://stalw.art/docs/http/jmap/push) | TERVERIFIKASI | Push notification, subscription. |
| 16 | Cloudflare — Email Routing DNS records | [https://developers.cloudflare.com/email-service/configuration/domains](https://developers.cloudflare.com/email-service/configuration/domains) | TERVERIFIKASI | MX override behavior, routing record. |
| 17 | Cloudflare — Email Routing DNS setup | [https://developers.cloudflare.com/email-routing/setup/email-routing-dns-records](https://developers.cloudflare.com/email-routing/setup/email-routing-dns-records) | TERVERIFIKASI | MX records yang ditambahkan saat Email Routing diaktifkan. |
| 18 | Stack Harbor — Cloudflare Email Routing MX conflict | [https://stackharbor.com/en/knowledge-base/cffix-email-routing-mx-conflict/](https://stackharbor.com/en/knowledge-base/cffix-email-routing-mx-conflict/) | TERVERIFIKASI | Artikel pihak ketiga menjelaskan mekanisme MX takeover. Update artikel 2026-07-03. |
| 19 | Stalwish v0.16 blog — Masked Emails | [https://stalw.art/blog/stalwart-0-16](https://stalw.art/blog/stalwart-0-16) | TERVERIFIKASI | Blog post menjelaskan fitur masked email. Update 2026-04-20. |
| 20 | Stalwish — Quotas | [https://stalw.art/docs/auth/authorization/quotas](https://stalw.art/docs/auth/authorization/quotas) | TERVERIFIKASI | Quota configuration per account. |
| 21 | VPS Inspeksi (langsung) | VPS Tencent, alias `vps-tencent3b` (43.153.206.84) | TERVERIFIKASI | Inspeksi dilakukan 2026-11-14: port listening, resource, container rustfs. |
| 22 | Stalwish — Enterprise edition | [https://stalw.art/enterprise](https://stalw.art/enterprise) | TERVERIFIKASI | Fitur Enterprise edition, termasuk masked email, multi-tenancy. |

### Sumber yang Tidak Ditemukan / Perlu Verifikasi Tambahan

| Klaim / Informasi | Status | Cara Verifikasi |
| --- | --- | --- |
| Apakah Stalwish mendukung ACME untuk TLS otomatis | TIDAK DITEMUKAN di docs | Baca docs Stalwish lengkap atau test di PoC. |
| Apakah Stalwish bisa pakai PostgreSQL sebagai storage backend | TIDAK DITEMUKAN di docs | Baca docs storage backend, atau tanya ke Stalwish support. |
| Lighthouse outbound port 25 restriction (apakah sama dengan CVM) | TIDAK DITEMUKAN | Verifikasi ke console Tencent atau support Tencent. |
| UFW status detail (port apa yang dibuka) | NOT VERIFIED | Perlu login VPS interaktif dengan sudo. |
| Stalwish behavior saat account dihapus di tengah SMTP transfer (race condition) | TIDAK DITEMUKAN | Test di PoC: kirim email, hapus account di tengah transfer, observasi. |
| Resource footprint Stalwish di VPS 2 vCPU / 3.6 GB RAM | TIDAK TERVERIFIKASI — tidak ada benchmark publik | PoC benchmark 24-48 jam. |
| Cloudflare Email Routing subdomain delegation behavior (apakah subdomain bisa punya MX sendiri) | TIDAK DITEMUKAN | Test di Cloudflare DNS: buat subdomain, set MX ke alamat lain, cek apakah berfungsi. |
| Integrasi JMAP Push/WebSocket ke aplikasi DomiBox | TIDAK DITEMUKAN | Reference implementasi, test di PoC. |

---

## 12. Ringkasan Keputusan Yang Perlu Dibuat

| Keputusan | Opsi | Keterangan |
| --- | --- | --- |
| **Apakah port 25 inbound bisa dibuka?** | (a) Buka port 25 via security group + UFW. (b) Gunakan alternatif (subdomain delegation, provider lain). | Tergantung hasil PoC verifikasi. |
| **Apakah DombaBox perlu subdomain mail (`mail.sintaksis.biz.id`)?** | (a) Gunakan apex domain. (b) Gunakan subdomain. | Subdomain lebih aman untuk delegasi/mail routing terpisah. |
| **Model mailbox sementara: mana yang dipakai?** | (a) Alias dari satu account. (b) Physical account per alamat. (c) Virtual mailbox (jika ada). | Rekomendasi utama: Opsi B (alias) untuk MVP, dengan custom automation. |
| **Apakah pakai Cloudflare Email Routing sebagai fallback?** | (a) Ya, tapi dengan subdomain delegation. (b) Tidak, karena mekanisme MX override terlalu invasif. | Harus di-evaluasi dengan hati-hati. |
| **TLS approach: Stalwish native ACME vs Caddy reverse proxy?** | (a) Stalwish native ACME. (b) Caddy reverse proxy. | Harus diverifikasi dukungan Stalwish untuk ACME. |
| **Storage backend: file-based saja atau Postgres?** | (a) File-based (default). (b) Postgres (jika support). | Harus diverifikasi support Postgres di Stalwish. |
| **Monitoring: apa yang cukup untuk MVP?** | (a) Logging + port checker. (b) Metrics + alerting. | Tergantung kebutuhan operational DombaBox. |

---

## 13. Catatan Akhir

Dokumen ini disusun berdasarkan riset dokumen vendor dan inspeksi VPS yang tersedia. Beberapa klaim memiliki tingkat kepercayaan yang rendah karena tidak bisa diverifikasi tanpa akses langsung ke sistem atau tanpa PoC yang dijalankan.

Klaibm yang tidak bisa diverifikasi disebutkan secara eksplisit sebagai "TIDAK TERVERIFIKASI" atau "TIDAK DITEMUKAN" dan disertai cara memverifikasinya.

File ini selesai pada 2026-11-14.
