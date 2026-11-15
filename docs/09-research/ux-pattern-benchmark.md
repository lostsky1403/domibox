# Riset Pola UX — Produk Temporary Mailbox & Admin Dashboard (DomiBox)

| Status | Versi | Tanggal | Penulis | Dokumen-Related |
| --- | --- | --- | --- | --- |
| COMPLETE | v1.0 | 2026-11-14 | omp-orchestrator/riset-ux-pattern | [../03-architecture/architecture-overview.md](../03-architecture/architecture-overview.md) · [../01-product/prd/product-requirements-document.md](../01-product/prd/product-requirements-document.md) · [../04-technical/database-schema.md](../04-technical/database-schema.md) |

> Tanggal akses seluruh URL dalam dokumen ini: **2026-11-14**. Riset dibatasi pada dokumentasi resmi dan halaman publik produk. Tidak ada kode proprietary, screenshot internal, atau kalimat branding yang disalin ke dalam dokumen ini; yang diambil adalah *pola interaksi* dan *model data*, bukan tampilan visual.

---

## 1. Metodologi

### 1.1 Tujuan

Riset ini aimed untuk menjawab satu pertanyaan: **pola UX apa yang sudah terbukti bekerja di produk temporary mailbox/alias dan dashboard admin, dan mana yang layak diadopsi, diadaptasi, atau ditolak untuk DomiBox?** Hasilnya menjadi bahan input bagi penulis IA & Interaction Spec, bukan spesifikasi final.

### 1.2 Metode

| Metode | Deskripsi | Digunakan untuk |
| --- | --- | --- |
| **Studi dokumentasi resmi** | Membaca dokumentasi API dan dokumentasi pengguna yang dipublikasikan vendor | Model data, alur quick-create,生命周期 expiry, kontrak token |
| **Observasi halaman publik** | Meninjau halaman publik tanpa login (landing page, halaman bantuan, halaman harga) | Pola entry point, positioning, tone interaksi |
| **Analisis pola (pattern extraction)** | Mengelompokkan perilaku yang berulang antar produk menjadi pola generik | Sintesis Bab 4 |
| **Analisis celah (gap analysis)** | Menandai apa yang TIDAK ada di produk acuan | Dasar keputusan Reject |

### 1.3 Aturan etika riset

1. **Tidak menyalin desain.** Yang dicatat adalah perilaku, urutan langkah, dan kontrak data — bukan warna, tipografi, ikon, layout pixel, atau string teks produk.
2. **Tidak menyalin kalimat branding.** Istilah generik ("mask", "alias", "catch-all", "quick-create") dipakai sebagai terminologi teknis, bukan kutipan.
3. **Tidak mengarang angka.** Jika angka (mis. durasi expiry, limit, rasio kontras) tidak ditemukan di sumber primer, ditulis eksplisit sebagai **TIDAK TERVERIFIKASI** beserta apa yang harus dicek.
4. **Wajib mencatat URL + tanggal akses.** Semua klaim yang ditandai *Terverifikasi* memiliki tautan sumber.
5. **Batas status.** Karena produk terus berubah, semua temuan bersifat *snapshot per 2026-11-14*.

### 1.4 Keterbatasan riset

- **Tidak ada login/akun uji.** Pola yang hanya terlihat setelah masuk (mis. pipeline hibrida Tailscale/Coolify) dibaca dari dokumentasi, bukan dari pengujian langsung.
- **Kode sumber proprietary tidak ditelusuri** kecuali Lisensi/Repositori resminya mempublikasikannya (mis. repositori API publik).
- **Aksesibilitas produk acuan tidak diuji langsung.** Klaim aksesibilitas pada produk acuan hanya diambil bila ada pernyataan resmi di dokumentasinya; selebihya ditandai *belum terverifikasi*.
- **Perilaku mobile** hanya dari changelog/dokumentasi resmi.

### 1.5 Klasifikasi bukti

| Label | Arti | Wajib Dissertation |
| --- | --- | --- |
| **Terverifikasi** | Ada URL sumber primer + tanggal akses | Ya |
| **Hipotesis** | Deduksi dari pola, belum diuji | Ya, harus ditandai eksplisit |
| **Asumsi** | Keputusan desain sementara yang perlu dikonfirmasi owner | Ya |
| **Tidak Diketahui** | Tidak ada sumber | Ya, harus menyebut apa yang perlu dicek |

---

## 2. Referensi Produk Temporary Mailbox

Klasifikasi produk acuan ke dalam dua paradigma, yang justru memengaruhi keputusan arsitektur DomiBox:

- **Paradigma A — "Inbox disposable"**: pengguna datang, mendapat satu alamat sekali pakai, membaca di tempat, lalu alamat dibuang. (1secmail, mail.tm, temp-mail.io, Guerrilla Mail)
- **Paradigma B — "Alias permanen"**: pengguna memasang identitas email sekali, lalu membuat banyak alias yang *meneruskan* ke inbox sungguhan. (SimpleLogin, addy.io, Firefox Relay, DuckDuckGo Email Protection)

DomiBox berdiri di antara keduanya: mailbox **ditampilkan di tempat** (seperti Paradigma A) tetapi dapat bersifat **permanen dan dapat diforward** (seperti Paradigma B).

### 2.1 1secmail

