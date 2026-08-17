# Project Context: Datenlens GERMANY

## Architecture Overview
- **Project Name:** Datenlens (Data Analytics & Dashboard Platform for Germany)
- **Primary Domain:** datenlens.de (Live Server IP: 16.171.169.68)
- **Local Dev Path:** `~/datenlens` (Backend) & `~/datenlens-frontend` (Frontend)
- **EC2 Deployment Path:** `/home/ubuntu/datenlens` & `/home/ubuntu/datenlens-frontend`
- **SSH Key:** `~/aws/datenlens-key.pem`

## Tech Stack
- **Backend:** Python 3.10+, FastAPI, Uvicorn, Async HTTPX, Docker/Podman
- **Frontend:** React (Vite), Pure CSS Dark Theme (`--bg-color: #0f172a`), Nginx
- **APIs Integrated:** Tankerkönig MTS-K API (Germany Live Gas Prices)
- **Container Port Mapping:** Frontend (`80:80`), Backend (`10000:10000`)

## Strict Development Rules
1. **Language & UI:** 100% English code, inline comments, labels, UI text, and commit messages. Absolutely NO Persian in source files or UI.
2. **Architecture:** Component-based, scalable Dashboard UI (Overview Widgets + Dedicated Feature Pages).
3. **Deployment Workflow (3-Step Pipeline):**
   - Step 1: Local test & verification on `localhost:5173` & `localhost:10000`.
   - Step 2: Synchronization to EC2 server (`16.171.169.68`).
   - Step 3: Full container rebuild (`--no-cache`) and verification on production domain/IP.
4. **Error Handling:** Always check full build logs and network configurations BEFORE suggesting fixes.
