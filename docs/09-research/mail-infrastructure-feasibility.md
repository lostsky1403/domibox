# Riset Kelayakan Infrastruktur Email (Mail Infrastructure Feasibility) — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/ResearchCore | `docs/00-governance/project-charter.md`<br>`docs/00-governance/open-questions.md`<br>`docs/03-architecture/architecture-overview.md`<br>`docs/03-architecture/tech-evaluation-matrix.md`<br>`docs/03-architecture/adr/ADR-002.md`<br>`docs/03-architecture/adr/ADR-010.md`<br>`docs/09-research/mail-infrastructure-suitability.md` |

---

## 1. Tujuan & Ruang Lingkup Riset
Riset ini memvalidasi kelayakan teknis, jaringan, dan lisensi dari komponen infrastruktur email untuk platform mandiri (*self-hosted*) **DomiBox** pada VPS target Tencent Cloud dan DNS Cloudflare. Riset ini menyelaraskan temuan mendalam dari `docs/09-research/mail-infrastructure-suitability.md` ke dalam format ringkas berlabel bukti kanonikal (*Evidence Labels*).

---

## 2. Register Bukti Infrastruktur Inti (F1–F6 Evidence Register)

Setiap fakta infrastruktur ditandai dengan label ketat sesuai standar tata kelola:
- `VERIFIED`: Diverifikasi langsung melalui inspeksi host, pengujian jaringan/DNS, atau dokumentasi resmi vendor yang diaudit.
- `NOT VERIFIED / PROPOSED`: Hipotesis atau pengamatan awal yang memerlukan pengujian penetrasi/validasi runtime lebih lanjut.
- `ASSUMPTION`: Asumsi kerja arsitektur yang dijadikan dasar batas cakupan MVP.

| ID Fakta | Parameter / Aspek | Temuan Empiris & Justifikasi Teknis | Status Bukti | Rujukan Dokumen / Sumber |
| :---: | --- | --- | :---: | --- |
| **F1** | Kebijakan Port 25 Tencent Cloud | Port TCP 25 **Inbound** terbuka dan dapat dikendalikan melalui Tencent Security Group & UFW. Port TCP 25 **Outbound** diblokir secara permanen oleh Tencent Cloud untuk pencegahan spam publik. Konsekuensi: MVP dibatasi 100% pada *inbound-only* (penerimaan email). | `VERIFIED` | Inspeksi CVM Tencent Cloud, `ADR-010`, `docs/09-research/mail-infrastructure-suitability.md` Bagian 2.1 |
| **F2** | Batasan Lisensi Stalwart Mail Server | Stalwart v1.0.3 Community Edition berlisensi AGPL-3.0. Fitur bawaan *Masked Email* merupakan fitur berbayar (*Enterprise-only*). DomiBox harus mengimplementasikan siklus hidup alamat sementara menggunakan primitif *virtual alias* dan *JMAP API* bawaan Community Edition. | `VERIFIED` | Audit Dokumentasi & Lisensi Stalwart v1.0.3, `ADR-002`, `ADR-003` |
| **F3** | Konflik Cloudflare Email Routing | Mengaktifkan *Cloudflare Email Routing* pada domain apex (`sintaksis.biz.id`) akan menimpa rekaman DNS MX ke server Cloudflare (`route*.mx.cloudflare.net`), sehingga paket SMTP port 25 tidak diarahkan ke IP VPS. Solusi: Gunakan rekaman MX langsung ke IP VPS, atau delegasikan subdomain terpisah (`mail.sintaksis.biz.id`). | `VERIFIED` | Pengujian DoH Cloudflare DNS & Evaluasi Konflik MX, `SRS.md`, `ADR-010` |
| **F4** | Ketiadaan Otomatisasi TTL Bawaan Stalwart | Stalwart Community Edition tidak memiliki scheduler internal untuk kedaluwarsa otomatis alamat email (*TTL auto-purge*). Logika penghitungan masa aktif dan penghapusan virtual alias wajib dieksekusi oleh Background Worker DomiBox melalui panggilan JMAP Management API. | `VERIFIED` | Spesifikasi JMAP RFC 8620/8621, Stalwart API Audit, `ADR-003`, `ADR-011` |
| **F5** | Keterbatasan Jaringan IPv6 Host | VPS Tencent Cloud (`vps-tencent3b`) yang dialokasikan tidak memiliki alamat IPv6 publik aktif (hanya antarmuka IPv4 statis `43.153.206.84`). Konsekuensi: Seluruh konfigurasi listener SMTP, reverse proxy Caddy, dan rekaman DNS A/AAAA hanya menggunakan IPv4. | `VERIFIED` | Inspeksi antarmuka jaringan Linux (`ip a`), `ADR-010` |
| **F6** | Otoritas DNS Domain Pilot | Domain pilot `sintaksis.biz.id` terdaftar pada Cloudflare Nameserver (`dylan.ns.cloudflare.com`, `kristina.ns.cloudflare.com`). Saat preflight, domain belum memiliki rekaman MX aktif. Pengaturan MX direct VPS memerlukan intervensi Cloudflare API atau dashboard. | `VERIFIED` | Resolusi DoH `https://cloudflare-dns.com/dns-query`, `Project Charter`, `ADR-010` |

