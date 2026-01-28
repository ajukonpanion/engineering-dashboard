# Konpanion Hub  
**Local-First Dashboard & API Hub for Raspberry Pi 5**

Konpanion Hub is a **production-ready, local-first web dashboard** designed to run **24/7 on a Raspberry Pi 5**.  
It can optionally act as its own **Wi-Fi Access Point**, allowing phones and devices to connect directly without internet access.

This repository contains everything needed to deploy, run, and maintain the hub reliably on multiple Raspberry Pi 5 units.

---

## ✨ Key Features

- ✅ Runs 24/7 using **systemd**
- ✅ **FastAPI + Uvicorn** backend
- ✅ **Nginx reverse proxy** (port 80 → 8000)
- ✅ Session-based authentication (login protected dashboard)
- ✅ Optimised for **Raspberry Pi 5**
- ✅ Works in **Wi-Fi AP mode** (local-only access)
- ✅ Clean separation of backend, static files, and templates
- ✅ Designed for reuse across multiple Pi deployments

---

## 🧠 Architecture Overview
Phone / Browser
↓
Wi-Fi (KonpanionHub AP or LAN)
↓
Nginx (port 80)
↓
Uvicorn (127.0.0.1:8000)
↓
FastAPI Application


- **Nginx** handles incoming HTTP requests
- **Uvicorn** runs the FastAPI app
- **FastAPI** serves:
  - Dashboard pages
  - Static assets
  - API endpoints
- **SessionMiddleware** manages login state

---

## 📂 Repository Structure
backend/
├── app/
│ ├── main.py # FastAPI app entry point
│ ├── routers/ # Dashboard, auth, devices, API routes
│ ├── templates/ # HTML pages
│ └── static/ # CSS / JS / favicon
├── run.sh # Local dev run helper
└── requirements.txt


---

## 🚀 Getting Started (Raspberry Pi 5)

### Prerequisites

- Raspberry Pi 5
- Debian 13 (trixie) recommended
- Python 3.11+
- Nginx installed
- (Optional) Ethernet connection for setup

---

### 1️⃣ Clone the repository

```bash
git clone https://github.com/ajukonpanion/engineering-dashboard.git
cd engineering-dashboard


