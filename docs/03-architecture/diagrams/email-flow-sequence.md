# Email Flow Sequence (Inbound to Notification)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-15`  
**Owner:** `Architecture`  
**Dokumen Terkait:** `../adr/ADR-001.md`, `../adr/002.md`, `../adr/ADR-003.md`, `../adr/ADR-004.md`, `../adr/ADR-006.md`, `../adr/ADR-008.md`, `../adr/ADR-011.md`, `./network-port-matrix.md`, `../../02-requirements/srs.md` (`FR-004`, `FR-005`, `FR-006`, `FR-007`, `INB-*`, `OTP-*`), `../../02-requirements/nfr-spec.md` (`NFR-004`, `NFR-005`), `../../02-requirements/security-privacy-requirements.md` (`SEC-002`, `SEC-004`, `SEC-005`, `SEC-006`, `SEC-007`)

## 1. Tujuan
Mendefinisikan urutan end-to-end penerimaan email inbound pada DomiBox: dari koneksi SMTP eksternal ke Stalwart, pemrosesan event/JMAP, parsing MIME, ekstraksi OTP/magic link, persistensi metadata/pesan, hingga distribusi pembaruan ke Telegram, webhook internal, dan Web UI (SSE/polling).

## 2. Aktor & Komponen
| Aktor/Komponen | Peran | Catatan Implementasi |
| --- | --- | --- |
| External MTA / Sender | Pengirim email eksternal | Mengirim ke MX domain yang mengarah ke VPS DomiBox |
| Stalwart Mail Server | SMTP ingress, penerimaan pesan, penyimpanan mail objects, event source | Port 25 publik; HTTP/JMAP internal (8081) |
| DomiBox Inbound Worker | Konsumen event/webhook/poll JMAP, orkestrasi ingestion | Bagian dari modular monolith backend/worker |
| MIME Parser & Sanitizer | Parsing RFC 5322/MIME, ekstraksi body/attachment metadata, sanitasi HTML | Menjaga `SEC-005`, `SEC-007` |
| OTP/Link Extractor | Heuristik regex/kontekstual untuk OTP dan magic link | Output `extracted_otp`, `extracted_link`, confidence metadata |
| PostgreSQL | Persistensi mailbox/message/audit/notification state | Internal only (`5432`) |
| Notification Dispatcher | Fan-out ke Telegram/Webhook/SSE channel state | Idempotent per message event |
| Telegram Bot API | Kanal notifikasi eksternal | Payload dibatasi (ringkasan + OTP/link sesuai kebijakan) |
| External Webhook Consumer | Integrasi downstream opsional | Signed payload + retry policy |
| Web API/SSE Endpoint | Update UI real-time/polling | Reverse proxy HTTPS publik |

## 3. Sequence Diagram (End-to-End)