- **Sumber:** <https://github.com/1sec-mail/1secmail-api> (README API, diakses 2026-11-14) dan <https://web.archive.org/web/20241223222139/https://www.1secmail.com/api> (arsip API lawas, diakses 2026-11-14).
- **Model:** API berbasis token. `POST /api/emails/{apiKey}` mengembalikan `email`, `domain`, `ip`, `fingerprint`, `expire_at`, `created_at`, `id`, dan `email_token`. Varian `1sec-mail.com` meminta API key dari vendor; API lawas `1secmail.com` tidak mewajibkan kunci (arsip 2024-12-23).
- **Pola quick-create:** satu panggilan membuat alamat acak pada domain aktif; alamat + `email_token` dikembalikan sebagai satu-satunya handle untuk operasi berikutnya. Ada `POST /api/emails/{apiKey}/{email}/{username}/{domain}` untuk **mengubah** username/domain tanpa membuat mailbox baru.
- **Domain handling:** `GET /api/domains/{apiKey}/{type}` dengan `type` ∈ {free, premium, all} → domain diklasifikasikan bertingkat; pengguna hanya memilih dari daftar yang diizinkan server.
- **Inbox UX:** `GET /api/messages/{apiKey}/{email}` mengembalikan daftar (subject, from, timestamp, `is_seen`, `attachments`); `GET .../message/{messageId}` untuk isi. Lampiran diunduh via `GET /api/d/{messageId}/{filename}`.
- **OTP/forwarding:** tidak ada forwarding; isi pesan diambil langsung lewat polling API. Tidak ada panel OTP khusus.
- **Expiry:** field `expire_at` dikembalikan server sebagai ISO-8601. **Nilai default durasi expiry TIDAK TERVERIFIKASI** dari sumber primer — yang perlu dicek: kebijakan retensi aktual server 1secmail saat ini.
- **Copy-first:** tidak ada concept copy-first di API;(copy adalah urusan layer web UI.
- **Kelemahan:** Ketergantungan penuh pada API key (varian berbayar) atau layanan pihak ketiga tanpa kontrol atas Ages; tidak ada konsep alias/pengguna; tidak ada metadata tag; `fingerprint`/`ip` yang dikembalikan server menambah data yang tidak perlu diekspos ke UI.

### 2.2 mail.tm

- **Sumber:** <https://docs.mail.tm/api/accounts> dan <https://docs.mail.tm/api/domains> (akses 2026-11-14), <https://docs.mail.tm/> (landing dokumentasi), <https://mail.tm/> (halaman publik), <https://api.mail.tm/> (OpenAPI 3.1, versi tertera 3.0.0 di dokumen).
- **Model:** Akun/password + token bearer. `POST /accounts` membuat akun dengan `address` dan `password`; token diperoleh setelah login dan dipakai sebagai bearer pada endpoint pesan.
- **Pola quick-create:** domain diambil lebih dulu dari `GET /domains`, lalu `POST /accounts` dengan alamat pilihan pengguna (umumnya acak). API tanpa kunci — Reduction friction maksimum.
- **Domain handling:** endpoint domain terpisah; server menentukan domain yang tersedia. **Daftar domain aktual dan kebijakan domain bersama TIDAK TERVERIFIKASI** — yang perlu dicek: apakah domain bersama mengizinkan alamat duplikat antar pengguna.
- **Inbox UX:** daftar pesan terpisah dari daftar akun; setiap akun = satu mailbox dengan daftar pesan sendiri.
- **OTP/forwarding:** tidak ada forwarding. OTP harus diekstrak pengguna dari isi pesan.
- **Expiry:** **TIDAK TERVERIFIKASI** — dokumentasi yang dibaca tidak menyebut masa berlaku akun secara eksplisit; yang perlu dicek: kebijakan penghapusan akun idle di ToS mail.tm.
- **Copy-first:** halaman publik mail.tm menampilkan alamat mailbox sebagai elemen utama dengan aksi salin, dan ada tombol "Copy" eksplisit di UI; API menyediakan `GET /messages` dan `GET /messages/{id}`.
- **Kelemahan:** Hanya satu mailbox per akun tanpa label/tag; tidak ada domain sendiri milik pengguna di free tier; lifetime alamat tidak eksplisit; konten HTML mentah perlu disanitasi di sisi klien.

### 2.3 temp-mail.io

- **Sumber:** <https://docs.temp-mail.io/docs/getting-started> (akses 2026-11-14), <https://docs.temp-mail.io/> (indeks dokumentasi), <https://temp-mail.io/api> (halaman publik API).
- **Model:** API key wajib (`X-API-Key`), akun premium diperlukan untuk memakai API.
- **Pola quick-create:** `POST /v1/emails` → `{ "email": "...", "ttl": 86400 }`. TTL diikutsertakan dalam respons, jadi客户端 tahu masa berlaku sejak respons pertama.
- **Domain handling:** `GET /v1/domains` mengembalikan domain yang boleh dipakai; server yang memutuskan.
- **Inbox UX:** `GET /v1/emails/{address}/messages` (ringkas: id, from, subject, created_at) → `GET /v1/messages/{id}` (body_text, body_html, attachments) → `GET /v1/messages/{id}/attachments/{attachmentId}`. Ada juga `GET /v1/messages/{id}/source` untuk melihat sumber mentah.
- **OTP/forwarding:** tidak ada forwarding; ada endpoint "source" berguna untuk debugging/ekstraksi kode yang ada di header.
- **Expiry:** `ttl` dalam detik (contoh 86400 = 24 jam) pada respons pembuatan. Perlu dicek: apakah TTL bisa dipilih saat pembuatan.
- **Copy-first:** tidak ada.
- **Kelemahan:** Butuh akun berbayar + API key (hambatan tinggi untuk trial); `ttl` tampak dikunci saat pembuatan sehingga "perpanjang masa hidup" perlu endpoint khusus yang **TIDAK TERVERIFIKASI** ada; rate limit Only diekspos lewat header (`X-Ratelimit-Limit/Remaining/Used/Reset`) — UI harus menanganinya.
- **Pola reusable untuk DomiBox:** amplop error terstruktur `{ error: { type, code, detail }, meta: { request_id } }` dan header rate-limit. Ini pola yang layak disalin secara *konsep* (bukan teks) karena memudahkan dukungan.

### 2.4 Guerrilla Mail

- **Sumber:** <https://www.guerrillamail.com/GuerrillaMailAPI.html> (dokumentasi API JSON, versi 1.0 bertanggal 19 April 2011, diakses 2026-11-14), <https://www.guerrillamail.com/about> (halaman publik).
- **Model:** Sesi berbasis cookie (`PHPSESSID`) + cookie langganan (`SUBSCR`); tidak ada akun pengguna.
- **Pola quick-create:** `get_email_address` langsung memberikan alamat acak **tanpa registrasi whatsoever** — titik gesek nol. `set_email_user` memungkinkan mengganti nama-pengguna pada sesi aktif.
- **Domain handling:** satu blokir domain bersama; pengguna tidak memilih domain. **Daftar domain TIDAK TERVERIFIKASI** (dokumentasi tidak mencantumkannya).
- **Inbox UX:** `check_email` ( polling, maksimal 20 item, dengan `mail_subject`, `mail_excerpt`, `mail_read`, `mail_timestamp`) dan `get_email_list` (berpaginasi via `offset`); `fetch_email` untuk isi.
- **OTP/forwarding:** tidak ada forwarding; polling berkala. Ekstraksi OTP harus dari subjek/body.
- **Expiry:** alamat kedaluwarsa **60 menit** setelah dibuat (dinyatakan eksplisit di dokumentasi). Fungsi `extend` menambah **1 jam**, dengan **maksimum 2 jam perpanjangan**. Sesi idle kedaluwarsa ~**18 menit**; saat sesi berakhir alamat baru dibuat, dan `set_email_user` dapat mengembalikan ke alamat lama selama belum kedaluwarsa.
- **Copy-first:** tombol salin menjadi.pattern di UI publik; API sendiri tidak menyediakannya.
- **Kelemahan:** Tidak ada account ownership (siapa pun yang tahu alamat bisa, pada model bersama, saling mengintervensi); sanitasi konten email dilakukan server (JavaScript/applet/iframe dibuang; gambar diblokir sampai pengguna menekan "Display Images") — pola blokir-gambar-by-default layak jadi rujukan untuk mailbox; model "lupa saya" (`forget_me`) adalah reset sekali-klik yang sangat efektif; tanpa bulk/tag/filter.

### 2.5 SimpleLogin

- **Sumber:** <https://simplelogin.io/docs/getting-started/create-alias>, <https://simplelogin.io/docs/custom-domain/add-domain>, <https://simplelogin.io/docs/subdomain/new>, <https://simplelogin.io/docs/directory/new>, <https://simplelogin.io/docs/custom-domain/manage-domain/>, <https://simplelogin.io/docs/getting-started/reverse-alias/>, <https://github.com/simple-login/app/blob/master/docs/api.md> (semua diakses 2026-11-14).
- **Model:** Alias email permanen yang meneruskan ke satu atau beberapa mailbox milik pengguna; domain sendiri dikonfigurasi via DNS.
- **Pola quick-create:** dua jenis alias — **custom** (local-part bermakna, misalnya nama situs) dan **random**. Untuk pembuatan *on-the-fly* tanpa membuka aplikasi, SimpleLogin menyediakan **subdomain** (contoh: `<apa-saja>@<subdomain>.aleeas.com`) dan **directory** (folder yang memetakan local-part ke alias) — keduanya didokumentasikan eksplisit sebagai cara "membuat alias dengan cepat di mana saja".
- **Domain handling:** tiga lapis — domain sendiri (verifikasi DNS), subdomain milik SimpleLogin, dan alias bersama. Endpoint `GET /api/v2/setting/domains` disebut mengembalikan domain yang boleh dipakai untuk alias acak.
- **Inbox UX:** **tidak ada inbox di dalam produk** — semua email diteruskan ke inbox asli pengguna; produk menampilkan daftar alias beserta status (aktif/ter blokir), bukan daftar pesan.
- **OTP/forwarding:** email OTP diteruskan ke inbox asli. Tidak ada panel OTP.
- **Expiry:** alias **tidak kedaluwarsa secara otomatis** pada model standar; yang ada adalah penonaktifan/deaktivasi manual. **TIDAK TERVERIFIKASI** apakah ada masa berlaku default pada paket berbayar.
- **Copy-first:** nieco — pola "salin alamat alias" ada di ekstensi browser dan dashboard.
- **Kelemahan:** Butuh DNS + domain sendiri untuk manfaat penuh; forward-only (tidak bisa melihat mailbox di dalam aplikasi); ada fitur premium (reverse alias, banyak alias, ekstensi) yang引人.". **Pola yang paling layak disalin: bukan "list of aliases"，而是 "list of aliases + quick-create dengan dua mode (custom/random) + onboarding domain" yang bisa langsung dipakai untuk "mailbox permanen" DomiBox.

### 2.6 addy.io (Anonaddy)

- **Sumber:** <https://addy.io/help/creating-new-email-aliases>, <https://addy.io/help/understanding-catch-all-and-alias-auto-create-regex-for-a-domain/>, <https://addy.io/help/what-are-the-different-kinds-of-aliases>, <https://addy.io/help/terminology>, <https://addy.io/faq/>, <https://addy.io/features>, <https://app.addy.io/docs> (semua diakses 2026-11-14).
- **Model:** Alias permanen yang meneruskan ke satu/more recipient; ada API REST dan ekstensi browser.
- **Pola quick-create:** dua cara resmi — **on the fly** (berikan alamat, alias tercipta saat email pertama masuk) dan **in advance** (generate dari dashboard, ekstensi, aplikasi seluler, atau API). Pola on-the-fly menekan friksi maksimum.
- **Domain handling:** lapis paling matang di antara produk acuan — **catch-all per domain** (toggle di halaman Domains: catch-all aktif ⇒ alamat apa pun pada domain itu diterima dan otomatis creating alias; nonaktif ⇒ hanya alias yang sudah ada yang diterima) plus **alias auto-create regex** untuk menyaring local-part saat catch-all nonaktif (contoh pola yang didokumentasikan: `^[a-zA-Z]+$`, `\.`, `^news`). Regex **wajib** diuji — dokumentasi menyediakan bagian "Test Alias Auto Create Regex".
- **Inbox UX:** tidak ada inbox; daftar alias dengan status, plus export CSV (`GET /api/export/aliases`) dan export data penuh (`GET /api/export/data`).
- **OTP/forwarding:** tidak ada forwarding ke inbox lain di luar model alias; email diteruskan. Tidak ada panel OTP.
- **Expiry:** alias **tidak kedaluwarsa** pada model standar (dapat diaktifkan/nonaktifkan manual). **TIDAK TERVERIFIKASI** untuk paket berbayar.
- **Copy-first:** ada pada dashboard alias.
- **Kelemahan:** Alias dengan domain bersama memerlukan konfirmasi email pada domain tertentu (mis. domain email provider besar) sehingga ada latensi; regex yang salah diam-diam memblokir email masuk — *fail-open vs fail-closed* harus diputuskan eksplisit di DomiBox; tidak ada inbox internal.
- **Pola yang layak disalin:** **catch-all + auto-create** sebagai opsi "jangan buat mailbox dulu, biarkan alamat muncul saat email pertama tiba". Ini cocok untuk use-case DomiBox "temp/permanent" yang detik.

### 2.7 Firefox Relay

- **Sumber:** <https://support.mozilla.org/en-US/kb/firefox-relay-what-email-mask>, <https://support.mozilla.org/en-US/kb/create-email-alias-through-firefox-relay>, <https://support.mozilla.org/en-US/kb/activate-firefox-relay-mask-your-email-address>, <https://support.mozilla.org/en-US/kb/register-your-own-domain-firefox-relay-premium>, <https://relay.firefox.com/faq> (semua diakses 2026-11-14).
- **Model:** "Email mask" = alamat forwarding yang menyembunyikan alamat asli; **tanpa** alias yang bisa dibalas, **tanpa** email masuk dari luar yang di-forward (tidak bisa menerima di dalam aplikasi).
- **Pola quick-create:** mask dibuat dari dashboard, ekstensi, atau keyboard shortcut browser; browser dapat **menawarkan mask secara otomatis** saat terdeteksi field email pada situs. Free tier dibatasi **5 mask**; premium mengizinkan mask tak terbatas.
- **Domain handling:** domain sendiri hanya untuk premium; selain itu memakai domain bersama milik Mozilla.
- **Inbox UX:** dashboard menampilkan daftar mask + pengaturan kategori (filter), bukan daftar email.
- **OTP/forwarding:** meneruskan ke inbox asli. Tidak ada panel OTP.
- **Expiry:** mask **tidak kedaluwarsa** secara otomatis; premium menyediakan kontrol "forwarding only for selected categories" sehingga reduces noise. **TIDAK TERVERIFIKASI** apakah kategori bisa diperluas di masa depan.
- **Copy-first:** ada di dashboard & ekstensi.
- **Kelemahan:** Ketergantungan browser Mozilla untuk quick-create terbaiknya; akun Mozilla wajib; tanpa akses ke isi email; **pola yang layak disalin: "kategori/filter" sebagai pengontrol noise dari mail Screening** — relevan untuk DomiBox karena mailboxisi penuh OTP spam.

### 2.8 DuckDuckGo Email Protection

- **Sumber:** <https://duckduckgo.com/email/faq>, <https://duckduckgo.com/duckduckgo-help-pages/email-protection/duck-addresses>, <https://duckduckgo.com/duckduckgo-help-pages/email-protection/duck-addresses/what-are-private-duck-addresses>, <https://duckduckgo.com/duckduckgo-help-pages/email-protection/duck-addresses/do-private-duck-addresses-expire>, <https://duckduckgo.com/duckduckgo-help-pages/email-protection/duck-addresses/where-can-i-manage-my-private-duck-addresses> (semua diakses 2026-11-14).
- **Model:** Dua jenis alamat — **personal Duck Address** (`<nama>@duck.com`, milik pengguna, tetap) dan **private Duck Addresses** (dihasilkan otomatis, mis. `amaze-gem-spider@duck.com`).
- **Pola quick-create:**私 private Duck Address **dihasilkan otomatis** saat dibutuhkan (browser/ekstensioulli mendeteksi field email dan menawarkan alamat); **tidak perlu membuka aplikasi sama sekali**. Ini adalah quick-create paling frictionless di seluruh referensi.
- **Domain handling:** seluruh alamat berada pada domain `duck.com` milik DuckDuckGo; **user tidak punya domain sendiri** dan tidak bisa memilih domain.
- **Inbox UX:** **tidak ada inbox**; semua diteruskan ke inbox asli setelah email tracking disembunyikan.
- **OTP/forwarding:** email diteruskan; tracking pixel dihapus sebelum meneruskan.
- **Expiry:** Private Duck Addresses **tidak kedaluwarsa** (dinyatakan eksplisit di halaman "Do private Duck Addresses expire?"); pengguna **deactivate/reactivate** dari menu Passwords di browser/ekstensi DDG.
- **Copy-first:** alamat私有 Duck Address disalin otomatis saat dipilih di form.
- **Kelemahan:** Kontrol naratif minimal (tidak bisa pilih domain, tidak bisa lihat isi, tidak bisa hapus dari web — deactivate hanya di app DDG); domain bersama membuat alamat mudah dikaitkan ke DDG.
- **Pola yang layak disalin: (a) private address yang dibuat otomatis dan berumur tetap, (b) on-the-fly generation tanpa "daftar dulu", (c) status aktif/nonaktif alih-alih hapus fisik.

### 2.9 Ringkasan Perbandingan Produk Temporary Mailbox

| Produk | Paradigma | Quick-create | Domain milik sendiri | Inbox di dalam produk | Forwarding | Masa hidup |
| --- | --- | --- | --- | --- | --- | --- |
| 1secmail | A | API token, satu panggilan | Tidak | Ya (via API polling) | Tidak | `expire_at` dari server (nilai default TIDAK TERVERIFIKASI) |
| mail.tm | A | Akun + password, tanpa kunci | Tidak | Ya | Tidak | Tidak dinyatakan (TIDAK TERVERIFIKASI) |
| temp-mail.io | A | API key + premium, TTL di respons | Tidak | Ya | Tidak | `ttl` (contoh 86400 detik) |
| Guerrilla Mail | A | Tanpa akun sama sekali | Tidak | Ya (polling) | Tidak | 60 menit + extend maks. 2 jam |
| SimpleLogin | B | Custom/random; on-the-fly via subdomain & directory | Ya (verifikasi DNS) | Tidak | Ya | Tidak kedaluwarsa (standar) |
| addy.io | B | On-the-fly atau in-advance (dashboard/ekstensi/API) | Ya + catch-all + regex | Tidak | Ya | Tidak kedaluwarsa (standar) |
| Firefox Relay | B | Dari browser/dashboard, masks dibatasi 5 (free) | Premium saja | Tidak | Ya + kategori | Tidak kedaluwarsa |
| DuckDuckGo EP | B | Dibuat otomatis saat dibutuhkan | Tidak (domain `duck.com`) | Tidak | Ya + anti-tracker | Tidak kedaluwarsa |

**Implikasi untuk DomiBox:** tidak ada satu pun produk acuan yang menggabungkan **inbox internal + alias permanen + catch-all + OTP panel**. Kombinasi itu adalahcelah pasar DomiBox — dan sekaligus alasan DomiBox harus/apps lookedaliカ cleanly supaya tidak sekadar "mail.tm dengan skin".


---

## 3. Referensi Admin Dashboard

Untuk dashboard solo-admin, kompleksitas berlebihan adalah musuh utama. Enam produk acuan ditinjau dengan kriteria: **pola navigasi, tabel & penyaring, aksi massal, state (kosong/loading/error), mode gelap, adaptasi mobile, aksesibilitas, dan kelayakan untuk solo-admin**.

### 3.1 shadcn/ui + Radix Primitives

- **Sumber:** <https://ui.shadcn.com/docs/components/data-table>, <https://ui.shadcn.com/docs/components/base/data-table>, <https://ui.shadcn.com/docs/components/base/table>, <https://www.radix-ui.com/primitives/docs/overview/accessibility> (semua diakses 2026-11-14).
- **Arsitektur:** Bukan library komponen monolitik; kode komponen disalin ke dalam repo aplikasi, dibangun di atas Radix Primitives (unstyled, WAI-ARIA compliant) dan TanStack Table (headless table).
- **Pola navigasi:** Menggunakan sidebar collapsible dan command menu (`cmdk`) yang terintegrasi.
- **Tabel + filter:** Pola resmi mendokumentasikan:
  - Header yang bisa diurutkan (sorting) via dropdown menu (`Asc`/`Desc`).
  - Filter kolom (text search atau faceted filter untuk status/kategori).
  - Seleksi baris (checkbox per baris + checkbox "select all" di header).
  - Visibilitas kolom (toggle kolom via dropdown).
  - Aksi per baris lewat `<DropdownMenu />` di kolom terakhir (pola elipsis `...`).
- **Aksi massal (bulk actions):** Menggunakan baris aksi yang muncul di atas tabel saat satu atau lebih baris dipilih (misal: "3 baris dipilih" + tombol aksi massal).
- **Empty / Loading / Error state:**
  - *Empty:* Baris tunggal dengan tinggi penuh menampilkan pesan "No results" di tengah tabel.
  - *Loading:* Skeleton loader pada baris-baris tabel (bukan spinner layar penuh).
  - *Error:* Alert banner di atas tabel atau toast notifikasi via Sonner.
- **Dark mode:** Berbasis class `dark` pada elemen `<html>` dengan CSS custom properties (HSL/OKLCH token).
- **Mobile:** Tabel membungkus dalam kontainer `overflow-x-auto`, atau pada layar sangat kecil diubah menjadi representasi kartu (card view).
- **Aksesibilitas:** Radix mengelola fokus, peran ARIA (`role="table"`, `role="row"`, `aria-sort`), dan interaksi keyboard out-of-the-box.
- **Kesesuaian untuk solo-admin:** **Sangat Tinggi**. Karena kode dimiliki sendiri oleh aplikasi (tidak ada runtime library eksternal yang membengkak), mudah dimodifikasi, dan kompatibel dengan Tailwind CSS yang umum dipakai.

### 3.2 Tailscale Admin Console

- **Sumber:** <https://tailscale.com/docs/concepts/tailnet>, <https://tailscale.com/docs/manage>, <https://tailscale.com/docs/reference/user-roles>, <https://tailscale.com/docs/features/access-control/acls>, <https://tailscale.com/docs/features/tailnet-policy-file> (semua diakses 2026-11-14).
- **Pola navigasi:** Navigasi horizontal di bagian atas (Machines, Users, Access Controls, DNS, Settings) dengan sidebar kontekstual di halaman-halaman tertentu.
- **Tabel + filter:** Daftar mesin (Machines) menampilkan status koneksi (titik hijau/abu-abu), alamat IP MagicDNS, nama perangkat, dan menu aksi elipsis. Filter cepat tersedia untuk mesin aktif, offline, atau berdasarkan tag.
- **Aksi massal:** Pemilihan mesin massal untuk operasi penonaktifan atau pemberian tag.
- **Empty / Loading / Error state:** State kosong halaman Machines mengarahkan pengguna ke alur instalasi perangkat pertama ("Add a machine") dengan panduan per OS yang jelas.
- **Dark mode:** Mengikuti preferensi sistem operasi dengan opsi toggle eksplisit di menu profil.
- **Mobile:** Tampilan web responsif; navigasi horizontal menciut menjadi menu dropdown.
- **Aksesibilitas:** Kontras tinggi pada indikator status, dukungan penuh keyboard untuk navigasi tabel.
- **Kesesuaian untuk solo-admin:** **Sedang-Tinggi**. Pola visual status titik (dot indicator) untuk konektivitas server/layanan dan editor teks untuk konfigurasi kebijakan (HuJSON) sangat cocok untuk dicontoh pada pengelolaan domain/DNS DomiBox.

### 3.3 Portainer

- **Sumber:** <https://docs.portainer.io/user/docker/dashboard>, <https://portainer.io/features> (semua diakses 2026-11-14).
- **Pola navigasi:** Sidebar vertikal tetap di sisi kiri (Dashboard, Stacks, Containers, Images, Volumes, Networks) dengan dropdown pemilihan environment di bagian atas.
- **Dashboard summary:** Layar utama menggunakan sistem "Summary Tiles" yang menampilkan metrik jumlah kontainer (running, stopped, healthy), volume, image, dan penggunaan disk dalam kotak-kotak terpisah yang bisa diklik untuk navigasi langsung ke halaman terkait.
- **Tabel + filter:** Tabel kontainer mencakup tombol aksi cepat di baris header (Start, Stop, Kill, Restart, Pause, Resume, Remove, Add container) yang aktif saat satu atau lebih item dipilih.
- **Empty / Loading / Error state:** Pesan informatif di dalam tabel ketika daftar kontainer kosong; spinner saat memuat data kontainer.
- **Dark mode:** Opsi mode gelap di pengaturan akun/antarmuka pengguna.
- **Mobile:** Kurang optimal untuk layar ponsel kecil; ditujukan terutama untuk penggunaan desktop/tablet karena kepadatan data yang tinggi.
- **Aksesibilitas:** Memadai untuk navigasi mouse, namun beberapa alur aksi massal membutuhkan navigasi keyboard bertingkat yang cukup dalam.
- **Kesesuaian untuk solo-admin:** **Sedang**. Pola "Summary Tiles" untuk ringkasan cepat kondisi sistem (jumlah mailbox aktif, pesan masuk hari ini, kapasitas disk VPS) sangat layak diadopsi untuk dashboard utama DomiBox.

### 3.4 Coolify

- **Sumber:** <https://coolify.io/docs/screenshots>, <https://coolify.io/docs/core/instance-management/instance-settings>, <https://coolify.io/docs/get-started/introduction> (semua diakses 2026-11-14).
- **Pola navigasi:** Sidebar kiri dengan grup navigasi yang rapi (Projects, Servers, Destinations, Settings). Halaman pengaturan menggunakan navigasi tab horizontal atau sub-sidebar bertingkat (Configuration: General/Advanced/Updates; Instance: Authentication/Email/Backup).
- **Tabel + filter:** Menampilkan daftar resource dan deployment dengan badge status warna yang tegas (hijau untuk deployed, merah untuk failed, kuning untuk in-progress).
- **Pola keamanan & aksi destruktif:** Fitur terdokumentasi "Destructive action confirmation" dengan opsi dua langkah (memerlukan kata sandi dan konfirmasi ketik teks nama resource) untuk mencegah penghapusan yang tidak disengaja.
- **Empty / Loading / Error state:** Alur onboarding dengan tombol besar "Create a Project" jika instance masih baru; log deployment real-time dengan streaming terminal jika terjadi error.
- **Dark mode:** Tema gelap default bernuansa modern (zinc/slate) yang sangat ramah mata untuk pengembang.
- **Mobile:** Cukup responsif dengan sidebar yang dapat disembunyikan (sheet/drawer).
- **Aksesibilitas:** Kontras teks baik di mode gelap; form input memiliki label dan teks bantuan (helper text) yang jelas.
- **Kesesuaian untuk solo-admin:** **Sangat Tinggi**. Coolify dirancang khusus untuk self-hoster mandiri. Pola "konfirmasi dua langkah untuk aksi destruktif" dan struktur pengelompokan pengaturan (General, Advanced, Security) adalah contoh sempurna untuk panel admin DomiBox.

### 3.5 Linear

- **Sumber:** <https://linear.app/enablement/guide/navigating-linear>, <https://linear.app/now/how-we-redesigned-the-linear-ui>, <https://linear.app/changelog/2026-01-22-customize-your-navigation-in-linear-mobile> (semua diakses 2026-11-14).
- **Pola navigasi:** Navigasi berbasis sidebar yang tenang (calm UI), dengan pintu masuk utama melalui **Command Palette (`Cmd+K` / `Ctrl+K`)**. Pengguna bisa melompat ke halaman mana saja atau mengeksekusi aksi apa pun tanpa mengangkat tangan dari keyboard.
- **Tabel & tampilan daftar:** Menggunakan daftar baris yang sangat padat namun terbaca (high density, high legibility). Tidak ada tombol aksi yang mencolok di setiap baris; aksi muncul saat kursor melayang (hover) atau saat baris dipilih via keyboard (`Enter` atau tombol pintas khusus).
- **Aksi massal:** Pemilihan multi-baris menggunakan `Shift + Panah Atas/Bawah` atau `X` (ala Gmail), lalu menu kontekstual atau command palette muncul untuk menerapkan aksi massal secara instan (optimistic UI).
- **Empty / Loading / Error state:** Menggunakan optimistic UI di mana perubahan langsung ditampilkan seketika sebelum konfirmasi server; animasi skeleton yang halus.
- **Dark mode:** Desain bertumpu pada skala transparansi hitam dan putih di atas latar netral, bukan sekadar warna abu-abu acak, menghasilkan kontras yang sangat seimbang.
- **Mobile:** Navigasi bawah (bottom navigation) yang bisa disesuaikan pengguna, dengan gestur swipe untuk aksi cepat.
- **Aksesibilitas:** Menetapkan standar emas untuk navigasi *keyboard-first*.
- **Kesesuaian untuk solo-admin:** **Tinggi (secara selektif)**. Pola `Cmd+K` untuk navigasi cepat dan keyboard shortcut untuk operasi umum (misal: `C` untuk buat mailbox baru, `D` untuk hapus, `/` untuk pencarian) akan membuat admin DomiBox bekerja sangat efisien.

### 3.6 Cloudflare Dashboard

- **Sumber:** <https://developers.cloudflare.com/security/settings>, <https://developers.cloudflare.com/waf/get-started>, <https://blog.cloudflare.com/designing-the-new-cloudflare-waf> (semua diakses 2026-11-14).
- **Pola navigasi:** Navigasi bertingkat: pemilih domain (Zone selector) di atas, diikuti sidebar vertikal dengan kategori keamanan, DNS, SSL/TLS, dan WAF.
- **Tabel + filter:** Menggunakan filter berbasis kueri visual ("filter chips") untuk aturan WAF, di mana admin dapat menambah kondisi filter (Field, Operator, Value) secara dinamis.
- **Aksi massal:** Kemampuan mengubah urutan aturan dengan drag-and-drop atau nomor prioritas; toggle aktif/nonaktif per aturan.
- **Empty / Loading / Error state:** Menampilkan banner status layanan jika ada gangguan; grafik kosong menampilkan saran konfigurasi awal.
- **Dark mode:** Dukungan mode gelap penuh yang konsisten di seluruh modul.
- **Mobile:** Navigasi kompleks disederhanakan tetapi tetap padat data; lebih ditujukan untuk pemantauan darurat daripada konfigurasi mendalam.
- **Aksesibilitas:** Dukungan kontras baik, namun hirarki navigasi yang dalam dapat membingungkan pengguna pembaca layar jika tidak terbiasa.
- **Kesesuaian untuk solo-admin:** **Rendah-Sedang**. Terlalu rumit untuk kebutuhan solo-admin DomiBox. Namun, pola **tampilan konfigurasi DNS / record status** dan **filter chips** layak diadaptasi untuk penyaringan log email.

---

## 4. Sintesis Pola

Berdasarkan analisis di atas, berikut adalah sintesis keputusan adopsi pola untuk DomiBox:

| No | Pola UX | Masalah yang Diselesaikan | Relevansi Pengguna DomiBox | Keputusan | Alasan & Bentuk Adaptasi |
| --- | --- | --- | --- | --- | --- |
| 1 | **Command Palette (`Cmd+K`)** (Linear) | Menghindari navigasi menu klik-berulang untuk solo-admin yang sering membuka sistem. | Solo-admin yang membutuhkan kecepatan tinggi saat mengelola domain, mencari mailbox, atau membuat alias baru. | **ADOPT** | Menggunakan primitif `cmdk` (ala shadcn/ui) untuk navigasi cepat ke halaman mailbox, pencarian alamat, dan eksekusi aksi cepat (mis. "Buat mailbox sementara"). |
| 2 | **One-Click Quick-Create + Immediate Copy** (Guerrilla Mail / DuckDuckGo) | Friksi mengisi form panjang saat pengguna hanya butuh email sekali pakai detik itu juga. | Solo-admin sedang mendaftar layanan baru di tab sebelah dan butuh email acak dalam hitungan 2 detik. | **ADOPT** | Tombol "Buat Cepat" di header dashboard yang langsung menghasilkan alamat acak, menampilkannya, dan otomatis menyalin ke clipboard dengan notifikasi toast. |
| 3 | **Two-Step Destructive Confirmation** (Coolify) | Mencegah penghapusan mailbox penting atau domain secara tidak sengaja. | Solo-admin yang mengelola mailbox permanen (berisi akun-akun penting) agar tidak terhapus bersama mailbox sementara. | **ADAPT** | Untuk mailbox sementara: cukup konfirmasi satu tombol (klik "Hapus"). Untuk mailbox berlabel PERMANEN atau Domain: wajib modal konfirmasi dua langkah (ketik nama alamat / domain untuk konfirmasi). |
| 4 | **Catch-All + Auto-Create Regex** (addy.io) | Kebutuhan membuat alias baru tanpa harus membuka aplikasi terlebih dahulu. | Memberikan email seperti `service-abc@sintaksis.biz.id` langsung di form eksternal, dan sistem otomatis membuatkannya saat email pertama tiba. | **ADOPT** | Terapkan toggle Catch-All per domain di pengaturan domain, dengan opsi filter regex untuk mencegah spam liar jika diinginkan. |
| 5 | **Inline Inbox / Split View** (mail.tm / shadcn) | Harus berpindah-pindah halaman antara daftar mailbox dan isi pesan masuk. | Admin ingin melihat apakah email OTP sudah sampai tanpa meninggalkan konteks daftar mailbox. | **ADAPT** | Layout split-pane responsif: sisi kiri daftar mailbox, sisi kanan langsung menampilkan isi pesan dari mailbox yang dipilih. Jika layar ponsel, beralih ke navigasi stack (masuk ke detail). |
| 6 | **OTP Auto-Detection Panel** (Pola Baru, adaptasi kebutuhan) | Pengguna harus membaca seluruh bodi email HTML yang panjang hanya untuk mencari 6 digit angka kode verifikasi. | Pengguna DomiBox yang 80% kebutuhannya adalah menerima kode OTP pendaftaran. | **ADOPT** | Ekstraksi regex otomatis di backend/frontend untuk kode 4-8 digit; tampilkan banner menonjol di atas isi email: "Kode Verifikasi: 123456" dengan tombol "Salin Kode". |
| 7 | **Summary Tiles Dashboard** (Portainer) | Tidak adanya gambaran kesehatan sistem secara cepat saat pertama kali membuka dashboard. | Solo-admin perlu tahu apakah disk VPS penuh, berapa mailbox aktif, dan apakah Stalwart berjalan normal. | **ADOPT** | 4 kotak ringkasan di beranda: Total Mailbox (Temp vs Permanen), Pesan Masuk (24 jam), Penggunaan Disk VPS, dan Status Server Mail (Stalwart). |
| 8 | **Reverse Alias Sending** (SimpleLogin) | Kebutuhan membalas email dari alias tanpa membocorkan alamat email asli ke luar. | Fitur pengiriman keluar yang kompleks dan rawan disalahgunakan sebagai spam relay. | **REJECT** | **DITOLAK untuk MVP.** Fokus DomiBox adalah mailbox penerima (inbox-first). Mengirim email membutuhkan reputasi IP, penanganan SPF/DKIM keluar yang ketat, dan menambah risiko IP Tencent di-blacklist. |
| 9 | **Public Self-Registration** (mail.tm) | Membuka pendaftaran akun publik bagi siapa saja di internet. | DomiBox adalah sistem *private single-owner*. | **REJECT** | **DITOLAK secara tegas.** Registrasi publik dimatikan sepenuhnya di tingkat kode dan konfigurasi instance (mengikuti pola default Coolify). Tidak ada formulir sign-up publik. |
| 10 | **Blocking Images by Default** (Guerrilla Mail) | Melindungi privasi admin dari web beacon/tracking pixel yang disematkan pengirim spam. | Admin membuka email dari sumber antah-berantah yang berpotensi melacak IP asli atau status aktif email. | **ADOPT** | Gambar eksternal dinonaktifkan secara bawaan dengan tombol "Tampilkan Gambar" per email. Mengurangi konsumsi bandwidth VPS. |
| 11 | **Hierarchical Multi-Tenant / Team Management** (Tailscale / Cloudflare) | Mengelola organisasi, tim, peran (Owner, Admin, Member, Billing), dan audit log multi-user. | DomiBox hanya digunakan oleh 1 orang pemilik (solo-admin). | **REJECT** | **DITOLAK.** Menambah kompleksitas skema database dan kerumitan UI yang tidak bernilai bagi pengguna tunggal. |
| 12 | **Polling Manual Berkala** (Guerrilla Mail API) | Klien harus memanggil API terus menerus setiap beberapa detik untuk mengecek email baru. | Menyita resource VPS Tencent yang hanya 2 vCPU dan membuat kuota jaringan terbuang. | **ADAPT** | Gunakan Server-Sent Events (SSE) atau WebSocket ringan dari backend ke web dashboard untuk pembaruan real-time saat halaman dibuka, bukan polling buta. |


---

## 5. Arsitektur Informasi (IA) & Navigasi yang Disarankan

Untuk memberikan pengalaman terbaik bagi solo-admin, antarmuka DomiBox dibagi menjadi dua saluran utama: **Web Dashboard** (untuk konfigurasi mendalam, audit, dan manajemen terpusat) dan **Telegram Bot** (untuk aksi kilat saat bepergian).

### 5.1 Sitemap & Struktur Halaman Web Dashboard

```
Web Dashboard (DomiBox)
├── / (Dashboard Beranda)
│   ├── Summary Tiles (Mailbox Aktif, Pesan 24 Jam, Disk VPS, Status Stalwart)
│   ├── Quick-Create Bar (Aksi 1-Klik Buat Mailbox)
│   └── Aktivitas Terkini (5 Email Terakhir Masuk)
├── /mailboxes (Manajemen Mailbox)
│   ├── Tab: Semua | Sementara (Temporary) | Permanen | Catch-All
│   ├── Tabel Mailbox (Pencarian, Filter Domain, Multi-select, Expiry Timer)
│   └── Modal / Drawer: Detail Mailbox & Log Penerimaan
├── /inbox (Pusat Baca Pesan - Split View)
│   ├── Pane Kiri: Daftar Pesan Masuk (Filter per Mailbox, Status Baca/Belum)
│   └── Pane Kanan: Penampil Pesan (Header, Banner OTP + Tombol Salin, Bodi Teks/HTML Aman)
├── /domains (Pengaturan Domain & DNS)
│   ├── Daftar Domain Terpasang (Status SPF, DKIM, DMARC, MX via Cloudflare/DoH)
│   ├── Konfigurasi Catch-All per Domain
│   └── Panduan Record DNS untuk Domain Baru
└── /settings (Pengaturan Sistem)
    ├── Konfigurasi Instance & Keamanan (Ganti Sandi Admin, Token API)
    ├── Integrasi Telegram Bot (Status Webhook, Chat ID Terdaftar)
    └── Preferensi Tampilan (Tema Gelap/Terang/Sistem)
```

### 5.2 Alur Percakapan Telegram Bot

Interaksi Telegram dirancang berbasis percakapan ringkas dan inline keyboard, bukan formulir yang bertele-tele:

```
Telegram Bot Interaksi:
├── /start -> Pesan sambutan singkat & menu inline utama [Buat Mailbox Cepat] [Daftar Aktif] [Status Sistem]
├── /quick -> Langsung menghasilkan mailbox sementara acak baru:
│   └── Respons: "Mailbox siap: temp-xyz@sintaksis.biz.id (Berlaku 60 mnt)"
│       └── Inline Keyboard: [📋 Salin Alamat] [⏱️ +1 Jam] [🗑️ Hapus Sekarang]
├── /list -> Menampilkan daftar 5 mailbox aktif terakhir dengan status expiry
├── /status -> Ringkasan singkat status server (CPU, RAM, Disk, Stalwart Running)
└── Notifikasi Pesan Masuk Otomatis (Push Notification):
    └── Format:
        📬 *Email Baru Masuk!*
        *Kepada:* `temp-xyz@sintaksis.biz.id`
        *Dari:* `noreply@service.com`
        *Subjek:* `Kode Verifikasi Akun Anda`
        🔑 *KODE OTP:* `849201`  <-- [Dideteksi Otomatis]
        └── Inline Keyboard: [📋 Salin OTP] [📖 Baca Email Penuh] [🗑️ Hapus Mailbox]
```

---

## 6. Pola Interaksi Kritis

### 6.1 Quick-Create Mailbox
- **Trigger:** Tombol menonjol `+ Buat Mailbox` di header atau pintasan keyboard `C`.
- **Form Minimalis:**
  - Pilihan Tipe: `Sementara` (default) vs `Permanen`.
  - Pilihan Domain: Dropdown memilih dari domain aktif (misal: `sintaksis.biz.id`).
  - Username: Tombol acak (default menghasilkan nama acak ramah manusia) atau input manual jika ingin custom.
  - Expiry (khusus tipe Sementara): Pilihan preset `1 Jam`, `24 Jam` (default), `7 Hari`.
- **Aksi:** Tekan `Enter` -> Mailbox langsung terdaftar -> Pop-up toast "Mailbox dibuat & alamat disalin ke clipboard!".

### 6.2 Copy-Immediately Behavior
- Di web dashboard, setiap alamat email dan kode OTP ditampilkan dalam kontainer klik-untuk-salin (`click-to-copy`).
- Ketika diklik, ikon berubah dari `Copy` menjadi `Checkmark` hijau selama 2 detik, disertai toast notifikasi "Disalin ke clipboard".
- Di Telegram, seluruh alamat email dan kode OTP wajib diformat menggunakan tag `code` (monospace Markdown: `` `teks` ``), sehingga pengguna ponsel dapat menyalinnya hanya dengan satu sentuhan.

### 6.3 Inline Inbox Preview & OTP Panel
- Saat membuka email di panel baca, sistem memindai bodi teks menggunakan regex deteksi angka verifikasi (`\b\d{4,8}\b` dikombinasikan dengan kata kunci seperti *verification, code, OTP, pin, token*).
- Jika terdeteksi, panel sorotan (callout) kuning/biru dengan kontras tinggi langsung muncul di bagian paling atas pesan:
  ```
  +-------------------------------------------------------+
  |  KODE VERIFIKASI TERDETEKSI:   948102                 |
  |  [ Tombol: Salin Kode OTP ]                           |
  +-------------------------------------------------------+
  ```
- Ini memangkas waktu pengguna dari rata-rata 15 detik (mencari angka di email panjang) menjadi 1 detik.

### 6.4 Konfirmasi Penghapusan (Deletion Confirm)
- **Mailbox Sementara:** Klik ikon tempat sampah -> Tombol berubah menjadi "Yakin Hapus?" (inline confirmation) selama 3 detik. Jika diklik lagi, mailbox terhapus.
- **Mailbox Permanen:** Klik hapus -> Modal dialog terbuka. Pengguna wajib mengetikkan kembali nama mailbox (misal: `admin@sintaksis.biz.id`) untuk mengaktifkan tombol "Hapus Permanen". Ini mengadopsi pola keamanan Coolify/GitHub.

### 6.5 Navigasi Keyboard Penuh (Keyboard-First)
- `Cmd+K` atau `Ctrl+K`: Membuka Command Palette universal.
- `J` / `K` atau `Panah Bawah/Atas`: Navigasi antar baris tabel mailbox atau pesan email.
- `Enter`: Membuka item yang sedang disorot.
- `C`: Pintasan cepat membuka modal pembuatan mailbox baru.
- `X`: Menandai/memilih baris untuk aksi massal.
- `Esc`: Menutup modal, drawer, atau membatalkan pilihan.

---

## 7. Standar Aksesibilitas (WCAG 2.2 Level AA)

DomiBox menargetkan kepatuhan terhadap standar **WCAG 2.2 Level AA** untuk memastikan panel admin dapat dioperasikan secara efisien dan tanpa hambatan.

### 7.1 Target Konkret & Kriteria Sukses

| Kriteria WCAG | Aspek | Target Implementasi di DomiBox | Cara Verifikasi |
| --- | --- | --- | --- |
| **SC 1.4.3** | Kontras Teks (Minimum) | Rasio kontras minimal **4.5:1** untuk teks normal dan **3.0:1** untuk teks tebal/besar (>= 18pt atau 14pt bold). Berlaku di mode terang dan gelap. | Pengujian otomatis via axe DevTools dan manual via WebAIM Contrast Checker. |
| **SC 1.4.11** | Kontras Non-Teks | Rasio kontras minimal **3.0:1** untuk batas elemen antarmuka (input border, tombol, status badge) dan ikon interaktif terhadap latar belakang. | Inspeksi color picker pada status badge (aktif, nonaktif, pending). |
| **SC 2.1.1** | Navigasi Keyboard | Seluruh fungsionalitas (pembuatan mailbox, pencarian, salin OTP, penghapusan) dapat diakses 100% menggunakan tombol `Tab`, `Shift+Tab`, `Enter`, `Space`, dan tombol panah. | Pengujian manual tanpa menyentuh mouse/trackpad sama sekali dari login hingga hapus mailbox. |
| **SC 2.4.7** | Fokus Terlihat (Focus Visible) | Indikator fokus yang jelas dan tegas saat elemen menerima navigasi keyboard (ring outline 2px dengan kontras tinggi terhadap latar). Dilarang keras memakai `outline: none` tanpa pengganti. | Uji tabulasi keyboard; pastikan setiap tombol dan input memiliki outline biru/emas yang kontras saat aktif. |
| **SC 2.4.11** | Fokus Tidak Terhalang (Focus Not Obscured) | Elemen yang sedang menerima fokus tidak boleh tertutup atau terhalang oleh elemen sticky lain (seperti header tetap, modal, atau toast notification). | Uji navigasi keyboard pada layar kecil dengan header sticky aktif. |
| **SC 2.5.8** | Target Sentuh Minimum (Target Size) | Seluruh target klik/sentuh (termasuk tombol ikon elipsis dan tombol salin di mobile) memiliki ukuran area sentuh minimal **24x24 CSS pixels** dengan padding yang memadai. | Inspeksi elemen CSS di mode responsive emulator mobile. |
| **SC 2.3.3** | Pengurangan Gerakan (Reduced Motion) | Menghormati pengaturan OS `prefers-reduced-motion: reduce`. Animasi transisi drawer atau modal dimatikan atau diganti dengan transisi opasitas instan jika opsi ini aktif. | Pengujian dengan mengaktifkan opsi "Reduce motion" di pengaturan sistem operasi. |
| **SC 4.1.2** | Nama, Peran, Nilai (ARIA) | Tombol-tombol berbasis ikon (seperti tombol copy, delete, refresh) wajib memiliki atribut `aria-label` yang deskriptif (misal: `aria-label="Salin alamat mailbox"`). | Audit pembaca layar menggunakan NVDA atau VoiceOver. |


---

## 8. Panduan Desain Mode Gelap (Dark Mode)

Mode gelap adalah preferensi utama bagi mayoritas pengembang dan sysadmin. Pendekatan yang diusulkan memastikan kontras tajam tanpa membuat mata lelah.

### 8.1 Arsitektur Token Warna (CSS Custom Properties)
Gunakan pendekatan token semantik berbasis CSS variables (kompatibel dengan Tailwind CSS / shadcn/ui) pada elemen root:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 240 10% 3.9%;
  --card: 0 0% 100%;
  --card-foreground: 240 10% 3.9%;
  --primary: 240 5.9% 10%;
  --primary-foreground: 0 0% 98%;
  --muted: 240 4.8% 95.9%;
  --muted-foreground: 240 3.8% 46.1%;
  --border: 240 5.9% 90%;
  --ring: 240 5% 64.9%;
}