---

## 3. Matriks Evaluasi Alternatif Mail Server Engine

| Kriteria / Metrik | Stalwart Mail Server (v1.0.3) | Mailu (Docker) | Mail-in-a-Box | Haraka SMTP |
| --- | :---: | :---: | :---: | :---: |
| **Konsumsi RAM (Idle / Peak)** | ~150 MB / ~250 MB | >1.5 GB (8 kontainer) | ~800 MB - 1.2 GB | ~120 MB / ~200 MB |
| **Bahasa & Runtime** | Rust murni (asinkron Tokio) | Python + Postfix + Dovecot | Shell + Postfix + Dovecot | Node.js (Event-driven) |
| **Manajemen API** | Native JMAP (RFC 8620/8621) + REST | REST API terbatas | Bash CLI internal | Plugin JavaScript kustom |
| **Dukungan Multi-Domain** | Bawaan (Virtual domains/aliases) | Bawaan matang | Terbatas pada setup primer | Butuh konfigurasi plugin |
| **Penyimpanan Pesan (Store)** | Built-in Blob/RocksDB/S3 | Dovecot Maildir | Dovecot Maildir | Tidak ada (SMTP receiver saja) |
| **Kesesuaian VPS 3.6 GB RAM** | **Sangat Baik (Terpilih)** | Tidak Layak (Boros RAM) | Kurang Layak | Baik (Namun butuh store terpisah) |
| **Status Verifikasi** | `VERIFIED` (`ADR-002`) | `VERIFIED` (`ADR-002`) | `VERIFIED` (`ADR-002`) | `VERIFIED` (`ADR-002`) |

---

## 4. Analisis Kelayakan Aliran Ingress & Egress SMTP

### 4.1 Ingress SMTP (Port 25 Inbound)
- **Status:** `FEASIBLE` (Layak / Terverifikasi).
- **Mekanisme:** Listener Stalwart mengikat port `0.0.0.0:25` pada kontainer Docker. Trafik dari internet diteruskan langsung melalui Docker port mapping.
- **Validasi Keamanan:** Stalwart secara otomatis mengeksekusi pemeriksaan SPF, DKIM, dan DMARC pada tahap handshake SMTP untuk menandai reputasi email masuk.

### 4.2 Egress SMTP (Port 25 Outbound)
- **Status:** `BLOCKED` (Tidak Layak untuk MVP tanpa Relay).
- **Penyebab:** Kebijakan pemblokiran ISP Tencent Cloud (`F1`).
- **Pilihan Mitigasi Pasca-MVP:**
  1. Pengajuan unblock port 25 melalui tiket resmi Tencent Cloud (memerlukan verifikasi identitas korporat dan domain terdaftar).
  2. Integrasi layanan SMTP Relay pihak ketiga terpercaya (misal: Resend, SendGrid, Amazon SES) melalui port 587/465 terenkripsi TLS (`ADR-010`).

---

## 5. Ringkasan Rekomendasi Arsitektur
1. Mengadopsi **Stalwart Mail Server v1.0.3 Community** sebagai engine email tunggal terpadu (`ADR-002`).
2. Menggunakan **Virtual Alias Routing** untuk mailbox sementara guna menghindari batasan enterprise `F2` dan efisiensi memori (`ADR-003`).
3. Menetapkan batasan MVP sebagai **Inbound-Only** untuk menyelaraskan diri dengan kondisi riil jaringan Tencent Cloud `F1` (`mvp-scope.md`).
4. Mengoperasikan **DomiBox Core Purge Engine** secara independen untuk menegakkan kedaluwarsa TTL `F4` (`ADR-011`).
