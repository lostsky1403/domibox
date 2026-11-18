# Catatan Realisme Purwarupa (Prototype Notes & Feasibility Reality) — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 1.0 | 2026-11-15 | omp-orchestrator/UXCore | `docs/00-governance/project-charter.md`<br>`docs/00-governance/documentation-standards.md`<br>`docs/01-product/prd/product-requirements-document.md`<br>`docs/01-product/ux-principles.md`<br>`docs/01-product/ia-and-interaction-spec.md` |

---

## 1. Pernyataan Kejujuran Status Implementasi (Zero Fabricated Prototype)
Sesuai dengan **Prinsip Kejujuran Bukti (*Evidence-Based Engineering*)** yang digariskan dalam `docs/00-governance/documentation-standards.md`:

> **STATUS RESMI SAAT INI:**
> **TIDAK ADA PURWARUPA KODE (CODE PROTOTYPE) MAUPUN DESAIN FIGMA INTERAKTIF YANG TELAH DIIMPLEMENTASIKAN ATAU DI-DEPLOY PADA REPOSITORI/HOST INI.**
>
> Seluruh diagram alur, arsitektur informasi, matriks interaksi, dan sketsa antarmuka yang terdokumentasi dalam `docs/01-product/` berstatus **Rancangan Spesifikasi Teknis Konseptual (*Proposed Conceptual Specifications*)**.

---

## 2. Batas Ruang Lingkup Desain Fase Bootstrap
1. **Tidak Ada Deploy Kode Frontend:** Repositori GitHub `lostsky1403/domibox` berstatus murni dokumentasi tata kelola (*documentation-first bootstrap*). Tidak ada aplikasi React atau build Vite yang dipublikasikan pada fase ini.
2. **Tidak Ada File Desain Biner:** Tidak ada file `.fig`, aset `.pen`, atau tautan purwarupa eksternal yang di-host.
3. **Penyelarasan dengan Alur Kerja Rekayasa Perangkat Lunak:** Implementasi antarmuka pengguna (React, Vite, Tailwind CSS, shadcn/ui) baru diizinkan dimulai setelah seluruh spesifikasi PRD, SRS, STD, dan kontrak API (`openapi.yaml`) disetujui sebagai baseline formal.

---

## 3. Rencana Realisasi Purwarupa Fase Eksekusi (Implementation Readiness)
Ketika fase implementasi kode disetujui oleh pemilik proyek, pengembangan purwarupa antarmuka akan mengikuti urutan pengujian komponen:
1. **Spike 1 (Komponen Generator Alamat):** Pengujian salin 1-klik dan pembuatan token lokal.
2. **Spike 2 (Iframe Sanitasi HTML):** Validasi perilaku `iframe sandbox` DOMPurify terhadap muatan uji XSS (*XSS test payloads*).
3. **Spike 3 (Polling Inbox Realtime):** Verifikasi latensi pembaruan daftar pesan melalui koneksi HTTP polling Fastify.