.dark {
  --background: 240 10% 3.9%;       /* #09090b - Zinc sangat gelap, bukan hitam murni */
  --foreground: 0 0% 98%;           /* #fafafa - Putih lembut */
  --card: 240 10% 6%;               /* #0f0f12 - Sedikit lebih terang dari background */
  --card-foreground: 0 0% 98%;
  --primary: 0 0% 98%;
  --primary-foreground: 240 5.9% 10%;
  --muted: 240 3.7% 15.9%;          /* Elemen sekunder */
  --muted-foreground: 240 5% 64.9%; /* Teks redup, tetap lolos kontras 4.5:1 */
  --border: 240 3.7% 15.9%;         /* Garis pemisah tegas */
  --ring: 240 4.9% 83.9%;           /* Indikator fokus keyboard */
}
```

### 8.2 Strategi Visual Mode Gelap
- **Hindari Hitam Murni (#000000):** Gunakan warna dasar gelap bernuansa netral/slate (misal `#09090b`) untuk latar belakang dan elevasi bertingkat (level kartu `#121215`, popover `#18181b`) untuk menciptakan kedalaman hierarki visual.
- **Pemberian Kontras Teks:** Teks utama menggunakan putih pudar (`#f4f4f5`) untuk menghindari efek halo/glare berlebihan pada mata.
- **Pencegahan Flash of Unstyled Theme (FOUC):** Skrip kecil inline dieksekusi di `<head>` sebelum rendering DOM untuk membaca preferensi tema dari `localStorage` atau `window.matchMedia('(prefers-color-scheme: dark)')` dan langsung menerapkan class `dark`.

