# Environment, Deployment & Operational Runbook Strategy

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/OperationsDocs | `docs/03-architecture/diagrams/deployment-diagram.md`<br>`docs/03-architecture/capacity-planning.md` |

---

## 1. Topologi Lingkungan Operasional (VPS Pilot)
Platform DomiBox dirancang untuk dijalankan pada VPS Linux tunggal dengan spesifikasi yang telah diverifikasi:
- **Penyedia Hosting:** Tencent Cloud (wilayah pilot `vps-tencent3b`).
- **Sistem Operasi:** Ubuntu 24.04.5 LTS (Kernel Linux 6.8+).
- **Alokasi Sumber Daya:** 2 vCPU AMD EPYC 7K62, ~3.6 GiB RAM fisik, ~1.9 GiB Swap, ~50 GiB sisa disk tersedia.
- **Orkestrasi Kontainer:** Docker Engine 29.x + Docker Compose v2.x.
- **Konfigurasi Jaringan & Firewall:** UFW aktif (Port 22 SSH, Port 25 SMTP inbound publik, Port 80/443 HTTP/HTTPS publik). Port basis data internal (5432) dan JMAP internal (8081) terisolasi dalam Docker bridge network `domibox-internal`.

---

## 2. Definisi Kontainer Layanan (Service Topology)

```yaml
# Ilustrasi Arsitektur Docker Compose (docker-compose.yml)
version: '3.8'

services:
  reverse-proxy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - domibox-internal

  domibox-core:
    build: .
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://domibox:securepass@postgres:5432/domibox_db
      - STALWART_JMAP_URL=http://stalwart:8080/jmap
    depends_on:
      - postgres
      - stalwart
    networks:
      - domibox-internal

  stalwart:
    image: stalwartlabs/mail-server:v1.0.3
    restart: unless-stopped
    ports:
      - "25:25"   # Inbound SMTP langsung dari internet
    volumes:
      - stalwart_data:/opt/stalwart-mail
    networks:
      - domibox-internal

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=domibox_db
      - POSTGRES_USER=domibox
      - POSTGRES_PASSWORD=securepass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - domibox-internal

networks:
  domibox-internal:
    driver: bridge

volumes:
  caddy_data:
  caddy_config:
  stalwart_data:
  postgres_data:
```

---

## 3. Strategi Cadangan, Pemulihan Bencana & Auto-Purge
1. **Pencadangan Basis Data Otomatis:** Script cron harian mengeksekusi `pg_dump` terkompresi ke direktori terisolasi dengan retensi rotasi 7 hari.
2. **Pembersihan Otomatis (*Auto-Purge*):**
   - Mailbox sementara: TTL habis -> alias dinonaktifkan di Stalwart -> data pesan dan lampiran dihapus permanen (*hard delete*) setelah grace period 24 jam.
   - Mailbox permanen: Pesan dapat disimpan sesuai kebijakan pemilik atau dihapus manual.
3. **Prosedur Pemulihan (Disaster Recovery):** Restore basis data dari dump file `psql < backup.sql` dan sinkronisasi ulang state alias ke engine Stalwart via API reconciliation worker.
