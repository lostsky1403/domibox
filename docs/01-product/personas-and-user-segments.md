# Personas & User Segments — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-14 | omp-orchestrator/ProductDocs | `docs/00-governance/project-charter.md`<br>`docs/01-product/product-vision.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/01-product/stakeholder-map.md`<br>`docs/09-research/ux-pattern-benchmark.md` |

---

## 1. Tujuan & Pendekatan Segmentasi (Purpose & Methodology)

Dokumen ini mendefinisikan persona pengguna arketipal (*archetypal personas*) dan segmentasi pengguna untuk platform **DomiBox**. Segmentasi mencakup spektrum pengguna dari kebutuhan mailbox sementara (*disposable mail*), mailbox permanen (*persistent aliases*), peran administrator sistem (*single-owner/sysadmin*), hingga operator penanganan penyalahgunaan (*abuse-ops*).

Sesuai dengan `docs/00-governance/documentation-standards.md`, persona ini disusun berdasarkan **analisis kebutuhan teknis dan pola perilaku yang diobservasi (*evidence-labeled: ASSUMPTION / PROPOSED*)**, mengingat riset primer kuantitatif pengguna belum dilakukan secara langsung (merujuk pada celah riset `Q-001` dalam `docs/09-research/problem-value-research.md`).

---

## 2. Matriks Segmentasi Pengguna (User Segmentation Matrix)

| Segmen Pengguna | Kebutuhan Utama | Saluran Interaksi Utama | Frekuensi Penggunaan | Tingkat Literasi Teknis | Status Bukti Segmen |
| --- | --- | --- | --- | --- | --- |
| **SEG-1: Developer & QA Engineer** | Uji coba pendaftaran aplikasi, pengujian alur verifikasi email otomatis, ekstraksi cepat OTP saat testing. | Web Dashboard, REST API (Fase 2), Telegram Bot | Sangat Sering (Harian / Tiap Sesi Uji) | Tinggi (Advanced) | `PROPOSED` |
| **SEG-2: Privacy-Conscious Power User** | Registrasi forum/buletin/SaaS baru tanpa mengekspos email utama; pemantauan kebocoran data. | Telegram Bot (Notifikasi Instan), Web Dashboard | Berkala (Beberapa kali per minggu) | Menengah ke Tinggi | `ASSUMPTION` |
| **SEG-3: Single-Owner & Platform Admin** | Manajemen domain DNS, pemantauan log SMTP inbound, alokasi kuota, audit keamanan dan rotasi rahasia. | Web Dashboard (Admin Panel), SSH Console, Docker CLI | Harian hingga Mingguan | Sangat Tinggi (Sysadmin / DevOps) | `VERIFIED` (Struktur Kepemilikan Privat) |
| **SEG-4: Abuse & Security Operator** | Penanganan bounce email, mitigasi serangan flood/spam inbound, peninjauan log penolakan pesan (`RCPT TO reject`). | Log Viewer, Alerting Channel, Web Dashboard | Insidental (Saat Anomali / Audit) | Sangat Tinggi (SecOps) | `PROPOSED` |

---

## 3. Profil Persona Detail (Detailed User Personas)

---

### 3.1 Persona 1: "Dev Dedi" — The Agile QA & Backend Engineer
*Representasi Segmen: SEG-1 (Developer & QA)*

- **Profil Demografis (Arketipe):** Pria, 28 tahun, Software Engineer / QA Automation.
- **Tingkat Keterampilan Teknis:** Mampu mengoperasikan API, curl, Git, dan Telegram Bot.
- **Kutipan Utama:** *"Saya hanya butuh alamat email yang pasti tembus filter pendaftaran, menerima email verifikasi dalam 3 detik, dan menampilkan kodenya tanpa harus bolak-balik buka webmail berat."*
- **Tujuan Utama (Goals):**
  1. Menghasilkan alamat email sementara dalam 1 klik sebelum form registrasi timeout.
  2. Menyalin kode OTP 6-digit langsung dari notifikasi pop-up atau chat Telegram.
  3. Menguji alur registrasi multi-akun tanpa harus membuat puluhan akun Google/Outlook manual.
- **Frustrasi Utama (Pains):**
  - Layanan temp-mail publik (temp-mail.org, 1secmail) diblokir oleh sistem anti-bot AWS/Cloudflare/Google.
  - Alamat email publik bisa diintip orang lain jika formatnya mudah ditebak.
  - Membuka webmail standar (Gmail/Roundcube) memakan waktu dan mengacaukan inbox pribadi dengan pesan uji coba sampah.
