# Deployment & Orchestration Specification — DomiBox Platform

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/TechSpec | `docs/07-operations/deployment-architecture.md`<br>`docs/03-architecture/diagrams/deployment-diagram.md`<br>`docs/03-architecture/adr/ADR-001.md`<br>`docs/03-architecture/adr/ADR-011.md` |

---

## 1. Lingkungan Infrastruktur Target (Node Spesifikasi)
Platform DomiBox dideploy pada infrastruktur komputasi mandiri (*self-hosted node*) yang telah divalidasi pada inspeksi pra-terbang 2026-11-14:
- **Hosting Provider:** Tencent Cloud (CVM).
- **Host Alias:** `vps-tencent3b`.
- **Operating System:** Ubuntu 24.04.5 LTS (Kernel Linux 6.8).
- **CPU & RAM:** 2 vCPU AMD EPYC 7K62, total RAM 3.6 GiB (~3.0 GiB tersedia), swap 1.9 GiB.
- **Penyimpanan:** 59 GB NVMe SSD (~50 GB ruang bebas tersedia).
- **Runtime:** Docker Engine 29.9.3, Docker Compose v5.7.0.

---

## 2. Konfigurasi Layanan Docker Compose (Orchestration Spec)

```yaml
# docker-compose.prod.yml (Spesifikasi Produksi DomiBox)
version: '3.8'

networks:
  domibox-public:
    driver: bridge
  domibox-internal:
    driver: bridge
    internal: true

volumes:
  postgres_data:
  caddy_data:
  caddy_config:
  stalwart_data:
  mail_spool:

services:
  caddy:
    image: caddy:2-alpine
    container_name: domibox-caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
      - ./frontend/dist:/srv/frontend:ro
    networks:
      - domibox-public
      - domibox-internal
    depends_on:
      - api
    mem_limit: 128m

  api:
    image: domibox/core-api:latest
    container_name: domibox-api
    restart: unless-stopped
    environment:
      NODE_ENV: production
      DATABASE_URL: postgres://domibox_app:${DB_PASSWORD}@postgres:5432/domibox
      MASTER_AUTH_SECRET: ${MASTER_AUTH_SECRET}
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      STALWART_JMAP_URL: http://stalwart:8080/jmap
      STALWART_ADMIN_SECRET: ${STALWART_ADMIN_SECRET}
    volumes:
      - mail_spool:/var/spool/domibox
    networks:
      - domibox-internal
    depends_on:
      - postgres
      - stalwart
    mem_limit: 512m

  stalwart:
    image: stalwartlabs/mail-server:latest
    container_name: domibox-mail
    restart: unless-stopped
    ports:
      - "25:25"      # Inbound SMTP port publik (F1)
    volumes:
      - stalwart_data:/opt/stalwart-mail
      - mail_spool:/var/spool/mail
    networks:
      - domibox-public
      - domibox-internal
    mem_limit: 768m

  postgres:
    image: postgres:16-alpine
    container_name: domibox-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: domibox
      POSTGRES_USER: domibox_app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - domibox-internal
    mem_limit: 384m
```

---

## 3. Matriks Alokasi Sumber Daya (Budgeting RAM & CPU)
Total pagu alokasi memori (*memory limits*) yang diatur pada kontainer DomiBox adalah **1.79 GiB**, yang secara aman berada di bawah kapasitas RAM bebas VPS (~3.0 GiB available), menyisakan minimal 1.2 GiB memori fisik dan 1.9 GiB swap untuk sistem operasi Ubuntu dan aplikasi independen yang berjalan di host.
