# C4 Level 3: Component Diagram (Backend Core) — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/ArchCore | `docs/00-governance/project-charter.md`<br>`docs/02-requirements/srs.md`<br>`docs/03-architecture/architecture-overview.md`<br>`docs/03-architecture/diagrams/c4-container.md`<br>`docs/03-architecture/adr/ADR-006.md` |

---

## 1. Deskripsi Tingkat Komponen (Backend Core Service)

Diagram Komponen (C4 Level 3) merinci struktur internal kontainer **Backend Core Application (Fastify / Node.js 24 LTS)**. Diagram ini memperlihatkan bagaimana logika bisnis dibagi menjadi modul-modul independen (*loosely coupled, highly cohesive*) yang bekerja sama untuk memproses email, mengekstrak kode OTP, mengelola domain dan mailbox, serta mengendalikan notifikasi.

### Daftar Komponen Utama:
1. **AuthGuard:** Modul otentikasi dan otorisasi yang memvalidasi Admin Session Cookie dan Guest Access Token (`X-Mailbox-Token`).
2. **DomainManager:** Komponen pengelola status domain kustom, generator token TXT verifikasi, dan validator rekaman DNS melalui kueri Cloudflare DoH.
3. **MailboxService:** Pengendali siklus hidup mailbox (sementara dan permanen), alokasi kuota, penghitungan TTL, dan perpanjangan masa aktif.
4. **InboundParser & MIME Demuxer:** Pembedah aliran MIME RFC 5322 mentah yang memisahkan teks polos, HTML tersanitasi, serta metadata lampiran.
5. **OTPExtractor:** Mesin heuristik yang memindai teks dan HTML pesan untuk menemukan kode verifikasi (angka 4–8 digit, alfanumerik) dan tautan aktivasi akun.
6. **NotificationDispatcher:** Komponen antrean internal yang memformat ringkasan pesan dan mengirimkannya secara asinkron ke Telegram Bot API.
7. **JMAPClient:** Klien HTTP internal terabstraksi yang berkomunikasi dengan Stalwart Management API untuk membuat alias virtual dan menyinkronkan kuota.
8. **PurgeWorker:** Eksekutor penjadwal latar belakang yang memindai dan menghapus data mailbox kedaluwarsa secara atomik dari basis data dan disk.

---

## 2. Diagram Mermaid C4 Component

