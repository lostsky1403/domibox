# Security Requirements & Threat Modeling (STRIDE)

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/SecurityDocs | `docs/02-requirements/security-privacy-requirements.md`<br>`docs/03-architecture/adr/ADR-009.md` |

---

## 1. Sasaran Keamanan Platform
Platform DomiBox mengadopsi prinsip *Defense in Depth*, *Least Privilege*, dan *Zero-Trust Rendering* untuk melindungi privasi pemilik tunggal, mencegah penyalahgunaan infrastruktur email, serta mencegah eksekusi kode berbahaya (XSS) yang berasal dari payload email masuk.

---

## 2. Analisis Ancaman STRIDE (STRIDE Threat Matrix)

| Kategori Ancaman | Komponen / Permukaan Serangan | Skenario Ancaman | Dampak | Kontrol Mitigasi Teknis (`SEC-*`) |
| --- | --- | --- | :---: | --- |
| **Spoofing** | Login Dashboard & Telegram Bot | Penyerang menebak kredensial pemilik atau membajak ID Telegram chat. | Tinggi | `SEC-001`, `SEC-006`: Autentikasi kuat master auth (argon2id + TOTP/Passkey); penautan Telegram wajib pairing token acak TTL 5 menit (`BOT-001`). |
| **Tampering** | Inbound Email Pipeline & DB | Penyerang memodifikasi header email atau memanipulasi kueri SQL mailbox. | Tinggi | `SEC-004`, `SEC-011`: Parameterized queries Drizzle/pg, verifikasi reputasi SPF/DKIM/DMARC inbound, isolasi jaringan bridge Docker. |
| **Repudiation** | Aktivitas Admin & Penghapusan | Penyerang atau skrip menghapus mailbox/domain tanpa jejak audit. | Sedang | `SEC-008`: Immutable append-only audit log (`audit_logs`) mencatat timestamp ISO-8601, IP, ID entitas, dan jenis aksi (`OPS-005`). |
| **Information Disclosure** | Pratinjau Email HTML & OTP | Email phishing/HTML mengandung pelacak (*tracking pixel*) atau kode XSS yang mencuri sesi/token. | Kritis | `SEC-002`, `SEC-005`, `SEC-007`: Token unik SHA-256 mailbox temp (`MBX-001`), sanitasi DOMPurify ketat (`INB-002`), isolasi iframe pratinjau (`WEB-003`), pemblokiran tracking pixel (`INB-003`). |
| **Denial of Service** | Inbound SMTP Port 25 & API | Flooding email masuk masif atau pembuatan ribuan mailbox otomatis. | Tinggi | `SEC-003`, `SEC-009`, `SEC-010`: Rate limiting Fastify (100 req/menit `OPS-004`), kuota penyimpanan ketat 100 MB per permanent mailbox, pembersihan otomatis data kedaluwarsa (`MBX-005`, `OPS-002`, `F4`). |
| **Elevation of Privilege** | API Endpoints & DB Access | Injeksi token atau manipulasi payload untuk mengakses endpoint internal admin. | Tinggi | `SEC-001`, `SEC-002`: Pemeriksaan otorisasi middleware di setiap rute; pembatasan akses database hanya pada peran aplikasi terisolasi. |

---

## 3. Kebijakan Sanitasi HTML & Keamanan Konten (Secure Rendering Policy)
1. **Tidak Ada Eksekusi JavaScript:** Semua tag `<script>`, atribut event `onload`, `onclick`, `onerror`, dan protokol `javascript:` wajib dibersihkan (*stripped*) sebelum disimpan atau ditampilkan.
2. **Isolasi Iframe Pratinjau:** Tampilan email HTML di Web Dashboard wajib menggunakan `<iframe sandbox="allow-same-origin">` tanpa izin `allow-scripts` atau `allow-forms`.
3. **Blokir Pelacak Gambar Eksternal:** Gambar eksternal diblokir secara default (*proxying or click-to-load*) untuk mencegah pengirim melacak alamat IP atau waktu buka email pemilik.
