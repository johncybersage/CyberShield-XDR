# 🛡️ CyberShield XDR Platform

<div align="center">

![CyberShield XDR](https://img.shields.io/badge/CyberShield-XDR%20Platform-00ccff?style=for-the-badge&logo=shield&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![CI](https://img.shields.io/github/actions/workflow/status/yourusername/cybershield-xdr/ci.yml?style=for-the-badge&label=CI)

**AI-Powered Extended Detection and Response Platform**

*Enterprise-grade cybersecurity platform for SOC teams*

[Live Demo](#) · [Documentation](#documentation) · [API Docs](#api-documentation) · [Report Bug](#)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Modules](#modules)
- [Screenshots](#screenshots)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## Overview

CyberShield XDR is a production-quality, AI-powered Extended Detection and Response platform built for enterprise SOC teams. It unifies asset discovery, vulnerability scanning, network intrusion detection, threat intelligence, malware analysis, and phishing detection into a single, modern dashboard.

---

## Features

| Module | Description |
|--------|-------------|
| 🖥️ **Asset Discovery** | Network scanning, OS detection, port/service enumeration |
| 🔍 **Vulnerability Scanner** | Nmap-based scanning with CVE/CVSS mapping and PDF reports |
| 🌐 **Network IDS** | Real-time packet capture, port scan/flood/ARP spoof detection |
| 🌍 **Threat Intelligence** | AbuseIPDB, VirusTotal, AlienVault OTX, MITRE ATT&CK integration |
| 🦠 **Malware Analysis** | Static analysis: PE headers, entropy, strings, YARA rules |
| 📧 **Phishing Detector** | ML-based email analysis with SPF/DKIM/DMARC checks |
| 🤖 **AI SOC Assistant** | GPT-4o powered alert explanation, YARA/Sigma rule generation |
| 🚨 **Alert Management** | Full incident lifecycle with assignment, timeline, and notes |
| 📊 **Dashboard** | Live metrics, interactive charts, attack timeline |
| 📄 **Reporting** | PDF, CSV, Excel executive and incident reports |
| 🔔 **Notifications** | Email, Slack, Discord, browser, webhook delivery |
| 📝 **Audit Logs** | Immutable security event trail |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                 │
│              Rate Limiting · TLS · Security Headers      │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
    ┌──────────▼──────────┐  ┌────────▼────────┐
    │   React Frontend    │  │  FastAPI Backend │
    │  Vite · TypeScript  │  │  Python 3.12     │
    │  TailwindCSS        │  │  SQLAlchemy      │
    │  Framer Motion      │  │  Pydantic        │
    └─────────────────────┘  └────────┬────────┘
                                      │
              ┌───────────────────────┼───────────────────┐
              │                       │                   │
    ┌─────────▼──────┐    ┌──────────▼──────┐  ┌────────▼──────┐
    │   PostgreSQL   │    │     Redis        │  │  OpenSearch   │
    │   Primary DB   │    │  Cache · Queue   │  │  Log Search   │
    └────────────────┘    └─────────────────┘  └───────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │    Celery Workers        │
                         │  Scans · Malware         │
                         │  Reports · Notifications │
                         └─────────────────────────┘
```

---

## Folder Structure

```
cybershield-xdr/
├── backend/            # FastAPI application
│   ├── api/            # API endpoints & routers
│   ├── auth/           # Authentication & JWT logic
│   ├── config/         # App settings & configurations
│   ├── database/       # SQLAlchemy models & sessions
│   ├── services/       # Core business logic (scans, malware, etc.)
│   └── workers/        # Celery background tasks
├── frontend/           # React/Vite application
│   ├── src/components/ # Reusable UI components
│   ├── src/pages/      # Dashboard and feature pages
│   └── src/store/      # Zustand state management
├── docker/             # Docker configuration files
├── docs/               # Additional documentation
└── screenshots/        # Application screenshots
```

---

## Tech Stack

**Backend:** Python 3.12, FastAPI, SQLAlchemy (async), Alembic, Pydantic v2, JWT, Passlib/bcrypt, Redis, Celery, WebSockets, PostgreSQL, OpenSearch

**Frontend:** React 18, Vite, TypeScript, TailwindCSS, Shadcn UI, React Router v6, Axios, Chart.js, Recharts, Framer Motion, Zustand

**Security Tools:** Nmap, Scapy, YARA, pefile, python-magic, scikit-learn

**DevOps:** Docker, Docker Compose, Nginx, GitHub Actions

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/cybershield-xdr.git
cd cybershield-xdr
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys and passwords
```

### 3. Start all services
```bash
docker compose up -d
```

### 4. Run database migrations
```bash
docker compose exec backend alembic upgrade head
```

### 5. Create admin user
```bash
docker compose exec backend python -m backend.utils.create_admin
```

### 6. Access the platform
- **Frontend:** http://localhost
- **API Docs:** http://localhost/api/docs
- **Flower (Celery):** http://localhost:5555

---

## Environment Variables

Ensure the following variables are configured in your `.env` file before starting the application:

| Variable | Description |
|----------|-------------|
| `APP_ENV` | Environment mode (`development`, `production`) |
| `SECRET_KEY` | Core application secret key |
| `JWT_SECRET_KEY` | Secret key for JWT signing |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis cache and session store URL |
| `CELERY_BROKER_URL` | Redis URL for Celery message broker |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery task results |

See `.env.example` for a complete list of optional variables.

---

## Modules

### Module 1 — Asset Discovery
Scans network ranges using Nmap to discover hosts, detect OS, enumerate open ports and running services. Results are stored with full history.

### Module 2 — Vulnerability Scanner
Performs TCP/UDP/version/OS detection scans. Maps discovered services to CVEs via the NVD database. Calculates CVSS scores and generates PDF reports.

### Module 3 — Network IDS
Captures packets using Scapy. Detects port scans, SYN floods, ICMP floods, DNS tunneling, ARP spoofing, and brute force attempts in real time.

### Module 4 — Threat Intelligence
Enriches IPs, domains, and file hashes against AbuseIPDB, VirusTotal, and AlienVault OTX. Maps threats to MITRE ATT&CK techniques.

### Module 5 — Malware Analysis
Performs static analysis on uploaded files: SHA256/MD5 hashing, entropy calculation, PE header parsing, string extraction, and YARA rule matching.

### Module 6 — Phishing Detector
ML-based email analysis combining URL features, sender reputation, header anomalies, and SPF/DKIM/DMARC authentication checks.

### Module 7 — AI SOC Assistant
GPT-4o powered assistant that explains alerts, summarizes incidents, generates YARA/Sigma rules, and produces executive reports.

### Module 8 — Alert Management
Full incident lifecycle management with severity triage, analyst assignment, timeline tracking, notes, and attachments.

---

## Screenshots

### Login
![Login](screenshots/loginpage.png)

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Alerts Management
![Alerts](screenshots/alertspage.png)

### Asset Discovery
![Assets](screenshots/assetspage.png)

### Threat Intelligence
![Threat Intel](screenshots/threadintelligencepage.png)

### Vulnerability Scanner
![Vulnerability Scanner](screenshots/vulnerabilityscannerpage.png)

### Settings
![Settings](screenshots/settingpage.png)

### Admin Panel
![Admin Panel](screenshots/adminpanel.png)

---

## API Documentation

Interactive API documentation available at `/api/docs` (Swagger UI) and `/api/redoc` (ReDoc) in development mode.

**Base URL:** `http://localhost/api/v1`

**Authentication:** Bearer JWT token in `Authorization` header.

---

## Security

- JWT authentication with refresh token rotation
- RBAC with Admin, SOC Analyst, and Viewer roles
- bcrypt password hashing (12 rounds)
- Account lockout after 5 failed attempts
- Rate limiting on all endpoints (stricter on auth)
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- Input validation via Pydantic
- Parameterized queries via SQLAlchemy ORM
- File upload validation (type, size, extension)
- Immutable audit log trail
- Secrets via environment variables only

---

## Testing

```bash
# Backend tests
cd cybershield-xdr
pytest backend/tests/ -v --cov=backend

# Frontend tests
cd frontend
npm test
```

---

## Deployment

See [docs/deployment.md](docs/deployment.md) for production deployment guide including:
- SSL/TLS configuration
- Environment hardening
- Database backup strategy
- Monitoring setup

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

---

## Author

**John K.** — Senior DevOps Engineer & Security Specialist

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with ❤️ for the cybersecurity community
</div>
