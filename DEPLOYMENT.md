# ACAI Deployment Guide

## Prerequisites

- Python 3.11
- Node.js 20+
- MongoDB Atlas account (free tier works)
- Google Cloud Console project with OAuth 2.0 credentials
- Render account (for backend deployment)
- Vercel, Netlify, or Render Static Site (for frontend)

---

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=acai
JWT_SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
OLLAMA_URL=http://localhost:11434/api/chat
LLM_MODEL=hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest
LLM_TIMEOUT=120
CHROMA_PATH=./data/chroma_db
GRAPH_DIRECTORY=./data/graphs
COOKIE_SECURE=false
```

Start Ollama separately:

```bash
ollama serve
ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest
```

Start backend:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

Start frontend:

```bash
npm run dev
```

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URL` | Yes | MongoDB Atlas connection string |
| `MONGODB_DATABASE` | No | Database name (default: `acai`) |
| `JWT_SECRET_KEY` | **Yes** | Strong random secret for JWTs |
| `JWT_ALGORITHM` | No | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Default: `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | Default: `7` |
| `GOOGLE_CLIENT_ID` | **Yes** | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | **Yes** | From Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | **Yes** | Must match exactly in Google Console |
| `FRONTEND_URL` | **Yes** | Where browser is sent after login |
| `ALLOWED_ORIGINS` | **Yes** | Comma-separated CORS origins |
| `OLLAMA_URL` | No | Default: `http://localhost:11434/api/chat` |
| `LLM_MODEL` | No | Ollama model name |
| `LLM_TIMEOUT` | No | Request timeout in seconds (default: `120`) |
| `CHROMA_PATH` | No | ChromaDB storage path |
| `GRAPH_DIRECTORY` | No | Graph JSON storage path |
| `COOKIE_SECURE` | No | Set `false` only for HTTP dev (default: `true`) |

---