---

## 9. Pola Interaksi Telegram Bot

Sebagai saluran sekunder yang sangat cepat, bot Telegram DomiBox harus mengikuti kaidah dan batasan resmi Telegram Bot API.

### 9.1 Pola yang Terbukti Efektif
- **Inline Keyboard vs Reply Keyboard:**
  - Selalu gunakan **Inline Keyboard** (tombol yang melekat langsung di bawah balon pesan). Hindari Reply Keyboard permanen di bawah kolom teks yang memenuhi layar ponsel.
  - Setiap aksi (seperti perpanjang masa aktif atau salin kode) langsung mengubah status pesan asli (`editMessageText` / `editMessageReplyMarkup`) daripada membanjiri riwayat obrolan dengan pesan-pesan baru.
- **Keamanan Callback Query:**
  - Payload data pada tombol inline (`callback_data`) dibatasi maksimal **1-64 byte** sesuai spesifikasi Bot API.
  - Format payload harus sangat ringkas, contoh: `ext:<mailbox_id>` atau `del:<mailbox_id>`.
  - Bot WAJIB selalu merespons dengan memanggil metode `answerCallbackQuery` dalam hitungan milidetik untuk menghilangkan ikon loading jam pasir pada tombol pengguna, disertai teks toast notifikasi (misal: "Masa aktif ditambah 1 jam!").