```mermaid
flowchart TD
    subgraph ExternalBoundaries["Input Eksternal & Proxy"]
        HTTP_REQ["Klien Web / API\n[HTTP Request / Header]"]
        INBOUND_HOOK["Stalwart Inbound Spool\n[Raw RFC 5322 MIME Stream]"]
        TG_POLL["Telegram Webhook / Updates\n[grammY Long-Polling]"]
    end

    subgraph FastifyBackend["Fastify Core Monolith (Container: backend-core)"]
        
        %% Lapisan Keamanan & Router
        Router["⚡ Fastify HTTP Router\n(Route Definitions & Validation Schema)"]
        AuthGuard["🛡️ AuthGuard\n- Session Cookie Validator (Admin)\n- Mailbox Access Token Validator (Guest)\n- Rate Limiting Enforcement"]
        
        %% Layanan Logika Bisnis
        DomainMgr["🌐 DomainManager\n- Registrasi Domain Kustom\n- DoH DNS Query Engine (MX/TXT)\n- Deteksi Konflik Cloudflare Routing"]
        
        MailboxSvc["📬 MailboxService\n- Generate Random / Custom Local-Part\n- Hitung & Perpanjang TTL (Expires_at)\n- Validasi Kuota Mailbox Permanen"]
        
        InboundParser["🧩 InboundParser & Demuxer\n- RFC 5322 MIME Stream Decomposer\n- Ekstraksi From, To, Subject, Date\n- DOMPurify HTML Sanitization"]
        
        OTPExtractor["🔍 OTPExtractor\n- Regex Heuristics (4-8 Digit OTP)\n- Pola Kata Kunci (Verification, Code, dsb.)\n- Ekstraksi Tautan URL Aktivasi"]
        
        NotifDispatch["📢 NotificationDispatcher\n- Template Formatter (MarkdownV2)\n- Retry Queue & Exponential Backoff\n- Dispatcher ke Telegram Bot Client"]
        
        JMAPClient["🔌 JMAPClient Service\n- Client Wrapper REST/JMAP Stalwart\n- Sinkronisasi Akun & Virtual Alias\n- Notifikasi Perubahan Kuota"]
        
        PurgeWorker["⏱️ PurgeWorker (Scheduler)\n- Interval Poller (Setiap 60 Detik)\n- Batch Deletion Record Expired\n- Trigger Unlink Attachment Files"]
    end

    subgraph DataAndExternal["Penyimpanan & Layanan Luar"]
        Postgres[("🗄️ PostgreSQL 16\n(Tabel: domains, mailboxes,\nmessages, tokens, audit_logs)")]
        FileStorage[("📁 Docker Volume Storage\n(Raw EML & Attachments)")]
        StalwartAPI["✉️ Stalwart JMAP Engine\n(Port 8080 Internal API)"]
        Cloudflare["☁️ Cloudflare DoH\n(https://cloudflare-dns.com)"]
        TelegramCloud["📱 Telegram Bot API\n(api.telegram.org)"]
    end

    %% Relasi Router & Auth
    HTTP_REQ --> Router
    Router --> AuthGuard
    AuthGuard --> DomainMgr
    AuthGuard --> MailboxSvc
    
    %% Relasi Aliran Inbound
    INBOUND_HOOK --> InboundParser
    InboundParser --> OTPExtractor
    InboundParser --> MailboxSvc
    InboundParser --> FileStorage
    
    %% Relasi Logika & Notifikasi
    OTPExtractor --> NotifDispatch
    MailboxSvc --> JMAPClient
    DomainMgr --> Cloudflare
    NotifDispatch --> TelegramCloud
    TG_POLL --> NotifDispatch

    %% Relasi Persistensi
    DomainMgr <--> Postgres
    MailboxSvc <--> Postgres
    InboundParser --> Postgres
    JMAPClient <--> StalwartAPI
    
    %% Relasi Purge
    PurgeWorker <--> Postgres
    PurgeWorker --> FileStorage
    PurgeWorker --> JMAPClient
```

---

## 3. Rincian Modul Komponen & Antarmuka Internal

| Komponen | Masukan (*Inputs*) | Keluaran (*Outputs*) | Dependensi Internal / Eksternal |
| --- | --- | --- | --- |
| **AuthGuard** | Header `Authorization`, `Cookie`, `X-Mailbox-Token` | Konteks `req.user` atau `req.mailbox` terverifikasi | Kueri session/token ke PostgreSQL, modul `@fastify/cookie` |
| **DomainManager** | Nama domain, request validasi TXT/MX | Status domain (`ACTIVE`, `PENDING`, `CONFLICT_ROUTING`) | Modul `node-fetch` ke Cloudflare DoH, tabel `domains` |
| **MailboxService** | Permintaan pembuatan mailbox, parameter TTL | Objek `Mailbox`, token akses unik 32-karakter | Modul `crypto`, JMAPClient, tabel `mailboxes` |
| **InboundParser** | Aliran biner MIME email masuk | Objek pesan terstruktur JSON, status SPF/DKIM | Pustaka `postal-mime`, `DOMPurify`, volume disk `mail-data` |
| **OTPExtractor** | Teks polos & teks HTML dari InboundParser | Array kode OTP terdeteksi, array URL aktivasi | Modul ekspresi reguler heuristik internal |
| **NotificationDispatcher** | Ringkasan email, metadata pesan, hasil OTP | Pengiriman pesan chat terformat ke Telegram | Framework `grammY`, Telegram Bot API eksternal |
| **JMAPClient** | Perintah pembuatan alias, update kuota | Respon status HTTP 200/204 dari Stalwart | Endpoint Stalwart JMAP (`http://stalwart:8080/jmap`) |
| **PurgeWorker** | Pemicu cron interval (60 detik) | Jumlah baris terhapus, berkas fisik yang di-unlink | Transaksi SQL PostgreSQL, syscall `fs.promises.unlink` |