- **Perilaku Penggunaan DomiBox:**
  - Menghubungkan bot Telegram DomiBox (`BOT-001`).
  - Mengetik `/new` di Telegram atau menekan tombol "Generate Mailbox" di dashboard web (`WEB-001`).
  - Mengandalkan tombol "Copy OTP" instan di Telegram inline keyboard.
- **Status Bukti:** `PROPOSED` (Berdasarkan analisis alur uji perangkat lunak umum).

---

### 3.2 Persona 2: "Rina Privasi" — The Digital Nomad & Privacy Advocate
*Representasi Segmen: SEG-2 (Privacy-Conscious Power User)*

- **Profil Demografis (Arketipe):** Wanita, 32 tahun, Konsultan Digital & Peneliti Independen.
- **Tingkat Keterampilan Teknis:** Menengah; paham konsep domain pribadi, DNS dasar, dan proteksi jejak digital.
- **Kutipan Utama:** *"Saya ingin domain pribadi saya bisa dipakai untuk membuat alamat email khusus per layanan, tapi saya tidak mau data saya dibaca oleh penyedia email komersial besar."*
- **Tujuan Utama (Goals):**
  1. Mendaftar ke buletin dan forum daring dengan alamat khusus (misal: `techforum@sintaksis.biz.id`).
  2. Mencegah korelasi data (*cross-site profiling*) antar layanan internet.
  3. Memiliki opsi mengubah alamat sementara menjadi permanen jika layanan tersebut ternyata penting untuk jangka panjang.
- **Frustrasi Utama (Pains):**
  - Biaya langganan SimpleLogin / addy.io untuk domain kustom.
  - Ketakutan "disposable mail trap", di mana akun penting terkunci karena alamat sementara kedaluwarsa tanpa bisa diperpanjang.
  - Pelacakan pixel (*tracking pixels*) di dalam email promosi yang mendeteksi lokasi dan perangkatnya.
- **Perilaku Penggunaan DomiBox:**
  - Menggunakan Web Dashboard untuk membuat mailbox dengan TTL panjang (misal: 7 hari atau permanen) (`MBX-001`, `MBX-002`).
  - Mengaktifkan fitur sanitasi HTML DomiBox yang menonaktifkan rendering gambar eksternal dan tracking beacon (`SEC-005`).
- **Status Bukti:** `ASSUMPTION` (Menunggu pengayaan riset masalah `Q-001`).

---

### 3.3 Persona 3: "Budi Sysadmin" — The Single-Owner & Self-Host Enthusiast
*Representasi Segmen: SEG-3 (Platform Owner & Administrator)*

- **Profil Demografis (Arketipe):** Pria, 35 tahun, DevOps / Homelab Owner. Pemilik sah VPS Tencent Cloud dan domain `sintaksis.biz.id`.
- **Tingkat Keterampilan Teknis:** Sangat Tinggi; terbiasa dengan Docker Compose, Linux CLI, reverse proxy, konfigurasi DNS (Cloudflare), dan pemecahan masalah port jaringan.
- **Kutipan Utama:** *"Sistem ini harus berjalan mandiri di VPS saya tanpa makan banyak RAM, tidak bentrok dengan port container lain, dan mudah diaudit lewat log terstruktur."*
- **Tujuan Utama (Goals):**
  1. Memastikan infrastruktur email masuk stabil dengan konsumsi RAM rendah (< 500 MB) pada VPS 2 vCPU / 3.6 GiB RAM.
  2. Memantau kesehatan server, log verifikasi domain (`DOM-001`), dan eksekusi auto-purge mailbox kedaluwarsa (`OPS-001`).
  3. Menjamin server email miliknya tidak disalahgunakan menjadi open relay atau target spam flood.
- **Frustrasi Utama (Pains):**
  - Mengelola Postfix/Dovecot manual yang rentan rusak saat pembaruan paket Linux.
  - Hambatan jaringan cloud (seperti blokir outbound port 25 oleh Tencent Cloud).
  - Ketidakpastian konsumsi memori mail engine tanpa adanya benchmark resmi.
- **Perilaku Penggunaan DomiBox:**
  - Mengatur konfigurasi variabel lingkungan dan rahasia via file `.env` terproteksi.
  - Memverifikasi status DNS MX via dashboard sebelum mengaktifkan domain.
  - Menginspeksi log audit sistem secara berkala melalui UI admin.
- **Status Bukti:** `VERIFIED` (Tervalidasi langsung melalui batas arsitektur VPS dan Piagam Proyek `docs/00-governance/project-charter.md`).

---

### 3.4 Persona 4: "Agus Abuse-Ops" — The Security & Anti-Abuse Sentinel
*Representasi Segmen: SEG-4 (Abuse & Security Operations)*