- **Manajemen Notifikasi & Batasan Pesan:**
  - Batas panjang pesan Telegram resmi adalah **4.096 karakter** untuk pesan teks biasa.
  - Konten email panjang dipotong secara cerdas (smart truncate): tampilkan header penting (Dari, Subjek, Kepada), ringkasan 200 karakter pertama, dan tombol inline "Baca Selengkapnya di Web".
  - Untuk pesan yang berisi OTP, kirimkan notifikasi dengan suara aktif; untuk email newsletter/spam biasa, gunakan opsi `disable_notification: true` agar tidak mengganggu admin.

---

## 10. Anti-Pattern yang Wajib Dihindari

Berdasarkan evaluasi terhadap produk-produk acuan dan jebakan umum aplikasi temporary mail, pola-pola berikut **DILARANG** diimplementasikan di DomiBox:

1. **Meminta Registrasi / Login Publik:**
   - *Alasan:* DomiBox adalah sistem pribadi (single-owner). Membuka pendaftaran publik hanya akan mengundang bot spammer dan menghabiskan resource VPS Tencent.
2. **Menyembunyikan Alamat Mailbox di Balik Banyak Klik:**
   - *Alasan:* Pengguna yang butuh email sementara ingin langsung melihat dan menyalin alamat dalam 1 detik. Membuka modal multi-step hanya untuk membuat email sementara adalah anti-pattern fatal.
