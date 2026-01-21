# 🚀 Mahakaal Deployment Guide
This document details the server configuration and deployment process for Mahakaal.

## 🖥️ Server Details (Oracle Cloud Infrastructure)

| Parameter | Value |
| :--- | :--- |
| **Public IP** | `147.224.205.129` |
| **Domain** | `mahakaal.abhijithsetty.com` |
| **SSH User** | `ubuntu` |
| **OS** | Ubuntu 24.04 LTS (AArch64) |
| **Instance Type** | VM.Standard.A1.Flex (4 OCPU, 24GB RAM) |
| **Project Path** | `/home/ubuntu/mahakaal` |

### 🔑 SSH Access
To access the server terminal:
```bash
ssh ubuntu@147.224.205.129
```
*(Requires your private SSH key to be added to the agent or specified via `-i`)*

---

## 🛠️ Application Architecture

The application runs on Docker Compose with the following services:

1.  **Nginx (Reverse Proxy)**
    *   **Port**: 80 (Public)
    *   **Function**: Serves the frontend and proxies `/api` requests to the backend.
2.  **Frontend (React/Vite)**
    *   **Internal Port**: 80
    *   **Based on**: Nginx Alpine image
3.  **Backend (FastAPI)**
    *   **Internal Port**: 8000
    *   **Database**: SQLite (`mahakaal_chats.db`) & JSON (`events.json`) - *Mounted Volumes*

---

## 📦 Deployment Process

You can deploy updates using the included script or manually.

### Option 1: Using the Script (Recommended)
This script syncs your local files to the server and rebuilds the containers.
```bash
./deploy_app.sh
```

### Option 2: Manual Deployment

1.  **Sync Code**:
    ```bash
    rsync -avz --exclude 'node_modules' --exclude 'venv' --exclude '.git' ./ ubuntu@147.224.205.129:~/mahakaal
    ```

2.  **SSH into Server**:
    ```bash
    ssh ubuntu@147.224.205.129
    ```

3.  **Rebuild Containers**:
    ```bash
    cd ~/mahakaal
    sudo docker compose up -d --build
    ```

---

## ⚙️ Configuration & Secrets

Environment variables are managed in the `.env` file on the server.
**File Path**: `/home/ubuntu/mahakaal/backend/.env`

**Current Production Config**:
```env
OPENAI_API_KEY=sk-... (your key)
REDIRECT_URI=http://mahakaal.abhijithsetty.com/api/auth/callback
FRONTEND_URL=http://mahakaal.abhijithsetty.com
```

> [!IMPORTANT]
> If you update `.env` on the server, you must restart the backend:
> `sudo docker compose restart backend`

---

## 🚨 Troubleshooting

**View Logs**:
```bash
# All logs
sudo docker compose logs -f

# Backend only
sudo docker compose logs -f backend
```

**Restart Services**:
```bash
sudo docker compose restart
```

**Check Status**:
```bash
sudo docker compose ps
```