- **Profil Demografis (Arketipe):** Pria, 30 tahun, Spesialis Keamanan Operasional (SecOps).
- **Tingkat Keterampilan Teknis:** Sangat Tinggi; ahli dalam analisis log MTA, reputasi IP, SPF/DKIM/DMARC, serta mitigasi payload berbahaya.
- **Kutipan Utama:** *"Setiap email masuk yang tidak terdaftar harus segera ditolak di level SMTP (RCPT TO), dan lampiran berbahaya tidak boleh dieksekusi di browser pengguna."*
- **Tujuan Utama (Goals):**
  1. Mencegah akumulasi sampah di antrean mail engine (*mail queue bloat*) dengan penolakan langsung pesan ke alamat kedaluwarsa.
  2. Memastikan sanitasi konten email masuk mencegah serangan XSS (*Cross-Site Scripting*) dan injeksi iframe.
  3. Membatasi laju pembuatan alamat sementara (*rate limiting*) untuk menghindari kehabisan memori atau storage exhaustion.
- **Frustrasi Utama (Pains):**
  - Serangan *dictionary attack* atau spam harvesting ke alamat catch-all yang tidak terkontrol.
  - Payload email phishing yang menyamar sebagai verifikasi resmi.
- **Perilaku Penggunaan DomiBox:**
  - Mengawasi metrik penolakan SMTP dan tingkat kegagalan autentikasi pesan masuk (`SEC-004`).
  - Mengonfigurasi batas kuota pesan per mailbox (misal: maksimum 50 pesan atau 10 MB per temp inbox) (`SEC-003`).
- **Status Bukti:** `PROPOSED` (Diturunkan dari persyaratan keamanan `SEC-001` s/d `SEC-008`).

---

## 4. Matriks Pemetaan Kebutuhan Fitur terhadap Persona

| Modul / Fitur DomiBox | ID Kebutuhan | Dev Dedi (QA) | Rina Privasi (User) | Budi Sysadmin (Owner) | Agus Abuse-Ops (Security) |
| --- | --- | :---: | :---: | :---: | :---: |
| **Domain Management & DNS Check** | `DOM-001` | Pemanfaat Domain | Pemilih Domain | **Pengelola Utama (A)** | Peninjau Keamanan |
| **Temporary Mailbox (TTL/Disposable)** | `MBX-001` | **Pengguna Utama (A)** | Pengguna Utama | Konfigurator Batas | Pemantau Siklus Hidup |
| **Permanent Mailbox & Long-Term Aliases** | `MBX-002` | Opsional | **Pengguna Utama (A)** | Konfigurator Kuota | Pemantau Kuota |
| **Inbound SMTP & MIME Processing** | `INB-001` | Penerima Pesan | Penerima Pesan | Pemantau Koneksi | **Pengawas Reputasi (A)** |
| **OTP & Magic Link Auto-Extraction** | `OTP-001` | **Pengguna Utama (A)** | Pengguna Tambahan | Pemantau Akurasi | Peninjau Regex/Sanitasi |
| **Telegram Bot Multi-Channel Delivery** | `BOT-001` | **Pengguna Utama (A)** | Pengguna Sekunder | Pengatur Token Bot | Pengawas Token Pairing |
| **Web Dashboard (Inbox & Message Viewer)** | `WEB-001` | Pengguna Tambahan | **Pengguna Utama (A)** | Pemantau Sesi UI | Peninjau CSP/Sanitasi |
| **Audit Logging & Auto-Purge Scheduler** | `OPS-001` | Tidak Terlihat | Tidak Terlihat | **Pengelola Utama (A)** | **Auditor Utama (A)** |

*(Keterangan: **(A)** = Pemangku kepentingan atau pengguna primer untuk fitur tersebut)*

---

## 5. Ringkasan Kebutuhan UX Berdasarkan Pola Persona
1. **Copy-First Experience:** Sesuai preferensi Dev Dedi dan Rina Privasi, antarmuka Web dan Telegram Bot wajib mengedepankan tombol *one-click copy* untuk alamat email yang dibuat serta kode OTP yang diekstraksi.
2. **Visual TTL Countdown:** Tampilan hitung mundur masa aktif mailbox sementara yang jelas dan opsi 1-klik untuk perpanjangan masa aktif (*extend TTL*) guna meredakan kekhawatiran "disposable mail trap".
3. **Safety Shielding:** Tampilan peringatan visual apabila SPF/DKIM pengirim email gagal (*failed*), dan penonaktifan gambar eksternal secara default untuk melindungi privasi pengguna.