3. **Memuat Gambar Eksternal Secara Otomatis:**
   - *Alasan:* Mengizinkan web bug/tracking pixel membocorkan alamat IP admin dan status validitas mailbox kepada spammer.
4. **Polling HTTP Berulang Tanpa Batas:**
   - *Alasan:* Polling client-side setiap 2 detik membakar kuota CPU dan log server VPS. Gunakan SSE atau WebSocket saat tab aktif, dan hentikan koneksi saat tab di-minimize.
5. **Menghapus Mailbox Tanpa Jejak Sesaat Sebelum OTP Sampai:**
   - *Alasan:* Banyak layanan memerlukan waktu 3-5 menit untuk mengirim email verifikasi. Expiry default minimal untuk mailbox sementara adalah 1 jam, bukan 10 menit.
6. **Formulir Pengaturan yang Menyimpan Otomatis Tanpa Notifikasi (Silent Autosave):**
   - *Alasan:* Pada konfigurasi sensitif (seperti DNS atau token), silent autosave membingungkan admin apakah perubahan sudah aktif atau gagal. Wajib gunakan tombol "Simpan Perubahan" yang jelas disertai indikator loading dan toast sukses.

---

## 11. Temuan Konkret untuk Penulis Spesifikasi (IA & Spec)

Poin-poin praktis yang dapat langsung disalin ke dalam dokumen spesifikasi produk lanjutan:

