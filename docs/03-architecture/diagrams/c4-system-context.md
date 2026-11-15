# C4 Level 1: System Context Diagram — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/ArchCore | `docs/00-governance/project-charter.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/02-requirements/srs.md`<br>`docs/03-architecture/architecture-overview.md`<br>`docs/03-architecture/diagrams/c4-container.md` |

---

## 1. Deskripsi Tingkat Konteks Sistem

Diagram Konteks Sistem (C4 Level 1) ini menggambarkan batasan terluar (*system boundaries*) dari platform **DomiBox**, pengguna manusia yang berinteraksi dengannya, serta sistem-sistem eksternal yang terhubung langsung melalui protokol jaringan.

### Entitas Utama dalam Konteks:
1. **System Owner / Administrator:** Pengguna tunggal pengelola sistem yang memiliki hak administratif penuh atas domain kustom, konfigurasi sistem, dan pemantauan mailbox.
2. **External Mail Sender (MTA Internet):** Server email pengirim di internet (seperti Google Gmail, Microsoft Outlook, penyedia SaaS/e-commerce) yang mengirimkan pesan email masuk ke domain yang dihosting di DomiBox.
3. **DomiBox Platform:** Sistem inti yang menangani penerimaan email SMTP, pemilahan mailbox, ekstraksi kode OTP, antarmuka web, serta integrasi bot Telegram.
4. **Cloudflare DNS Infrastructure:** Penyedia layanan DNS otoritatif untuk resolusi rekaman MX, A, dan validasi TXT kepemilikan domain kustom.
5. **Telegram Bot API:** Layanan cloud perpesanan Telegram yang menghubungkan bot DomiBox dengan aplikasi Telegram milik pemilik.
6. **Tencent Cloud Infrastructure:** Penyedia infrastruktur komputasi awan yang meng-host instans CVM `vps-tencent3b`, mengelola Security Group, dan menyediakan konektivitas jaringan publik.

---

## 2. Diagram Mermaid C4 Context

```mermaid
flowchart TB
    subgraph Users["Pengguna Sistem"]
        Owner["👤 System Owner / Admin\n[Person]\nPemilik tunggal sistem yang mengelola domain,\nmembuat mailbox, meninjau email, dan OTP"]
        Sender["🌐 External Mail Sender (MTA)\n[External System]\nServer mail eksternal di internet (Google, MS365,\nSaaS platform) yang mengirim email transaksi & OTP"]
    end

    subgraph Boundaries["Perimeter Sistem DomiBox"]
        DomiBox["📦 DomiBox Platform\n[Software System]\nSistem manajemen email multi-domain mandiri\n(Inbound SMTP, Disposable/Permanent Mailboxes,\nOTP Extractor, Web Dashboard SPA, Telegram Bot)"]
    end

    subgraph ExternalSystems["Sistem & Infrastruktur Eksternal"]
        Cloudflare["☁️ Cloudflare DNS\n[External SaaS]\nManajemen DNS zona otoritatif (MX, A, TXT)\ndan validasi status kepemilikan domain kustom"]
        TelegramAPI["📱 Telegram Bot API\n[External SaaS]\nLayanan perpesanan Telegram untuk pengiriman notifikasi\npush ringkasan email, kode OTP, dan interaksi command bot"]
        TencentInfra["🏢 Tencent Cloud Infrastructure\n[External IaaS / VPS Host]\nMenyediakan instans VPS Ubuntu 24.04 (2 vCPU, 3.6 GiB RAM),\nkontrol Security Group jaringan, dan penyimpanan blok"]
    end

    %% Relasi Aliran Data
    Sender -->|"Mengirim email masuk via SMTP\n[TCP:25 / STARTTLS]"| DomiBox
    Owner -->|"Mengakses dashboard web via peramban\n[HTTPS / Port 443]"| DomiBox
    Owner <-->|"Menerima notifikasi OTP & mengirim perintah bot\n[Aplikasi Klien Telegram / HTTPS]"| TelegramAPI

    DomiBox <-->|"Mengirim push notifikasi email & polling pesan\n[HTTPS REST API / JSON]"| TelegramAPI
    DomiBox -->|"Melakukan verifikasi rekaman DNS MX & TXT\n[DNS-over-HTTPS (DoH) / UDP 53]"| Cloudflare
    DomiBox -.->|"Dihosting dan berjalan di atas instans\n[Docker Engine / Ubuntu Linux]"| TencentInfra

    Sender -.->|"Menanyakan rekaman MX domain tujuan\n[DNS Query UDP:53]"| Cloudflare

    %% Styling visual
    classDef person fill:#08427B,stroke:#052E56,color:#FFFFFF,font-weight:bold;
    classDef system fill:#1168BD,stroke:#0B4884,color:#FFFFFF,font-weight:bold;
    classDef extSystem fill:#999999,stroke:#666666,color:#FFFFFF;

    class Owner person;
    class Sender,Cloudflare,TelegramAPI,TencentInfra extSystem;
    class DomiBox system;
```

---

## 3. Matriks Aliran Data & Protokol Antar-Sistem

| Sumber | Tujuan | Protokol / Port | Payload & Karakteristik Data | Rujukan Kebutuhan |
| --- | --- | :---: | --- | :---: |
| **External Mail Sender** | **DomiBox** | SMTP / TCP:25 (STARTTLS) | Aliran data email mentah RFC 5322 (Header, MIME multipart, teks, HTML, lampiran $\le 15$ MB). | `INB-001`, `FR-004` |
| **System Owner** | **DomiBox** | HTTPS / TCP:443 (TLS 1.3) | Permintaan Web Dashboard SPA, autentikasi session cookie, kueri mailbox, dan inspeksi pesan. | `WEB-001`, `FR-007` |
| **DomiBox** | **Telegram Bot API** | HTTPS / TCP:443 (REST) | Pengiriman payload notifikasi JSON (subjek, pengirim, ringkasan teks, kode OTP yang diekstrak). | `BOT-001`, `FR-006` |
| **DomiBox** | **Cloudflare DNS** | DNS over HTTPS / TCP:443 | Kueri JSON REST ke endpoint Cloudflare DoH (`https://cloudflare-dns.com/dns-query`) untuk validasi MX dan TXT. | `DOM-001`, `FR-001` |
| **DomiBox** | **Tencent Cloud** | Kernel Syscalls & Cgroups | Eksekusi runtime Docker Compose, batasan memori RAM $\le 1.2$ GiB, partisi penyimpanan disk volume $\le 10$ GB. | `OPS-001`, `NFR-009` |