## MongoDB Setup

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a database user with read/write access
3. Whitelist `0.0.0.0/0` in Network Access (or Render's IP range)
4. Copy the connection string — replace `<username>` and `<password>`
5. Set `MONGODB_URL` in Render environment variables

---

## Google OAuth Setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → APIs & Services → OAuth consent screen
3. Create OAuth 2.0 Client ID (Web application)
4. Add Authorized Redirect URIs:
   - Development: `http://localhost:8000/auth/google/callback`
   - Production: `https://YOUR-BACKEND.onrender.com/auth/google/callback`
5. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in Render

---

## Ollama in Production — IMPORTANT

### The Problem

Render web services are standard Linux containers. Ollama is a separate
process that serves LLM inference. Running Ollama **inside** a Render web
service is technically possible but has significant constraints:

- **Free tier**: 512 MB RAM — insufficient for any useful LLM model
- **Paid starter tier (2 GB RAM)**: sufficient only for the smallest
  quantized models (e.g. Llama-3.2-1B Q4)
- Render does not provide GPU instances on standard plans
- Model files are large (500 MB–8 GB) and re-downloaded on every deploy
  unless a persistent disk is attached

### Recommended Architecture Options

#### Option A: Render + Persistent Disk (Simplest, Low Cost)

Run Ollama as a background process via a startup script on a Render
**paid** instance with a persistent disk.

1. Upgrade to Render Starter ($7/month)
2. Add a persistent disk at `/data` (1 GB minimum)
3. Create `backend/start.sh`:

```bash
#!/bin/bash
set -e

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama in background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Ollama ready."
    break
  fi
  sleep 2
done

# Pull model only if not already cached on persistent disk
MODEL="${LLM_MODEL:-hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest}"
if ! ollama list | grep -q "$MODEL"; then
  echo "Pulling model: $MODEL"
  OLLAMA_MODELS=/data/ollama ollama pull "$MODEL"
fi

# Start FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
```

Set `startCommand` in `render.yaml` to: `bash start.sh`

Set env var `OLLAMA_MODELS=/data/ollama` so models persist across restarts.

**Trade-offs**: Cold starts are slow (model pull on first deploy). The
application starts correctly but LLM calls will fail if Ollama is still
initialising — the `LLMService.is_available()` check handles this gracefully.

#### Option B: Separate Ollama Service (More Reliable)

Run Ollama on a separate always-on machine or cloud instance:

- A $5/month VPS (e.g. DigitalOcean, Hetzner) running `ollama serve`
- Set `OLLAMA_URL=http://<vps-ip>:11434/api/chat` in Render env vars
- Restrict port 11434 to Render's IP range for security

#### Option C: Hugging Face Inference Endpoints (Paid)

Deploy the model to HuggingFace Inference Endpoints and point
`OLLAMA_URL` at a compatible endpoint. Requires modifying
`LLMService` to match their API format.

#### Option D: Keep Local for Now

If you are not ready for production LLM hosting, run the backend
**without** deploying Ollama to Render. The backend will start and
serve all routes. Chat endpoints will return HTTP 503 with a clear
error message when Ollama is unavailable.

### What The Application Does When Ollama is Unavailable

The `LLMService` raises `LLMUnavailableError` on connection failure.
The chat endpoint catches this and returns:

```json
{"detail": "The AI model is currently unavailable. Please try again later."}
```

with HTTP status `503`. All other endpoints (auth, documents, memories,
graph) continue to work normally.

---

## Render Backend Deployment

1. Push code to GitHub
2. Create a new **Web Service** on Render
3. Connect your GitHub repo
4. Set Root Directory: `backend`
5. Set Build Command: `pip install -r requirements.txt`
6. Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Set Python Version: `3.11` (via `runtime.txt`)
8. Add all environment variables from the table above
9. If using ChromaDB persistence: add a Persistent Disk at `/data`
   and update `CHROMA_PATH=/data/chroma_db` and `GRAPH_DIRECTORY=/data/graphs`

---

## Frontend Deployment

### Build

```bash
cd frontend
# Set your production backend URL
echo "VITE_API_URL=https://YOUR-BACKEND.onrender.com" > .env.production
npm run build
# dist/ is the static site to deploy
```

### Vercel

```bash
npm i -g vercel
cd frontend
vercel --prod
# Set VITE_API_URL in Vercel project settings
```

### Render Static Site

1. Create a new **Static Site** on Render
2. Root Directory: `frontend`
3. Build Command: `npm install && npm run build`
4. Publish Directory: `dist`
5. Add environment variable: `VITE_API_URL=https://YOUR-BACKEND.onrender.com`

---

## Persistence Limitations on Render Free Tier

**Render free tier uses ephemeral storage.**

This means:
- ChromaDB data (`data/chroma_db/`) is **wiped on every deploy or restart**
- Knowledge graph JSON files (`data/graphs/`) are **also wiped**
- In-process BM25 indexes and short-term memory are already in-memory

**Impact:**
- Uploaded documents must be re-uploaded after each restart
- Knowledge graph is reset
- Semantic/episodic/procedural memories in ChromaDB are lost
- MongoDB data (users, conversations, messages) persists normally

**Mitigation:**
- Upgrade to Render paid tier and attach a Persistent Disk
- Mount it at `/data`
- Set `CHROMA_PATH=/data/chroma_db` and `GRAPH_DIRECTORY=/data/graphs`

---

## CORS Configuration

`ALLOWED_ORIGINS` must exactly match the frontend's origin.

Example:
```
ALLOWED_ORIGINS=https://acai-frontend.vercel.app
```

Multiple origins:
```
ALLOWED_ORIGINS=https://acai-frontend.vercel.app,https://custom-domain.com
```

Do **not** use `*` — cookies require explicit origins.

---

## Known Limitations

1. **Ollama on Render free tier is not practical** — see Ollama section above
2. **ChromaDB is not persistent on Render free tier** — must use paid disk
3. **Short-term memory (ConversationMemory) is in-process** — lost on restart;
   MongoDB stores durable history so users can reload conversations
4. **BM25 index is in-process** — rebuilt from ChromaDB at startup; requires
   ChromaDB persistence to survive restarts
5. **Knowledge graph files require persistent storage** — same as ChromaDB
6. **Graph extraction runs an LLM call per sentence** during document upload —
   this will be slow or fail if Ollama is unavailable