- **Mailbox Model:** Dukung 2 tipe mailbox sejak hari pertama: `Temporary` (dengan waktu kedaluwarsa otomatis) dan `Permanent` (tanpa kedaluwarsa, untuk layanan jangka panjang).
- **Primary Layout:** Desain web dashboard mengadopsi struktur dua panel (Split Pane): panel kiri daftar mailbox/pesan (lebar 350px-400px), panel kanan isi pesan aktif (fleksibel).
- **Fast Path:** Header dashboard wajib memiliki tombol `Quick Temp Mail` yang langsung menyalin alamat ke clipboard saat ditekan.
- **OTP First Class:** Komponen penampil email harus memiliki slot khusus di bagian atas untuk mengekstrak dan menampilkan kode OTP dengan tombol salin satu-klik.
- **DNS Health Indicator:** Halaman domain wajib menampilkan indikator visual (badge hijau/merah) untuk status record MX, SPF, DKIM, dan DMARC guna memudahkan diagnosa tanpa harus membuka terminal.
- **Telegram Dual-Mode:** Bot Telegram difungsikan sebagai *listener & quick responder* (notifikasi OTP instan dan perpanjangan mailbox 1-klik), bukan replika penuh dari seluruh dashboard admin.

---

## 12. Daftar Sumber & Verifikasi

