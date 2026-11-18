# Requirements Assumptions & Evidence Gaps Register

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Requirements Lead / Orchestrator (ReqTrace)`  
**Related Documents:**
- `docs/00-governance/project-charter.md`
- `docs/00-governance/open-questions.md`
- `docs/00-governance/decision-log.md`
- `docs/02-requirements/traceability/traceability-matrix.md`
- `docs/09-research/problem-value-research.md`
- `docs/09-research/competitive-comparative-research.md`
- `docs/09-research/mail-infrastructure-suitability.md`
- `docs/09-research/ux-pattern-benchmark.md`

---

## 1. Tujuan (Purpose)
Dokumen ini mendokumentasikan secara formal seluruh asumsi tingkat kebutuhan (*requirements-level assumptions*), batasan, dan celah pembuktian bukti riset (*evidence gaps*). Tujuan pencatatan ini adalah mencegah terjadinya klaim palsu atau implementasi berbasis asumsi liar, serta memandu fase arsitektur dan teknis selanjutnya agar tetap memiliki pijakan auditabilitas yang solid.

---

## 2. Taksonomi Status Bukti (Evidence Status Taxonomy)
Sesuai dengan `docs/00-governance/documentation-standards.md`, setiap entitas data atau klaim diklasifikasikan ke dalam:
- **`VERIFIED` (Terverifikasi):** Terdapat bukti empiris, pengujian langsung, atau rujukan sumber terverifikasi dalam repositori.
- **`ASSUMPTION` (Asumsi):** Dugaan logis rekayasa yang belum divalidasi dengan sumber primer namun diperlukan untuk kelangsungan perancangan.
- **`PROPOSED` (Usulan):** Rekomendasi desain atau kebutuhan yang diajukan untuk disetujui pemangku kepentingan.
- **`GAP` (Celah Bukti / Tidak Diketahui):** Informasi yang tidak ditemukan pada repositori riset dan wajib diselesaikan via penyelidikan lebih lanjut.

---

## 3. Register Asumsi Kebutuhan (Requirements Assumptions Register)

| ID Asumsi | Deskripsi Asumsi | Kategori | Dasar Pemikiran / Konteks | Dampak Jika Tidak Valid | Status Bukti | Isu Terkait | Tindakan Mitigasi |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **A-REQ-001** | DomiBox melayani kebutuhan pengguna tunggal (*single-tenant/self-hosted*) dan/atau tim tertutup, bukan platform publik komersial multi-tenant massal pada rilis MVP. | Cakupan Produk | Penyederhanaan arsitektur MVP dan pengurangan risiko penyalahgunaan spam besar-besaran. | Arsitektur skema basis data dan penanganan isolasi pengguna perlu dirancang ulang total. | `ASSUMPTION` | `Q-003` | Verifikasi batasan MVP dengan pemilik proyek sebelum membekukan SRS. |
| **A-REQ-002** | Pengguna memiliki kontrol penuh terhadap konfigurasi DNS domain yang akan didaftarkan (mampu menambahkan record MX, TXT, dan CNAME). | Integrasi Domain | Verifikasi kepemilikan domain dan perutean email masuk memerlukan record MX terarah ke server DomiBox. | Alur onboarding domain akan gagal total bagi pengguna tanpa akses DNS level domain. | `ASSUMPTION` | `DOM-001` | Sediakan instruksi langkah demi langkah verifikasi DNS dan panduan fallback. |
| **A-REQ-003** | Server hosting memiliki IP publik statis dengan port 25 inbound terbuka dan tidak diblokir oleh penyedia cloud/ISP. | Infrastruktur | Penerimaan email masuk langsung via SMTP membutuhkan port 25 terbuka. | Penerimaan email masuk harus beralih ke penyedia pihak ketiga atau integrasi webhook/API email relay. | `ASSUMPTION` | `INB-001`, `RISK-007` | Lakukan pengecekan konektivitas jaringan VPS (lihat `mail-infrastructure-suitability.md`). |
| **A-REQ-004** | Masa retensi default untuk pesan pada mailbox sementara adalah 1 jam hingga 24 jam sebelum dihapus permanen secara otomatis. | Kebijakan Data | Menghemat ruang penyimpanan disk dan menjamin privasi email sementara. | Penumpukan kuota penyimpanan lokal atau keluhan pengguna jika email terhapus terlalu cepat. | `PROPOSED` | `MBX-001`, `OPS-001` | Parameter konfigurasi TTL dibuat dapat disesuaikan per domain atau jenis mailbox. |
| **A-REQ-005** | Format ekstraksi kode OTP dapat diandalkan menggunakan kombinasi pencarian kata kunci multi-bahasa (Indonesia & Inggris) dan ekspresi reguler (4–8 digit numerik/alfanumerik). | Fungsionalitas Parser | Mayoritas layanan verifikasi menggunakan pola standar seperti "kode verifikasi", "OTP", "verification code", "security code". | Tingkat kegagalan deteksi kode OTP tinggi pada email yang memiliki format non-standar atau berbasis gambar. | `ASSUMPTION` | `OTP-001` | Menyediakan antarmuka cadangan untuk membaca email mentah utuh jika parser gagal mengekstraksi kode. |
| **A-REQ-006** | Pengguna menginginkan notifikasi instan melalui Telegram Bot sebagai kanal alternatif di luar web dashboard. | Interaksi Pengguna | Pola benchmark UX (`ux-pattern-benchmark.md`) menunjukkan adopsi bot pesan instan meningkatkan kemudahan akses kode OTP. | Modul bot menjadi beban pemeliharaan jika pengguna hanya menggunakan antarmuka web. | `PROPOSED` | `BOT-001` | Modul bot dirancang independen (*loosely coupled*) sehingga dapat diaktifkan/dinonaktifkan secara modular. |

---

## 4. Register Celah Bukti Riset (Evidence Gaps Register)

| ID Celah | Pertanyaan Terbuka Terkait | Deskripsi Celah Bukti | Dokumen Terdampak | Dampak Terhadap Kebutuhan | Rencana Verifikasi / Tindak Lanjut |
| --- | --- | --- | --- | --- | --- |
| **GAP-001** | `Q-001` | Dokumen sumber primer untuk *Problem-Value Research* tidak ditemukan dalam pencarian sesi awal. | `docs/09-research/problem-value-research.md`, `BR-001`, `BR-003` | Validasi masalah pengguna riil (pain points) dan proposisi nilai belum berakar pada data empiris riset pengguna formal. | Tandai placeholder `docs/09-research/problem-value-research.md` sebagai `PROPOSED`. Lakukan wawancara pengguna atau studi literatur independen sebelum fase penutupan PRD. |
| **GAP-002** | `Q-002` | Dokumen sumber primer untuk *Competitive-Comparative Research* tidak ditemukan dalam pencarian sesi awal. | `docs/09-research/competitive-comparative-research.md`, strategi pemosisian fitur | Matriks komparasi terhadap kompetitor (misalnya MailSlurp, Guerrilla Mail, Temp-Mail, Cloudflare Email Routing) didasarkan pada pengetahuan sekunder umum, bukan audit data primer terverifikasi. | Tandai placeholder sebagai `PROPOSED`. Jadwalkan *Spike Task* untuk mengaudit fitur teknis kompetitor dan merevisi dokumen komparasi. |
| **GAP-003** | `Q-003` | Batasan fungsional tegas antara kapabilitas mailbox sementara (*disposable*) dan mailbox permanen (*persistent*) belum disahkan oleh pemilik produk. | `PRD`, `BR-001`, `MBX-001`, `MBX-002`, `traceability-matrix.md` | Risiko *scope creep* di mana sistem bergeser menjadi penyedia layanan email lengkap (*full-blown mail client*) dengan fitur kirim email, folder bersarang, dan kalender. | Eksplisitkan bahwa MVP hanya berfokus pada **inbound reception**, ekstraksi OTP, dan mailbox sementara, sedangkan mailbox permanen tingkat lanjut masuk ke Fase 2. |
| **GAP-004** | `Q-004` | Model autentikasi dan otorisasi antarmuka web dashboard belum diputuskan (apakah berbasis Master API Key, akun multi-user, WebAuthn/Passkey, atau sesi sementara). | `SEC-002`, `SEC-003`, `SEC-006`, `ADR-004` (Pending) | Mempengaruhi arsitektur basis data, session store, dan mekanisme isolasi mailbox. | Buat usulan arsitektur dengan autentikasi berbasis Master Secret/Token untuk MVP single-user, dan siapkan skema RBAC untuk pengembangan selanjutnya. |

---

## 5. Hubungan dengan Keputusan Tata Kelola (Traceability to Governance Decisions)
- **`DEC-001`:** Seluruh asumsi dan celah bukti menggunakan format ID kanonikal (`A-REQ-###` dan `GAP-###`) untuk memastikan keterlacakan lintas dokumen.
- **`DEC-003`:** Kebijakan tata kelola melarang fabrikasi data; oleh karena itu, ketiadaan data riset wajib dinyatakan sebagai `GAP` yang dipetakan langsung ke pertanyaan terbuka `Q-001` dan `Q-002`.
