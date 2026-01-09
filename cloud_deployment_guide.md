# Cloud Deployment Guide

Moving Mahakaal from local Docker to the cloud requires updating your authentication flow and ensuring data persistence.

## 1. Google Cloud Console Updates
Google OAuth is strict about redirect URIs. When you have a cloud domain (e.g., `mahakaal.yourdomain.com`), you must:
- Go to [Google Cloud Console](https://console.cloud.google.com/).
- Navigate to **APIs & Services > Credentials**.
- Edit your OAuth 2.0 Client ID.
- Add `https://mahakaal-api.yourdomain.com/auth/callback` to the **Authorized redirect URIs**.

## 2. Backend Configuration
Update `backend/auth.py` or use an environment variable to change the `REDIRECT_URI`:
```python
# In backend/auth.py
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
```

## 3. Frontend Configuration
The frontend currently assumes the backend is at `localhost:8000`. You'll need to update your API calls (usually in a `.env` or config file) to point to your cloud API URL.

## 4. Environment Variables & Secrets
Securely provide these to your cloud container service (e.g., GCP Cloud Run, AWS ECS, or Render):
- `OPENAI_API_KEY`
- `REDIRECT_URI` (pointing to your cloud callback)
- `credentials.json` (as a secret or mounted file)

## 5. Persistent Storage (CRITICAL)
In Docker Compose, we used local volumes. In the cloud, ensure you mount a **Persistent Volume** to `/app` (or specifically for `token.json` and `events.json`).
- **Why?** Without this, the agent will lose its login token every time the container restarts, forcing you to re-authenticate constantly.

## 6. Recommended Providers
- **Render / Railway**: Easiest for Docker Compose-like setups.
- **Google Cloud Run**: Native, scalable, and works well with Google APIs.
- **Vercel (Frontend) + Render (Backend)**: Common split-hosting approach.

## 7. Kubernetes (K8s) vs. PaaS
Is Kubernetes "better"? It depends on your scale and expertise.

| Feature | PaaS (Render, Cloud Run) | Kubernetes (GKE, EKS) |
| :--- | :--- | :--- |
| **Complexity** | Low (few clicks/commands) | High (Learning curve) |
| **Cost** | Fixed or Pay-per-use | Higher (Control plane + Node fees) |
| **Management** | Zero-maintenance | Requires constant management |
| **Scaling** | Vertical/Simple Horizontal | Infinite (if configured right) |

### When to use Kubernetes:
- You need complex networking between many microservices.
- You want to practice enterprise DevOps.
- You need high-availability with multi-region failover.

### When to stick to PaaS (Recommended for Mahakaal):
- This is a personal agent (single user/small group).
- You want to spend time on features, not infrastructure.
- You want the best price-to-performance ratio for a small app.

> [!TIP]
> If you choose Kubernetes, you'll need **Manifests** (YAML files) for your Deployment, Services, and Ingress. I can generate these for you if you'd like to proceed with K8s!