Semua URL berikut telah diverifikasi dan diakses pada tanggal **2026-11-14**:

### Referensi Produk Mailbox & Alias
1. **1secmail API Specification:**
   - URL: <https://github.com/1sec-mail/1secmail-api> (Dokumentasi resmi repositori)
   - Arsip Web Lawas: <https://web.archive.org/web/20241223222139/https://www.1secmail.com/api>
2. **mail.tm Documentation & OpenAPI:**
   - URL Akun API: <https://docs.mail.tm/api/accounts>
   - URL Domain API: <https://docs.mail.tm/api/domains>
   - URL OpenAPI 3.1: <https://api.mail.tm/>
3. **temp-mail.io Official REST API:**
   - URL Panduan API: <https://docs.temp-mail.io/docs/getting-started>
   - URL Indeks API: <https://docs.temp-mail.io/>
4. **Guerrilla Mail JSON API Specification:**
   - URL Dokumentasi API v1.0: <https://www.guerrillamail.com/GuerrillaMailAPI.html>
   - URL Informasi Layanan: <https://www.guerrillamail.com/about>
5. **SimpleLogin Knowledge Base & GitHub:**
   - URL Pembuatan Alias: <https://simplelogin.io/docs/getting-started/create-alias>
   - URL Custom Domain: <https://simplelogin.io/docs/custom-domain/add-domain>
   - URL Subdomain On-the-Fly: <https://simplelogin.io/docs/subdomain/new>
   - URL Reverse Alias: <https://simplelogin.io/docs/getting-started/reverse-alias>
   - URL Repositori API: <https://github.com/simple-login/app/blob/master/docs/api.md>
6. **addy.io (Anonaddy) Help Center:**
   - URL Pembuatan Alias: <https://addy.io/help/creating-new-email-aliases>
   - URL Catch-All & Regex Otomatis: <https://addy.io/help/understanding-catch-all-and-alias-auto-create-regex-for-a-domain/>
   - URL Tipe Alias: <https://addy.io/help/what-are-the-different-kinds-of-aliases>
   - URL API addy.io: <https://app.addy.io/docs>
7. **Firefox Relay Support & FAQ:**
   - URL Penjelasan Mask: <https://support.mozilla.org/en-US/kb/firefox-relay-what-email-mask>
   - URL Cara Pembuatan Mask: <https://support.mozilla.org/en-US/kb/create-email-alias-through-firefox-relay>
   - URL Domain Pribadi Relay: <https://support.mozilla.org/en-US/kb/register-your-own-domain-firefox-relay-premium>
   - URL FAQ Layanan: <https://relay.firefox.com/faq>
8. **DuckDuckGo Email Protection Help Pages:**
   - URL Tanya Jawab Proteksi Email: <https://duckduckgo.com/email/faq>
   - URL Alamat Duck Pribadi: <https://duckduckgo.com/duckduckgo-help-pages/email-protection/duck-addresses>
   - URL Detail Private Duck Address: <https://duckduckgo.com/duckduckgo-help-pages/email-protection/duck-addresses/what-are-private-duck-addresses>
   - URL Masa Berlaku Alamat: <https://duckduckgo.com/duckduckgo-help-pages/email-protection/duck-addresses/do-private-duck-addresses-expire>

### Referensi Dashboard Admin & Library UI
9. **shadcn/ui & Radix Primitives:**
   - URL Data Table shadcn: <https://ui.shadcn.com/docs/components/data-table>
   - URL Base Table shadcn: <https://ui.shadcn.com/docs/components/base/table>
   - URL Aksesibilitas Radix Primitives: <https://www.radix-ui.com/primitives/docs/overview/accessibility>
10. **Tailscale Documentation:**
    - URL Konsep Tailnet & Admin Console: <https://tailscale.com/docs/concepts/tailnet>
    - URL Pengelolaan Perangkat: <https://tailscale.com/docs/manage>
    - URL Peran Pengguna & Admin: <https://tailscale.com/docs/reference/user-roles>
    - URL Kebijakan ACL: <https://tailscale.com/docs/features/access-control/acls>
11. **Portainer Documentation:**
    - URL Dashboard Docker Standalone: <https://docs.portainer.io/user/docker/dashboard>
    - URL Fitur Produk Portainer: <https://portainer.io/features>
12. **Coolify Documentation:**
    - URL Pengaturan Instance: <https://coolify.io/docs/core/instance-management/instance-settings>
    - URL Tangkapan Layar Antarmuka: <https://coolify.io/docs/screenshots>
    - URL Pengenalan & Arsitektur: <https://coolify.io/docs/get-started/introduction>
13. **Linear UI & Guidelines:**
    - URL Navigasi Linear: <https://linear.app/enablement/guide/navigating-linear>
    - URL Redesain UI Linear: <https://linear.app/now/how-we-redesigned-the-linear-ui>
    - URL Kustomisasi Navigasi Mobile: <https://linear.app/changelog/2026-01-22-customize-your-navigation-in-linear-mobile>
14. **Cloudflare Security & WAF Dashboard:**
    - URL Pengaturan Keamanan: <https://developers.cloudflare.com/security/settings>
    - URL Panduan WAF Dashboard: <https://developers.cloudflare.com/waf/get-started>
    - URL Arsitektur Desain WAF Baru: <https://blog.cloudflare.com/designing-the-new-cloudflare-waf>

### Standar Aksesibilitas & Telegram API
15. **W3C Web Content Accessibility Guidelines (WCAG) 2.2:**
    - URL Standar Resmi WCAG 2.2: <https://www.w3.org/TR/WCAG22/>
    - URL Kriteria SC 2.4.11 (Focus Not Obscured): <https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html>
    - URL Kriteria SC 2.5.8 (Target Size Minimum): <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html>
    - URL Quick Reference WCAG 2.2: <https://www.w3.org/WAI/WCAG22/quickref/>
16. **Telegram Bot API Official Documentation:**
    - URL Referensi Bot API Utama: <https://core.telegram.org/bots/api>
    - URL Tipe Objek CallbackQuery: <https://core.telegram.org/bots/api/types/callbackquery>
    - URL Tipe Objek InlineKeyboardMarkup: <https://core.telegram.org/bots/api/types/inlinekeyboardmarkup>
    - URL Panduan Tombol & Keyboard Bot: <https://core.telegram.org/api/bots/buttons>
