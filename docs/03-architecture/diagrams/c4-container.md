# C4 Level 2: Container Diagram — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/ArchCore | `docs/00-governance/project-charter.md`<br>`docs/02-requirements/srs.md`<br>`docs/03-architecture/architecture-overview.md`<br>`docs/03-architecture/diagrams/c4-system-context.md`<br>`docs/03-architecture/diagrams/component-diagram.md`<br>`docs/03-architecture/diagrams/deployment-diagram.md` |

---

## 1. Deskripsi Tingkat Kontainer Sistem

Diagram Kontainer (C4 Level 2) membedah batasan internal sistem **DomiBox** menjadi modul-modul kontainer perangkat lunak terisolasi yang dapat dideploy secara independen namun beroperasi secara terkoordinasi di bawah satu orkestrator Docker Compose pada VPS host.

### Daftar Kontainer dalam Ekosistem DomiBox:
1. **Edge Reverse Proxy (Caddy v2 Alpine):** Gerbang tunggal lalu lintas web masuk (HTTP/HTTPS) yang menangani terminasi TLS otomatis via Let's Encrypt dan menyajikan aset statis.
2. **Web Dashboard SPA (React 18 + Vite + shadcn/ui):** Antarmuka pengguna browser berbasis Single Page Application murni.
3. **Core Backend & Ingestion Service (Fastify / Node.js 24 LTS):** Monolit modular yang menangani REST API, webhook/pipe ingestion dari server mail, MIME parsing, heuristik ekstraksi OTP, dan integrasi bot.
4. **Purge Worker / Scheduler (In-Process / BullMQ):** Pekerja latar belakang terjadwal untuk evaluasi kedaluwarsa mailbox (`expires_at`) dan pembersihan file disk.
5. **Mail Server Engine (Stalwart v1.0.3 Community - Rust):** Server mail performa tinggi penyedia listener SMTP port 25, pemverifikasi SPF/DKIM/DMARC, serta API manajemen JMAP.
6. **Relational Database (PostgreSQL 16 Alpine):** Basis data relasional persisten untuk metadata sistem, definisi domain, mailbox, token, dan indeks pencarian pesan.

---

## 2. Diagram Mermaid C4 Container

