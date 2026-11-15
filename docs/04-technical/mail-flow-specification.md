# Mail Flow & Ingestion Pipeline Specification — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/TechSpec | `docs/02-requirements/functional-specs/03-inbox-management.md`<br>`docs/03-architecture/diagrams/email-flow-sequence.md`<br>`docs/03-architecture/adr/ADR-002.md`<br>`docs/03-architecture/adr/ADR-010.md` |

---

## 1. Arsitektur Alur Surat Masuk (Inbound Mail Architecture)
Platform DomiBox beroperasi dalam mode **Inbound-Only** pada fase MVP (`A-001`, `Q-003`). Email masuk diarahkan ke server melalui rekaman DNS MX domain kustom yang menunjuk langsung ke alamat IP publik VPS Tencent Cloud (`vps-tencent3b`, Port 25 inbound).

---

## 2. Diagram Pipeline Pemrosesan Email (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor Sender as MTA Pengirim (Gmail/SaaS)
    participant DNS as Cloudflare DNS
    participant SMTP as Stalwart Mail Engine (Port 25)
    participant Pipe as DomiBox Ingestion Worker (Fastify)
    participant Parser as MIME & HTML Sanitizer
    participant OTP as OTP Regex Extractor
    participant DB as PostgreSQL 16
    participant Bot as Telegram Bot (grammY)
    participant Web as Web Dashboard (SSE Client)

    Sender->>DNS: Kueri Rekaman MX domain (sintaksis.biz.id)
    DNS-->>Sender: Return IP VPS DomiBox (Priority 10)
    Sender->>SMTP: Buka Koneksi SMTP TCP/25 + STARTTLS
    SMTP->>SMTP: Validasi RCPT TO (Apakah domain & mailbox aktif?)
    alt Mailbox Tidak Ditemukan / Kedaluwarsa
        SMTP-->>Sender: 550 5.1.1 User unknown / Mailbox expired
    else Mailbox Aktif
        SMTP-->>Sender: 250 2.1.5 Recipient OK
        Sender->>SMTP: Kirim Payload RFC822 (DATA)
        SMTP-->>Sender: 250 2.0.0 Message accepted for delivery
        SMTP->>Pipe: Webhook HTTP POST / Inbound Pipe Raw EML
        Pipe->>Parser: Parse Header, Multipart MIME, Sanitasi HTML (DOMPurify)
        Parser->>OTP: Ekstraksi Pola OTP (4-8 Digit) & Magic Link
        Pipe->>DB: INSERT INTO messages (sender, subject, sanitized_html, otp, ...)
        par Notifikasi Multi-Kanal
            Pipe->>Bot: Kirim Pesan Push Telegram (< 2 detik)
        and
            Pipe->>Web: Emit Event SSE `new_message` ke Dashboard Aktif
        end
    end
```

---

## 3. Langkah-Langkah Validasi & Keamanan Inbound
1. **Validasi RCPT TO di Edge MTA:** Stalwart memvalidasi alamat penerima terhadap daftar alias aktif via kueri internal/webhook. Email untuk alamat yang telah kedaluwarsa atau tidak terdaftar langsung ditolak dengan kode SMTP 550 (`F4`, `MBX-005`).
2. **Evaluasi Otentikasi Email (`SEC-004`):**
   - SPF (*Sender Policy Framework*) dievaluasi terhadap IP pengirim.
   - DKIM (*DomainKeys Identified Mail*) diverifikasi menggunakan public key pengirim.
   - DMARC dievaluasi dan status dicatat pada kolom `spf_status`, `dkim_status`, `dmarc_status`.
3. **Penyimpanan Raw EML Terbatas:** Berkas mentah disimpan sementara pada volume lokal Docker `mail_spool` dan akan dihapus saat mailbox kedaluwarsa (`MBX-005`).
