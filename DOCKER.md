# Docker Deployment Guide

## Overview

The RAG Research Assistant is fully containerized with:
- **Backend**: Python FastAPI in Alpine Linux (lightweight)
- **Frontend**: React built with Node.js, served by Nginx
- **Orchestration**: Docker Compose for multi-container management

## Quick Start (One Command)

```bash
docker-compose up --build
```

**Expected output:**
```
Creating network "dotmappers_rag-network" with driver "bridge"
Building backend
Building frontend
Creating rag-backend ... done
Creating rag-frontend ... done
rag-backend    | INFO:     Started server process [1]
rag-backend    | INFO:     Uvicorn running on http://0.0.0.0:8000
rag-frontend   | nginx: master process started
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- API Health: http://localhost:8000/health

**Stop:**
```bash
docker-compose down
```

---

## Prerequisites

### Required
- Docker (v20.10+): https://www.docker.com/products/docker-desktop
- Docker Compose (v2.0+): Usually bundled with Docker Desktop

### Optional
- `docker` and `docker-compose` CLI tools for advanced operations

### Verify Installation
```bash
docker --version
docker-compose --version
```

---

## Configuration

### Environment Variables

The system uses `.env` file for Gemini API key:

```bash
GEMINI_API_KEY=your_api_key_here
```

**Make sure `.env` exists in project root before running `docker-compose up`**

### Custom Port Mapping

Edit `docker-compose.yml` to change ports:

```yaml
backend:
  ports:
    - "8000:8000"  # Change first 8000 to your desired port

frontend:
  ports:
    - "3000:3000"  # Change first 3000 to your desired port
```

---

## Docker Architecture

### Backend Container

```dockerfile
python:3.12-slim
├── /app/
│   ├── backend/          (RAG pipeline code)
│   ├── data/documents/   (mounted volume)
│   ├── chroma_db/        (persisted vector store)
│   └── eval_log.db       (persisted evaluation logs)
```

**Features:**
- Slim Python image (~150 MB)
- Health checks: Auto-restart on failure
- Volume mounts: Data persists after container stops
- Network: Internal bridge network with frontend

**Port:** 8000 (FastAPI/Uvicorn)

### Frontend Container

```dockerfile
nginx:alpine
├── Stage 1: Node.js builder
│   ├── npm install
│   └── npm run build → /app/build/
├── Stage 2: Nginx server
│   ├── Copy built files → /usr/share/nginx/html
│   └── Serve on port 3000
```

**Features:**
- Multi-stage build: Optimized image size (~30 MB)
- Nginx config: Proxy API calls to backend service
- SPA routing: React Router fallback to index.html
- Health checks: Verify Nginx is responding

**Port:** 3000 (Nginx)

---

## Common Operations

### View Logs

**All services:**
```bash
docker-compose logs -f
```

**Backend only:**
```bash
docker-compose logs -f backend
```

**Frontend only:**
```bash
docker-compose logs -f frontend
```

### Restart Services

**All:**
```bash
docker-compose restart
```

**Backend only:**
```bash
docker-compose restart backend
```

### Stop All Containers

```bash
docker-compose stop
```

### Remove All Containers (Clean)

```bash
docker-compose down
```

### Remove Volumes (Wipe Data)

```bash
docker-compose down -v
```

---

## Troubleshooting

### Backend won't start

**Symptom:** `ERROR: Backend container exited with code 1`

**Solution:**
```bash
# Check logs
docker-compose logs backend

# Ensure .env file exists
ls -la .env

# Rebuild and restart
docker-compose down
docker-compose up --build backend
```

### Frontend shows 502 Bad Gateway

**Symptom:** Nginx can't reach backend

**Solution:**
```bash
# Check backend is healthy
docker-compose ps
# Status should be "Up" and healthy

# Restart both services
docker-compose restart
```

### Cannot connect to http://localhost:3000

**Symptom:** Connection refused

**Solution:**
```bash
# Check if port 3000 is already in use
netstat -an | grep 3000

# If in use, kill the process or change port in docker-compose.yml
# Or wait for service to fully start (can take 30-60s)
docker-compose logs frontend
```

### API calls from frontend timeout

**Symptom:** "Failed to fetch from http://localhost:8000"

**Solution:**
- Nginx config has proxy rule: `proxy_pass http://backend:8000/`
- Frontend requests to `/query` are forwarded to backend service
- Ensure backend container is healthy: `docker-compose ps`