```mermaid
flowchart TD
    subgraph Users["Klien Pengguna & Pengirim"]
        Sender["🌐 External MTA\n(Internet Mail Sender)"]
        Browser["👤 Web Browser\n(System Owner / Admin)"]
        Telegram["📱 Telegram App\n(System Owner Client)"]
    end

    subgraph ExternalServices["Layanan Pihak Ketiga"]
        CloudflareDoH["☁️ Cloudflare DoH API\n(DNS Validation Engine)"]
        TelegramAPI["📱 Telegram Bot API\n(Push Notification & Commands)"]
    end

    subgraph DomiBoxBoundary["Perimeter Sistem DomiBox (Docker Network: domibox-net)"]
        
        Caddy["🛡️ Caddy Reverse Proxy\n[Container: Caddy v2 Alpine]\n- Terminasi TLS Otomatis (Let's Encrypt)\n- Penyaji Aset Statis Web SPA\n- Reverse Proxy /api/* & /jmap/*\nRAM: ~30 MB"]
        
        WebSPA["💻 Web Dashboard SPA\n[Static Files / React 18 + Vite]\n- Antarmuka manajemen domain & mailbox\n- Penampil pesan email & kode OTP\n- Berkas statis di-cache Caddy"]
        
        FastifyApp["⚙️ Core Backend & Ingestion\n[Container: Fastify / Node.js 24 LTS]\n- REST API Endpoints (/api/v1/*)\n- Inbound MIME Parser & Sanitizer\n- OTP & Verification Link Extractor\n- AuthGuard (Session & Guest Token)\n- Telegram Bot Service (grammY)\nRAM: ~150 MB"]
        
        Scheduler["⏱️ Purge Worker & Scheduler\n[In-Process Module / Fastify Worker]\n- Interval Scan Tiap 60 Detik\n- Hard-delete Mailbox Expired\n- Unlink Attachment Files dari Disk\n- Sinkronisasi Alias via JMAP"]
        
        Stalwart["✉️ Stalwart Mail Server\n[Container: Rust v1.0.3]\n- SMTP Listener Inbound (Port 25)\n- Verifikator SPF, DKIM, DMARC\n- JMAP Management API (:8080)\n- Virtual Alias Routing\nRAM: ~180 MB"]
        
        Postgres[("🗄️ Relational Database\n[Container: PostgreSQL 16 Alpine]\n- Tabel: domains, mailboxes, messages\n- Tabel: tokens, audit_logs, attachments\n- JSONB Indexing & ACID Transactions\nRAM: ~120 MB")]
        
        MailVol[("📁 Maildir / Attachment Volume\n[Docker Named Volume: mail-data]\nPenyimpanan berkas mentah EML &\nlampiran biner email permanen")]
    end

    %% Aliran Masuk Inbound SMTP
    Sender -->|"SMTP TCP:25\n[STARTTLS / RFC 5321]"| Stalwart
    Stalwart -->|"Ingest Hook / Webhook HTTP\n[POST /internal/inbound]"| FastifyApp

    %% Aliran Akses Web
    Browser -->|"HTTPS:443\n[TLS 1.3 / HTTP/2]"| Caddy
    Caddy -->|"Serve /index.html & JS/CSS"| WebSPA
    Caddy -->|"Reverse Proxy /api/v1/*"| FastifyApp
    Caddy -->|"Reverse Proxy /jmap/*"| Stalwart

    %% Interaksi Logika & Basis Data
    FastifyApp <-->|"Kueri Metadata, Sesi & Transaksi\n[pg pool: 15 conn / SQL]"| Postgres
    FastifyApp -->|"Baca/Tulis Konten Berkas EML"| MailVol
    FastifyApp <-->|"JMAP Client API\n[HTTP:8080 / JSON]"| Stalwart
    
    %% Aliran Scheduler
    Scheduler <-->|"Kueri Mailbox Kedaluwarsa\n[SELECT ... WHERE expires_at < NOW()]"| Postgres
    Scheduler -->|"Hapus File Lampiran Fisik"| MailVol
    Scheduler -->|"Evict Alias Virtual via JMAP"| Stalwart

    %% Integrasi Eksternal
    FastifyApp -->|"Validasi Record DNS MX & TXT\n[HTTPS / JSON REST]"| CloudflareDoH
    FastifyApp <-->|"Kirim Notifikasi Push & Polling\n[HTTPS REST / grammY]"| TelegramAPI
    Telegram <-->|"Interaksi Pesan Instan"| TelegramAPI
```

---

## 3. Tanggung Jawab & Batas Kontainer

| Nama Kontainer | Teknologi / Image | Port Internal / Terbuka | Batas Memori (cgroups) | Tanggung Jawab Utama |
| --- | --- | :---: | :---: | --- |
| **caddy** | `caddy:2.8-alpine` | `80:80`, `443:443` | `64 MB` | Manajemen sertifikat SSL otomatis, penyajian berkas statis frontend, mitigasi rate-limit awal HTTP. |
| **stalwart** | `stalwartlabs/mail-server:v1.0.3` | `25:25`, `8080:8080` (internal) | `384 MB` | Menerima koneksi SMTP inbound, validasi anti-spoofing (SPF/DKIM), manajemen akun/alias via JMAP. |
| **backend-core** | `node:24-alpine` | `3000:3000` (internal) | `256 MB` | Menjalankan Fastify server, orkestrasi bisnis domain/mailbox, ekstraksi OTP, pengirim notifikasi Telegram. |
| **postgres** | `postgres:16-alpine` | `5432:5432` (internal) | `256 MB` | Menjamin konsistensi ACID, isolasi konkurensi (MVCC), penyimpanan metadata pesan dan audit log. |
| **web-spa** | N/A (Multi-stage build) | N/A (Static files) | `0 MB` (Runtime) | Menghasilkan bundel HTML/JS/CSS yang dimount langsung ke root direktori web Caddy. |
