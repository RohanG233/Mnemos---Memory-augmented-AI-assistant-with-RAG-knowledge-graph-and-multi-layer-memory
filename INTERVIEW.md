# ACAI — Backend/Frontend Connectivity Deep-Dive

> This document explains how the React frontend and FastAPI backend communicate,
> covering every protocol decision, data contract, authentication flow,
> error handling pattern, and deployment consideration.
> Intended for technical interviews and code reviews.

---

## Table of Contents

1. [Communication Protocol](#1-communication-protocol)
2. [API Base URL Resolution](#2-api-base-url-resolution)
3. [Authentication Flow — End to End](#3-authentication-flow--end-to-end)
   - [Login](#login)
   - [Token Storage](#token-storage)
   - [Authenticated Requests](#authenticated-requests)
   - [Silent Token Refresh](#silent-token-refresh)
   - [Logout](#logout)
4. [The `apiFetch` Function](#4-the-apifetch-function)
5. [CORS Configuration](#5-cors-configuration)
6. [Cookie Configuration](#6-cookie-configuration)
7. [Chat Conversation Flow](#7-chat-conversation-flow)
8. [Data Contracts (Request/Response Shapes)](#8-data-contracts-requestresponse-shapes)
9. [Error Handling Contract](#9-error-handling-contract)
10. [Frontend State Management](#10-frontend-state-management)
11. [LocalStorage and Persistence](#11-localstorage-and-persistence)
12. [RAG Pipeline from the Frontend's Perspective](#12-rag-pipeline-from-the-frontends-perspective)
13. [Document Upload Flow](#13-document-upload-flow)
14. [Memory and Graph — Read-only from the Frontend](#14-memory-and-graph--read-only-from-the-frontend)
15. [Deployment Connectivity](#15-deployment-connectivity)
16. [Security Model](#16-security-model)
17. [Common Interview Questions](#17-common-interview-questions)

---

## 1. Communication Protocol

The frontend and backend communicate exclusively over **HTTPS** (HTTP in local dev) using a **REST API**.

- All request/response bodies are `application/json`
- File uploads use `multipart/form-data`
- No WebSockets, no Server-Sent Events — responses are synchronous HTTP

The API is a standard FastAPI application served by Uvicorn on a single port.
On Render, Render's load balancer terminates TLS and proxies to `uvicorn` over HTTP internally.

---

## 2. API Base URL Resolution

**Frontend** (`frontend/src/services/api.ts`):

```typescript
const API_URL: string =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";
```

`VITE_API_URL` is a Vite build-time environment variable injected from:
- `frontend/.env` — local development
- `frontend/.env.production` — production build

Vite replaces `import.meta.env.VITE_API_URL` with the literal string at build time.
There is no runtime environment variable lookup in the browser bundle.

This means **changing `VITE_API_URL` requires a rebuild** of the frontend.

**Backend** does not know the frontend's URL except through:
- `FRONTEND_URL` — where to redirect the browser after OAuth completes
- `ALLOWED_ORIGINS` — which origins to accept in CORS

---

## 3. Authentication Flow — End to End

### Login

```
Browser                    Frontend (React)            Backend (FastAPI)        Google
  │                              │                           │                     │
  │  click "Continue with        │                           │                     │
  │  Google"                     │                           │                     │
  │─────────────────────────────►│                           │                     │
  │                              │  GET /auth/google         │                     │
  │                              │──────────────────────────►│                     │
  │                              │  {authorization_url}      │                     │
  │                              │◄──────────────────────────│                     │
  │                              │                           │                     │
  │  window.location.href =      │                           │                     │
  │  authorization_url           │                           │                     │
  │◄─────────────────────────────│                           │                     │
  │                              │                           │                     │
  │  redirect to Google          │                           │                     │
  │──────────────────────────────────────────────────────────────────────────────►│
  │                              │                           │                     │
  │  user consents               │                           │                     │
  │                              │                           │                     │
  │  redirect to GOOGLE_REDIRECT_URI?code=...&state=...      │                     │
  │─────────────────────────────────────────────────────────►│                     │
  │                              │                           │                     │
  │                              │                           │  fetch_token(code)  │
  │                              │                           │────────────────────►│
  │                              │                           │  access_token       │
  │                              │                           │◄────────────────────│
  │                              │                           │                     │
  │                              │                           │  GET userinfo       │
  │                              │                           │────────────────────►│
  │                              │                           │  {id, email, name}  │
  │                              │                           │◄────────────────────│
  │                              │                           │                     │
  │                              │                           │  upsert user in     │
  │                              │                           │  MongoDB            │
  │                              │                           │                     │
  │                              │                           │  create JWT (15min) │
  │                              │                           │  create refresh tok │
  │                              │                           │  store refresh tok  │
  │                              │                           │  in MongoDB         │
  │                              │                           │                     │
  │  302 redirect to             │                           │                     │
  │  FRONTEND_URL/chat           │                           │                     │
  │  ?access_token=<JWT>         │                           │                     │
  │  Set-Cookie: refresh_token=  │                           │                     │
  │  <token>; HttpOnly; Secure   │                           │                     │
  │◄─────────────────────────────────────────────────────────│                     │
  │                              │                           │                     │
  │  load /chat                  │                           │                     │
  │─────────────────────────────►│                           │                     │
  │                              │  extractAccessTokenFromUrl()                    │
  │                              │  reads ?access_token from URL                   │
  │                              │  strips it from URL bar                         │
  │                              │  stores in React state (memory only)            │
```

### Token Storage

| Token | Where stored | Accessible to JS? | Lifetime |
|---|---|---|---|
| Access token (JWT) | React state (`useState`) | Yes (intentionally) | 15 minutes |
| Refresh token | HttpOnly cookie | No | 7 days |

The access token is **never written to localStorage or sessionStorage**. It exists only in React component state. If the page is refreshed, the `AuthContext` immediately calls `/auth/refresh` (using the cookie) to get a new access token silently.

The refresh token is **never accessible to JavaScript**. It is only sent by the browser automatically when the origin matches and credentials are included.

### Authenticated Requests

Every API call that requires authentication goes through `apiFetch` in `frontend/src/services/api.ts`:

```typescript
const requestInit: RequestInit = {
  ...options,
  headers: {
    ...options.headers,
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  },
  credentials: "include",   // ensures cookies are sent cross-origin
};
```

The backend extracts the token in `app/auth/dependencies.py`:

```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> str:
    token = credentials.credentials
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return payload["sub"]   # user_id (MongoDB ObjectId as string)
```

### Silent Token Refresh

When `apiFetch` receives a `401`:

```typescript
if (response.status !== 401) return response;

// Try refresh
const newToken = await refreshHandler();
if (!newToken) return response;

// Retry with new token
return fetch(url, { ...init, headers: { ...headers, Authorization: `Bearer ${newToken}` } });
```

`refreshHandler` is registered by `AuthContext` via `setRefreshHandler(refresh)`.
It calls `POST /auth/refresh` with `credentials: "include"`, which sends the HttpOnly cookie.

The backend:
1. Reads the `refresh_token` cookie
2. Looks up the user in MongoDB by `refresh_token`
3. Checks expiry
4. Issues a new JWT
5. Issues a new refresh token (rotation)
6. Writes the new refresh token to MongoDB
7. Returns `{access_token}` + sets a new `Set-Cookie` header

### Logout

```typescript
// frontend
await fetch(`${API_URL}/auth/logout`, { method: "POST", credentials: "include" });
setAccessToken(null);
```

```python
# backend
# Removes refresh_token from MongoDB
# Deletes the cookie by setting max_age=0
response.delete_cookie(key="refresh_token", ...)
```

After logout, the refresh token is invalidated in MongoDB and the cookie is cleared.
The JWT remains valid until its 15-minute expiry (standard JWT trade-off — no server-side JWT revocation).

---

## 4. The `apiFetch` Function

`frontend/src/services/api.ts` is the single point of contact between the frontend and the backend.

It wraps `fetch` with:

1. **Authorization header injection** — adds `Bearer <token>` if a token is present
2. **Cookie forwarding** — `credentials: "include"` ensures the HttpOnly refresh cookie is sent on every request, including to a different origin (cross-origin)
3. **Automatic 401 retry** — if the request fails with 401, it silently refreshes the token and retries once

All service files (`chatService.ts`, `uploadService.ts`, etc.) call `apiFetch` rather than calling `fetch` directly. This means the 401 retry logic is centralised and consistent.

---

## 5. CORS Configuration

**Why CORS matters here**: The frontend (e.g. `https://acai-frontend.onrender.com`) and backend (`https://acai-backend.onrender.com`) are different origins. The browser blocks cross-origin requests unless the server sends correct CORS headers.

**Backend configuration** (`app/main.py`):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # exact list, never "*"
    allow_credentials=True,          # required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

`allow_credentials=True` **requires** that `allow_origins` is an explicit list, not `["*"]`.
If `allow_origins=["*"]` is used with `allow_credentials=True`, browsers reject the request.

`ALLOWED_ORIGINS` comes from the environment variable of the same name.

**Frontend**: `credentials: "include"` is set on every request in `apiFetch`.
This is what causes the browser to include the `refresh_token` cookie on cross-origin requests.

**SameSite=None**: Because the cookie crosses origins (frontend ≠ backend), the cookie must be `SameSite=None; Secure`. The backend sets this when `COOKIE_SECURE=true`.

---

## 6. Cookie Configuration

| Attribute | Local dev | Production |
|---|---|---|
| `HttpOnly` | true | true |
| `Secure` | false (`COOKIE_SECURE=false`) | true (`COOKIE_SECURE=true`) |
| `SameSite` | `lax` | `none` |
| `Path` | `/` | `/` |
| `Max-Age` | 7 days | 7 days |

`SameSite=None` is required when the cookie must be sent from a different origin.
`SameSite=None` **requires** `Secure=true` — browsers reject `SameSite=None` without `Secure`.
This is why `COOKIE_SECURE` must be `true` in production even though Render terminates TLS externally.

In local development, both the frontend (`localhost:5173`) and backend (`localhost:8000`) are `localhost`, so `SameSite=Lax` works and `Secure=false` allows HTTP.

---

## 7. Chat Conversation Flow

The conversation ID flow is critical and often misunderstood.

**Wrong approach (pre-fix)**: the frontend was creating a local UUID (`crypto.randomUUID()`) and sending it to the backend as `conversation_id`. The backend would return 404 because it had never created that conversation.

**Correct approach (current)**:

```
1. User opens Chat page
2. useChat hook mounts, reads rooms from localStorage
3. If no rooms found:
   POST /chat/conversations
   → backend creates conversation in MongoDB
   → returns { conversation_id: "<uuid>", title: "New Chat" }
   → frontend stores this as room.conversationId

4. User types a message and clicks Send
5. Frontend calls POST /chat with:
   { message: "...", conversation_id: room.conversationId }

6. Backend:
   a. Verifies conversation exists AND belongs to this user
   b. Saves user message to MongoDB
   c. Runs RAG pipeline
   d. Saves assistant response to MongoDB
   e. Returns { answer: "...", ... }

7. Frontend adds both messages to UI and saves to localStorage
```

The `room.id` (local UUID) is used only as a React key for list rendering.
The `room.conversationId` (server UUID) is what gets sent to the backend.

---

## 8. Data Contracts (Request/Response Shapes)

### Chat Request
```typescript
// Frontend sends
interface ChatRequest {
  message: string;
  conversation_id: string;  // server-assigned UUID
}
```

```python
# Backend expects (Pydantic model)
class ChatRequest(BaseModel):
    message: str
    conversation_id: str
```

### Chat Response
```typescript
// Frontend receives
interface ChatResponse {
  answer: string;
  retrieved_chunks: string[];
  memories: string[];
  episodes: string[];
  procedures: string[];
  graph_facts: string[];
}
```

```python
# Backend returns
class ChatResponse(BaseModel):
    answer: str
    retrieved_chunks: list[str] = []
    memories: list[str] = []
    episodes: list[str] = []
    procedures: list[str] = []
    graph_facts: list[str] = []
```

The frontend renders only `answer`. The other fields are available for debugging but not shown in the UI.

### Auth Refresh Response
```typescript
interface RefreshResponse {
  access_token: string;
}
```

### Error Response (all endpoints)
```json
{
  "detail": "Human-readable error message"
}
```

The frontend reads `error?.detail` from error responses.

---

## 9. Error Handling Contract

| HTTP Status | Meaning | Frontend behaviour |
|---|---|---|
| `200` | Success | Normal flow |
| `400` | Bad request (invalid input) | Show `error.detail` to user |
| `401` | Unauthenticated | Trigger refresh, retry once, redirect to /login if still 401 |
| `403` | Forbidden | Show error |
| `404` | Not found | Show error |
| `413` | Payload too large | Show "file too large" |
| `422` | Validation error | Show `error.detail` |
| `500` | Internal server error | Show generic error |
| `503` | Service unavailable (Ollama down) | Show "AI model unavailable" |

The backend never exposes Python tracebacks in production responses.
FastAPI's default 422 validation errors include field-level detail which the frontend logs but does not display verbatim.

---

## 10. Frontend State Management

ACAI uses no global state management library (no Redux, no Zustand). State is managed through:

| State | Where | How |
|---|---|---|
| Access token | `AuthContext` (`useState`) | Shared via React Context |
| Loading state | `useAuth`, `useChat`, `useUpload` | Local hook state |
| Chat rooms | `useChat` | Local state + localStorage |
| Active room ID | `useChat` | Local state |
| Messages | `useChat` (derived from rooms) | Derived from rooms array |
| Documents | `useUpload` | Local state, fetched on mount |
| Memories | `useMemories` | Local state, fetched on mount |
| Graph | `useGraph` | Local state, fetched on mount |

### Why no global state library?

The application has clear data ownership: each page owns its own data, and the only truly global piece of state is the access token. React Context is sufficient for this.

### Stale state avoidance

In `useChat.send()`, the assistant message is appended using a snapshot of the state captured after the user message was added:

```typescript
const afterUser = rooms.map(...);     // snapshot with user message
updateRooms(afterUser);               // optimistic update

const response = await sendMessage(...);

const afterAssistant = afterUser.map(...);  // build from snapshot, not from current state
updateRooms(afterAssistant);
```

This avoids the "stale closure" problem where `rooms` inside a `then()` callback would still reference the pre-update value.

---

## 11. LocalStorage and Persistence

Chat rooms are persisted to `localStorage` under the key `acai_chat_rooms`.

**What is stored per room:**
```typescript
{
  id: string;              // local UUID (React key only)
  conversationId?: string; // server UUID (sent to backend)
  title: string;
  messages: ChatMessage[]; // full message history
  createdAt: number;
  updatedAt: number;
}
```

**Migration guard** (`chatStorage.ts`):
```typescript
return rooms.filter((r) => r.conversationId);
```

Rooms without a `conversationId` are from an older version of the code and are filtered out on load. The hook then creates a new room with a proper server-assigned ID.

**Race condition fix** (`useChat.ts`):

A `loadComplete` boolean flag ensures the auto-create effect only fires after the localStorage read has been committed to React state:

```typescript
const [loadComplete, setLoadComplete] = useState(false);

useEffect(() => {
  const saved = getChatRooms();
  if (saved.length > 0) {
    setRooms(saved);
    setActiveRoomId(saved[0].id);
  }
  setLoadComplete(true);  // signal that load is done
}, []);

useEffect(() => {
  if (!loadComplete || !accessToken) return;  // wait for both
  if (rooms.length === 0) createNewRoom();
}, [loadComplete, accessToken]);
```

Without `loadComplete`, the second effect could fire before the first effect's `setRooms` has committed, incorrectly seeing `rooms.length === 0` and creating a new room.

---

## 12. RAG Pipeline from the Frontend's Perspective

From the frontend's perspective, the chat endpoint is a black box:

```
POST /chat
Body: { message, conversation_id }
Response: { answer, retrieved_chunks, memories, episodes, procedures, graph_facts }
```

Inside the backend, the following happens synchronously before the response is sent:

1. **Validate** — conversation exists and belongs to this user
2. **Persist** user message to MongoDB
3. **BM25 search** — keyword search over user's document chunks
4. **Vector search** — semantic search via ChromaDB embedding query
5. **Deduplicate** — merge BM25 and vector results, remove duplicates
6. **Graph retrieval** — find entities from the query in the user's graph, return 2-hop neighbourhood
7. **Memory retrieval** — query ChromaDB for relevant semantic/episodic/procedural memories
8. **Build prompt** — assemble system prompt with all context sections
9. **LLM call** — send to Ollama, wait for response (up to `LLM_TIMEOUT` seconds)
10. **Persist** assistant response to MongoDB
11. **Background updates** (still synchronous in current implementation):
    - Extract triples from the user message, update graph
    - Classify and store new memories
12. **Return response**

The frontend shows a loading indicator (animated dots) for the duration of this entire pipeline. There is no streaming — the full response arrives at once.

---

## 13. Document Upload Flow

```
Frontend                        Backend
   │                                │
   │  POST /documents/upload        │
   │  Content-Type: multipart/form-data
   │  Authorization: Bearer <token>
   │  Body: file=<binary>           │
   │───────────────────────────────►│
   │                                │  validate filename (path traversal guard)
   │                                │  check extension (.txt only)
   │                                │  check size (≤ 10 MB)
   │                                │  decode UTF-8
   │                                │  split into chunks (500 chars, 70 overlap)
   │                                │  embed chunks → store in ChromaDB
   │                                │  add to per-user BM25 index
   │                                │  extract triples (LLM) → update graph
   │  200 { document_id, chunks }   │
   │◄───────────────────────────────│
```

The frontend does not send the file to a temporary URL or pre-signed URL. It uploads directly to the FastAPI endpoint using `FormData`.

Deletion removes:
- All ChromaDB entries with matching `document_id`
- The corresponding chunks from the in-process BM25 index
- All graph edges sourced from this `document_id`

---

## 14. Memory and Graph — Read-only from the Frontend

The memory and graph endpoints are **read-only** from the frontend.

Memories and graph entries are created entirely as a **side effect of chatting and uploading documents**. The user never directly creates or deletes them through the UI.

- `GET /memories` — semantic memories (personal facts)
- `GET /memories/episodes` — significant conversation events
- `GET /memories/procedures` — behavioural instructions
- `GET /graph` — all nodes and edges for this user

All queries are filtered by `user_id` on the backend. Users cannot read each other's data.

---

## 15. Deployment Connectivity

In production on Render:

```
Browser
  │
  │  HTTPS
  ▼
Render CDN/Load Balancer
  │
  ├──► acai-frontend.onrender.com  (Render Static Site)
  │    Serves index.html + JS bundle
  │    VITE_API_URL baked in at build time
  │
  └──► acai-backend.onrender.com   (Render Web Service)
       FastAPI + Uvicorn
       │
       ├──► MongoDB Atlas          (external, HTTPS)
       ├──► Ollama                 (localhost:11434 or external VPS)
       └──► ChromaDB               (local persistent disk /data/chroma_db)
```

**Critical constraint**: `VITE_API_URL` is a build-time constant in the frontend JavaScript bundle. The frontend JavaScript literally contains the string `https://acai-backend.onrender.com` after building. There is no runtime configuration file.

This means if the backend URL ever changes, the frontend must be rebuilt and redeployed.

**Cookie cross-origin requirement**: Because frontend and backend are on different subdomains (not same origin), the refresh token cookie must be:
- `Secure` (HTTPS only)
- `SameSite=None` (cross-site cookie allowed)

Render always serves over HTTPS, so `COOKIE_SECURE=true` is correct.

---

## 16. Security Model

### User isolation

Every piece of user data is scoped by `user_id`:

```python
# All MongoDB queries
conversations_collection.find({"user_id": user_id, ...})

# All ChromaDB queries
collection.get(where={"user_id": user_id}, ...)
collection.query(where={"user_id": user_id}, ...)

# All graph files
get_graph_path(user_id) → data/graphs/{user_id}.json
```

A user cannot read or modify another user's data because every query includes their own `user_id`, derived from the validated JWT.

### JWT validation

```python
payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
```

`python-jose` verifies:
- Signature (using `JWT_SECRET_KEY`)
- Expiry (`exp` claim)
- Algorithm (`alg` header must match)

If any check fails, `JWTError` is raised and the dependency returns HTTP 401.

### What happens if JWT_SECRET_KEY leaks?

An attacker can forge JWTs with any `user_id`. This gives them full access to any user's data. **Rotate the key immediately** and all existing tokens become invalid.

### Refresh token security

- Stored as a cryptographically random 64-byte URL-safe string (`secrets.token_urlsafe(64)`)
- Stored in MongoDB against the user's document
- Rotated on every use (old token is invalidated, new token issued)
- HttpOnly cookie — not readable by JavaScript even on the frontend origin
- Expires after 7 days

---

## 17. Common Interview Questions

**Q: Why use both an access token and a refresh token?**

Short-lived access tokens (15 min) limit the window of abuse if a token is intercepted. Long-lived refresh tokens (7 days, HttpOnly cookie) allow seamless re-authentication without the user re-entering credentials. The refresh token is never accessible to JavaScript, so XSS cannot steal it.

**Q: Why not store the access token in localStorage?**

localStorage is accessible to any JavaScript on the page, including injected scripts (XSS). React state (in-memory) is not persistent across page refreshes, but the silent refresh on mount (via the HttpOnly cookie) immediately restores it. The trade-off: if Ollama is down and the page refreshes, the user sees a 503 on their next message rather than being logged out.

**Q: Why is VITE_API_URL a build-time variable?**

Vite's `import.meta.env` variables are replaced with literal strings during `vite build`. This is intentional — it means there is no server-side rendering or runtime config file needed. The downside is that changing the backend URL requires a rebuild.

**Q: What happens if Ollama is down?**

`LLMService.generate()` raises `LLMUnavailableError`. The chat endpoint catches this and returns HTTP 503 with `{"detail": "The AI model is currently unavailable."}`. The frontend displays this as a chat error. All other features (auth, documents, memory browsing, graph) continue to work normally.

**Q: Why use ChromaDB for memories instead of MongoDB?**

Memories need to be retrieved by semantic similarity (embedding distance), not by exact match. ChromaDB is a vector database that supports efficient approximate nearest-neighbour search over embeddings. MongoDB does not support vector search in the free tier. ChromaDB also stores the embeddings themselves, so re-querying does not require re-embedding.

**Q: How does user isolation work in ChromaDB?**

ChromaDB's `where` filter is passed to every query:
```python
collection.query(query_embeddings=[...], where={"user_id": user_id}, ...)
```
ChromaDB supports metadata filtering. All documents, memories, episodes, and procedures are stored with `{"user_id": user_id}` in their metadata, and all queries filter on this field.

**Q: What is Reciprocal Rank Fusion and why use it?**

RRF combines ranked lists from multiple retrievers (BM25 and vector) into a single ranked list without needing to calibrate the scores from each retriever. Score from each ranker: `1 / (k + rank)`. Documents appearing near the top of multiple rankers get higher fused scores. It is effective because BM25 is good at keyword matching while vector search is good at semantic similarity — they are complementary.

**Q: Why is `--workers 1` set for Uvicorn?**

The BM25 index and short-term `ConversationMemory` are held in process memory as Python dictionaries. Multiple workers would have separate copies of these, causing consistency issues (e.g., a document indexed by worker 1 is invisible to worker 2). For horizontal scaling, these would need to be externalised to Redis or a database. The `--workers 1` flag makes this limitation explicit.

**Q: What is the conversation ID race condition and how was it fixed?**

When `useChat` mounts, two React effects run:
1. Load rooms from localStorage → `setRooms(saved)` (async)
2. If `rooms.length === 0` and `accessToken` is set → create a new room

Because React batches state updates, effect 2 could see `rooms.length === 0` before effect 1's `setRooms` has committed — even if rooms were found in localStorage. The fix: a `loadComplete` boolean state is set after the load is done, and effect 2 waits for `loadComplete === true` before checking `rooms.length`.

**Q: How does the access token reach the frontend after OAuth?**

OAuth flows with a redirect cannot carry JSON bodies — they use HTTP redirects (302). The backend appends the access token as a URL query parameter: `FRONTEND_URL/chat?access_token=<JWT>`. The frontend reads this in `extractAccessTokenFromUrl()`, stores it in React state, and immediately strips it from the URL bar using `window.history.replaceState`. This avoids the token appearing in browser history or being logged by proxies.

**Q: Why does the frontend filter legacy rooms from localStorage?**

Before the conversation ID refactor, rooms were stored with a locally-generated `id` that was sent to the backend. After the fix, rooms have a `conversationId` field containing the server-assigned UUID. Old rooms in localStorage lack this field. Filtering them out prevents the frontend from trying to send an invalid `conversation_id` to the backend and getting a 404.