### Rebuild needed after code changes

**For backend changes:**
```bash
docker-compose up --build backend
```

**For frontend changes:**
```bash
docker-compose up --build frontend
```

**For all:**
```bash
docker-compose up --build
```

---

## Production Considerations

### Security

- ✅ Containers run as non-root (default)
- ✅ Environment variables via `.env` (not hardcoded)
- ✅ Health checks prevent unhealthy restarts
- ⚠️ TODO: Use secrets management (Docker Secrets, HashiCorp Vault)
- ⚠️ TODO: Enable HTTPS/TLS in Nginx

### Performance

- ✅ Lightweight base images (python:3.12-slim, nginx:alpine)
- ✅ Multi-stage frontend build (only runtime artifacts in image)
- ✅ Volume mounts for persistent data (fast I/O)
- ⚠️ TODO: Add request rate limiting
- ⚠️ TODO: Configure caching headers in Nginx

### Scaling

- ✅ Docker Compose works for dev/staging
- ⚠️ For production scaling, migrate to:
  - Kubernetes (K8s)
  - AWS ECS
  - Docker Swarm

### Monitoring

- ✅ Health checks configured
- ⚠️ TODO: Add Prometheus metrics
- ⚠️ TODO: Add centralized logging (ELK Stack, Splunk)
- ⚠️ TODO: Add APM (Application Performance Monitoring)

---

## Image Sizes

```bash
docker images | grep rag
```

**Expected sizes:**
- `rag-backend`: ~800 MB (Python + dependencies)
- `rag-frontend`: ~30 MB (Nginx + React build)
- Total: ~830 MB

**To reduce:**
- Use `python:3.12-slim` ✅ (already done)
- Multi-stage frontend build ✅ (already done)
- Remove unnecessary dependencies
- Use `.dockerignore` ✅ (already done)

---

## Networking

### Service Communication

Within Docker Compose, containers communicate via service names:

```
frontend → http://backend:8000/query
           (not localhost:8000)
```

This is handled by Nginx reverse proxy in `frontend/nginx.conf`:
```nginx
upstream backend {
    server backend:8000;
}
```

### External Access

- Frontend: http://localhost:3000 (from host machine)
- Backend: http://localhost:8000 (from host machine)

---

## Volume Mounts

### Persisted Data

```yaml
volumes:
  - ./backend/chroma_db:/app/backend/chroma_db       # Vector store
  - ./backend/eval_log.db:/app/backend/eval_log.db   # Evaluation logs
  - ./data/documents:/app/data/documents             # Source documents
```

**Behavior:**
- Data survives `docker-compose stop`
- Data lost with `docker-compose down -v`
- Data accessible from host machine

---

## Testing the Deployment

### 1. Health Checks

```bash
# All healthy?
docker-compose ps
# Status should show "(healthy)"

# Individual checks
curl http://localhost:8000/health
curl http://localhost:3000/
```

### 2. Full Workflow

1. Open http://localhost:3000
2. Upload a PDF to **Documents tab**
3. Ask a question in **Q&A tab**
4. Check metrics in **Evaluations tab**

### 3. API Test

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the Transformer architecture?"}'
```

---

## CI/CD Integration

### Build Images Locally

```bash
docker-compose build
```

### Push to Docker Hub

```bash
docker tag rag-backend:latest yourdockerhub/rag-backend:latest
docker tag rag-frontend:latest yourdockerhub/rag-frontend:latest
docker push yourdockerhub/rag-backend:latest
docker push yourdockerhub/rag-frontend:latest
```

### Deploy to Remote Server

```bash
# On remote server:
git clone https://github.com/Jyothirmai11-cmk/Dotmappers.git
cd Dotmappers
docker-compose pull
docker-compose up -d
```

---

## Debugging

### Access Container Shell

```bash
# Backend Python shell
docker-compose exec backend bash

# Frontend Nginx shell
docker-compose exec frontend sh
```

### View Container Processes

```bash
docker-compose top backend
docker-compose top frontend
```

### Inspect Container Network

```bash
docker-compose exec backend ping frontend
docker-compose exec frontend wget http://backend:8000/health
```

---

## References

- Docker Docs: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Nginx Proxy: https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- Python Docker Best Practices: https://docs.docker.com/language/python/