```mermaid
sequenceDiagram
    autonumber
    actor Sender as External MTA / Sender
    participant DNS as Authoritative DNS/MX
    participant ST as Stalwart (SMTP :25 / JMAP :8081)
    participant IW as DomiBox Inbound Worker
    participant DB as PostgreSQL (:5432 internal)
    participant MP as MIME Parser & Sanitizer
    participant OE as OTP/Link Extractor
    participant ND as Notification Dispatcher
    participant TG as Telegram Bot API
    participant WH as External Webhook Consumer
    participant WEB as Web API/SSE (HTTPS :443 via proxy)
    participant UI as Web Dashboard Client

    %% SMTP ingress & recipient validation
    Sender->>DNS: Resolve MX(domain)
    DNS-->>Sender: MX -> mail host (VPS)
    Sender->>ST: TCP connect :25 + EHLO/HELO
    Sender->>ST: MAIL FROM / RCPT TO(mailbox@domain)
    ST->>IW: Recipient validation hook/query (JMAP/internal API or local policy callback)
    IW->>DB: Lookup domain/mailbox status (ACTIVE, not expired, not purged)
    DB-->>IW: Mailbox/domain state + policy flags

    alt Recipient invalid / domain inactive / mailbox expired
        IW-->>ST: Reject recipient (policy decision)
        ST-->>Sender: 550/554 User unknown or mailbox inactive
        Note over ST,Sender: Early rejection (INB-001, SEC-004) mencegah antrian sampah
    else Recipient valid and active
        IW-->>ST: Accept recipient
        ST-->>Sender: 250 OK (RCPT accepted)
        Sender->>ST: DATA (RFC 5322/MIME message)
        ST-->>Sender: 250 Message accepted / queued for processing

        %% Event delivery to DomiBox
        ST-->>IW: Inbound event / webhook / JMAP change notification (message id, mailbox ref, envelope metadata)
        IW->>ST: JMAP Email/get, Blob/download (raw message/MIME parts, headers, auth results if available)
        ST-->>IW: Raw message + metadata + SPF/DKIM/DMARC indicators (as provided)

        %% Idempotency and parsing pipeline
        IW->>DB: Begin transaction + upsert message stub (idempotency key: server msg-id/hash)
        DB-->>IW: Inserted/new or duplicate

        alt Duplicate event/message
            IW->>DB: Record duplicate event (audit/debug) and commit no-op
            Note over IW,DB: Idempotent processing; no duplicate notifications
        else New message
            IW->>MP: Parse MIME, headers, text/plain, text/html, attachments metadata
            MP-->>IW: Structured content + sanitized HTML preview payload + parse status
            IW->>OE: Extract OTP and magic link (subject/body heuristics)
            OE-->>IW: extracted_otp, extracted_link, confidence, evidence offsets (internal)
            IW->>DB: Persist Message, auth statuses, extraction results, mailbox last_activity
            IW->>DB: Append audit/event log entries (OPS-002, SEC-008)
            DB-->>IW: Commit OK

            %% Fan-out notifications and UI updates
            par Telegram notification
                IW->>ND: Dispatch notification event (mailbox/message summary)
                ND->>DB: Resolve paired Telegram chat + notification preferences
                DB-->>ND: Active chat binding / none
                opt Telegram pairing active
                    ND->>TG: sendMessage / inline keyboard (summary + OTP copy action)
                    TG-->>ND: Delivery result
                    ND->>DB: Store notification delivery status
                end
            and Webhook notification
                ND->>DB: Resolve webhook subscriptions (if configured)
                DB-->>ND: Webhook targets + secrets/policy
                opt Webhook subscription exists
                    ND->>WH: HTTPS POST signed payload (event, mailbox, otp/link metadata policy)
                    WH-->>ND: 2xx/Retryable error
                    ND->>DB: Store webhook attempt/result
                end
            and Web UI update
                ND->>WEB: Publish message-created event (internal bus/channel)
                WEB-->>UI: SSE event / polling response includes new message summary
                UI->>WEB: GET message detail (with mailbox access token/session)
                WEB->>DB: Authorize + fetch sanitized message payload
                DB-->>WEB: Message detail
                WEB-->>UI: JSON response (sanitized HTML/text + extracted OTP/link)
            end
        end
    end
```

## 4. Alur Detail & Aturan Pemrosesan

### 4.1 Ingress SMTP & Validasi Penerima (Stalwart + Policy)
1. External MTA menyelesaikan lookup MX dan membuka koneksi TCP/25 ke Stalwart.
2. Saat `RCPT TO`, Stalwart memanggil mekanisme validasi penerima (hook/policy/query ke backend/JMAP directory state) untuk memastikan domain `ACTIVE` dan mailbox `ACTIVE`/tidak `EXPIRED`.
3. Alamat tidak valid/expired ditolak dini (SMTP 550/554) untuk mengurangi beban storage dan spam queue (`INB-001`, `SEC-004`).
4. Pesan valid diterima dan disimpan oleh Stalwart; event ingestion diteruskan ke DomiBox Inbound Worker.

### 4.2 Ingestion Event, JMAP Fetch, dan Idempotensi
1. Worker menerima event (push webhook dari Stalwart atau polling JMAP perubahan) berisi referensi pesan.
2. Worker mengambil data lengkap via JMAP/HTTP internal (`Email/get`, blob/body part fetch) tanpa mengekspos endpoint internal ke publik (`ADR-004`, `network-port-matrix.md`).
3. Worker membuat idempotency key (kombinasi mailbox + server message id + hash envelope/body fingerprint) untuk mencegah duplikasi saat retry/event ganda.
4. Seluruh operasi persistensi inti dilakukan dalam transaksi DB; duplicate event menghasilkan no-op notifikasi.

### 4.3 Parsing MIME, Sanitasi, dan Ekstraksi
1. MIME parser memisahkan header, body plaintext/HTML, dan metadata lampiran (`INB-002`).
2. Sanitizer membersihkan HTML berbahaya (script/event handler/tracker policy sesuai `SEC-005`, `SEC-007`) dan menyiapkan payload aman untuk viewer sandbox.
3. OTP extractor menerapkan heuristik regex + konteks kata kunci (kode 4–8 digit / alfanumerik 6–8) dan deteksi magic link (`OTP-001`, `OTP-002`).
4. Hasil parsing/ekstraksi disimpan bersama status SPF/DKIM/DMARC bila tersedia (`INB-003`).

### 4.4 Persistensi, Audit, dan Fan-out Notifikasi
1. Message record, extraction metadata, status autentikasi pengirim, dan audit log ditulis ke PostgreSQL (`OPS-002`, `SEC-008`).
2. Notification Dispatcher melakukan fan-out paralel ke Telegram, webhook, dan kanal Web UI.
3. Payload Telegram/webhook dibatasi sesuai prinsip minimisasi data (tidak mengirim seluruh body mentah secara default; fokus pada ringkasan + OTP/link yang relevan).
4. Kegagalan pengiriman kanal eksternal tidak membatalkan persistensi pesan; retry dicatat sebagai status delivery terpisah.

