# Error Catalogue & Standard Error Envelopes

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/TechSpec | `docs/04-technical/api/openapi.yaml`<br>`docs/00-governance/documentation-standards.md` |

---

## 1. Standar Format Amplop Respon Error (Standard Envelope)
Setiap kegagalan pemanggilan API mengembalikan format JSON standar (*Standard Error Envelope*) dengan status HTTP yang sesuai:

```json
{
  "success": false,
  "error": {
    "code": "ERR_DOMAIN_VERIFICATION_FAILED",
    "message": "Rekaman DNS MX atau TXT tidak ditemukan atau tidak cocok dengan token verifikasi.",
    "details": {
      "domain": "sintaksis.biz.id",
      "expectedRecord": "domibox-verify=d82fa0192e104",
      "detectedRecord": null
    },
    "timestamp": "2026-11-15T02:00:00.000Z"
  }
}
```

---

## 2. Katalog Kode Kesalahan Sistem (Error Code Matrix)

| Kategori | Kode Kesalahan | HTTP Status | Deskripsi & Penyebab | Langkah Penanganan Klien |
| --- | --- | :---: | --- | --- |
| **Auth** | `ERR_AUTH_INVALID_CREDENTIALS` | 401 | Kredensial username atau password salah. | Periksa kembali username/password pemilik. |
| **Auth** | `ERR_AUTH_TOKEN_EXPIRED` | 401 | Token JWT sesi kedaluwarsa. | Lakukan login ulang untuk memperbarui token. |
| **Auth** | `ERR_AUTH_FORBIDDEN` | 403 | Sesi tidak memiliki wewenang untuk aksi ini. | Pastikan sesi terdaftar sebagai role OWNER. |
| **Domain** | `ERR_DOMAIN_NOT_FOUND` | 404 | Domain ID yang diminta tidak terdaftar. | Periksa ID domain pada daftar domain aktif. |
| **Domain** | `ERR_DOMAIN_ALREADY_EXISTS` | 409 | Nama domain sudah pernah didaftarkan. | Gunakan domain yang sudah ada atau hapus terlebih dahulu. |
| **Domain** | `ERR_DOMAIN_VERIFICATION_FAILED`| 422 | Rekaman DNS MX atau TXT gagal diverifikasi. | Konfigurasikan DNS di Cloudflare sesuai instruksi. |
| **Mailbox**| `ERR_MAILBOX_NOT_FOUND` | 404 | Mailbox ID tidak ditemukan. | Periksa kembali daftar mailbox. |
| **Mailbox**| `ERR_MAILBOX_CONFLICT` | 409 | Alamat email (local_part@domain) sudah digunakan.| Pilih local part lain atau buat alamat acak baru. |
| **Mailbox**| `ERR_MAILBOX_EXPIRED` | 410 | Mailbox sementara telah melewati batas waktu TTL. | Buat mailbox baru; perpanjangan waktu telah habis. |
| **Message**| `ERR_MESSAGE_NOT_FOUND` | 404 | Email ID tidak ditemukan atau telah di-purge. | Segarkan tampilan inbox. |
| **Parser** | `ERR_EMAIL_MIME_PARSE_ERROR` | 422 | Struktur email RFC822 korup / gagal diurai. | Email dipindahkan ke folder dead-letter / quarantine. |
| **Telegram**|`ERR_TELEGRAM_PAIR_EXPIRED` | 400 | Kode pairing bot Telegram kedaluwarsa (>5 menit). | Minta kode pairing baru dari Web Dashboard. |
| **System** | `ERR_RATE_LIMIT_EXCEEDED` | 429 | Ambang batas frekuensi request terlampaui. | Tunggu beberapa detik sebelum mencoba kembali. |
| **System** | `ERR_INTERNAL_SERVER_ERROR` | 500 | Kesalahan tidak terduga pada server/database. | Periksa log kontainer Fastify / PostgreSQL. |
| **Engine** | `ERR_STALWART_COMMUNICATION` | 502 | Gagal berkomunikasi dengan JMAP/HTTP Stalwart. | Periksa apakah service Docker stalwart berjalan. |