## 5. Failure Modes & Penanganan
| Failure Mode | Deteksi | Respons Sistem | Dampak |
| --- | --- | --- | --- |
| Mailbox/domain tidak valid saat `RCPT TO` | Lookup DB/policy gagal | SMTP reject 550/554 | Pesan tidak diterima; mencegah spam storage |
| Event diterima ganda | Idempotency key duplicate | No-op persist/notify, audit duplicate | Konsistensi terjaga |
| JMAP fetch gagal sementara | HTTP timeout/error dari Stalwart | Retry dengan backoff + dead-letter operasional | Keterlambatan ingest, tanpa kehilangan event jika retry berhasil |
| MIME malformed | Parser exception/partial parse | Simpan raw/partial + `PARSE_WARNING`, lanjut ekstraksi terbatas | Pesan tetap dapat ditinjau |
| Sanitizer menemukan konten berbahaya | Rule match (script/handler/URI) | Strip/neutralize, tandai hasil sanitasi | Viewer aman, fidelitas HTML dapat berkurang |
| Telegram/webhook down | Non-2xx/timeout | Persist sukses, enqueue retry notifikasi | Pesan tetap tersedia di Web UI |
| DB transaction failure | Commit error | Rollback, retry ingestion | Konsistensi atomik terjaga |

## 6. Kebutuhan Observabilitas (Minimum)
- Metrik: jumlah SMTP accepted/rejected, latensi event-to-persist, latensi event-to-notify, tingkat duplikasi event, failure rate parser/sanitizer/extractor, delivery success rate Telegram/webhook.
- Log terstruktur (JSON): `message_id`, `mailbox_id`, `domain`, `smtp_rcpt_result`, `ingest_stage`, `parse_status`, `otp_detected`, `notify_channels`, `latency_ms`.
- Korelasi audit: event inbound, persist, dan dispatch harus dapat ditelusuri per message id (`SEC-008`, `OPS-002`).

## 7. Traceability
| Kebutuhan | Cakupan pada Diagram/Flow |
| --- | --- |
| `BR-002` | Penerimaan inbound real-time, parsing, ekstraksi OTP/link |
| `BR-003` | Distribusi ke Telegram dan pembaruan Web UI |
| `FR-004`, `INB-001..003` | SMTP RCPT validation, MIME parsing, status SPF/DKIM/DMARC |
| `FR-005`, `OTP-001..002` | Ekstraksi OTP dan magic link |
| `FR-006`, `BOT-001..002` | Dispatch notifikasi Telegram ke chat ter-pairing |
| `FR-007`, `WEB-001..002` | SSE/polling update dan payload viewer tersanitasi |
| `FR-008.1`, `OPS-002` | Audit/event logging pada tahap ingest dan dispatch |
| `NFR-004`, `NFR-005` | Target latensi pemrosesan inbound dan akurasi ekstraksi OTP |
| `SEC-002`, `SEC-004`, `SEC-005`, `SEC-006`, `SEC-007`, `SEC-008` | Isolasi akses, validasi pengirim/penerima, sanitasi konten, minimisasi payload notifikasi, audit trail |
| `ADR-001..004`, `ADR-006`, `ADR-008`, `ADR-011` | Modular monolith, Stalwart, JMAP integration, PostgreSQL persistence, auth/session boundaries, Telegram, background processing/dispatch |

## 8. Referensi Teknis & Standar
- RFC 5321 — Simple Mail Transfer Protocol: https://www.rfc-editor.org/rfc/rfc5321
- RFC 5322 — Internet Message Format: https://www.rfc-editor.org/rfc/rfc5322
- RFC 2045 — MIME Part One: Format of Internet Message Bodies: https://www.rfc-editor.org/rfc/rfc2045
- RFC 8620 — JMAP Core: https://www.rfc-editor.org/rfc/rfc8620
- RFC 8621 — JMAP for Mail: https://www.rfc-editor.org/rfc/rfc8621
- RFC 7208 — SPF: https://www.rfc-editor.org/rfc/rfc7208
- RFC 6376 — DKIM Signatures: https://www.rfc-editor.org/rfc/rfc6376
- RFC 7489 — DMARC: https://www.rfc-editor.org/rfc/rfc7489
- Stalwart Mail Server Documentation: https://stalw.art/docs/
- Stalwart JMAP Documentation: https://stalw.art/docs/jmap/overview
- Telegram Bot API: https://core.telegram.org/bots/api
- OWASP XSS Prevention Cheat Sheet (sanitasi/rendering aman): https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- Server-Sent Events (WHATWG HTML Living Standard): https://html.spec.whatwg.org/multipage/server-sent-events.html
