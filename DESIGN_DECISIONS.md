# Mnemos — Design Decisions

Every significant architectural and technical choice made in this project,
with the reasoning, alternatives considered, and why this approach was chosen.

---

## Table of Contents

1. [LLM Runtime — Ollama](#1-llm-runtime--ollama)
2. [LLM Model — Llama 3.2 1B GGUF (quantized)](#2-llm-model--llama-32-1b-gguf-quantized)
3. [Vector Database — ChromaDB](#3-vector-database--chromadb)
4. [Primary Database — MongoDB Atlas](#4-primary-database--mongodb-atlas)
5. [Embedding Model — all-MiniLM-L6-v2](#5-embedding-model--all-minilm-l6-v2)
6. [Full-Text Search — BM25 (bm25s)](#6-full-text-search--bm25-bm25s)
7. [Retrieval Fusion — Reciprocal Rank Fusion (RRF)](#7-retrieval-fusion--reciprocal-rank-fusion-rrf)
8. [Knowledge Graph — NetworkX + JSON files](#8-knowledge-graph--networkx--json-files)
9. [Triple Extraction — LLM-based](#9-triple-extraction--llm-based)
10. [Memory Architecture — Three separate collections](#10-memory-architecture--three-separate-collections)
11. [Memory Decay — Score-based forgetting](#11-memory-decay--score-based-forgetting)
12. [Short-term Memory — In-process rolling window](#12-short-term-memory--in-process-rolling-window)
13. [Text Splitting — RecursiveCharacterTextSplitter](#13-text-splitting--recursivecharactertextsplitter)
14. [Web Framework — FastAPI](#14-web-framework--fastapi)
15. [ASGI Server — Uvicorn (single worker)](#15-asgi-server--uvicorn-single-worker)
16. [Authentication — Google OAuth + JWT](#16-authentication--google-oauth--jwt)
17. [Token Storage — React state (access) + HttpOnly cookie (refresh)](#17-token-storage--react-state-access--httponlycookie-refresh)
18. [Token Strategy — Short-lived JWT + rotating refresh tokens](#18-token-strategy--short-lived-jwt--rotating-refresh-tokens)
19. [CORS Strategy — Explicit origins, credentials: include](#19-cors-strategy--explicit-origins-credentials-include)
20. [Conversation ID — Server-assigned UUID](#20-conversation-id--server-assigned-uuid)
21. [Frontend Framework — React + Vite + TypeScript](#21-frontend-framework--react--vite--typescript)
22. [State Management — React Context + custom hooks (no library)](#22-state-management--react-context--custom-hooks-no-library)
23. [Chat Persistence — LocalStorage + MongoDB](#23-chat-persistence--localstorage--mongodb)
24. [Graph Visualisation — ReactFlow (@xyflow/react)](#24-graph-visualisation--reactflow-xyflowreact)
25. [Markdown Rendering — react-markdown](#25-markdown-rendering--react-markdown)
26. [Deployment Platform — Render](#26-deployment-platform--render)
27. [Frontend Deployment — Render Static Site](#27-frontend-deployment--render-static-site)
28. [Persistent Storage — Render Disk (for ChromaDB + graphs)](#28-persistent-storage--render-disk-for-chromadb--graphs)
29. [Service Architecture — Two separate Render services](#29-service-architecture--two-separate-render-services)
30. [RAG Architecture — Hybrid BM25 + vector, no reranker](#30-rag-architecture--hybrid-bm25--vector-no-reranker)
31. [Error Isolation — Per-step try/except in RAG pipeline](#31-error-isolation--per-step-tryexcept-in-rag-pipeline)
32. [File Upload — Plain HTTP multipart, .txt only](#32-file-upload--plain-http-multipart-txt-only)
33. [Cookie SameSite Strategy — None in production, Lax in dev](#33-cookie-samesite-strategy--none-in-production-lax-in-dev)
34. [Graph Storage — Atomic write (tmp + rename)](#34-graph-storage--atomic-write-tmp--rename)
35. [User Isolation — user_id on every record](#35-user-isolation--user_id-on-every-record)

---

## 1. LLM Runtime — Ollama

**What it is**: Ollama is a local LLM inference server. It runs quantized models on CPU or GPU and exposes a simple HTTP API (`/api/chat`).

**Why it was chosen**:
- Zero API cost — runs entirely on your own hardware
- No data sent to third-party servers — full privacy
- Supports hundreds of models through a single unified API
- Simple to install and operate
- The `LLMService` abstraction makes the URL and model name fully configurable

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| OpenAI GPT-4o | Pay-per-token cost, user data leaves the machine, requires internet |
| Anthropic Claude | Same issues as OpenAI |
| Google Gemini API | Same issues |
| Hugging Face Inference API | Rate-limited free tier, data sent externally |
| vLLM | More complex setup, designed for multi-GPU server deployments |
| llama.cpp directly | No HTTP API — would require subprocess calls or C bindings |

**Trade-off**: Ollama running on consumer hardware is significantly slower and less capable than a cloud-hosted frontier model. The 1B parameter model chosen here responds in seconds on a CPU, making it practical for development.

---

## 2. LLM Model — Llama 3.2 1B GGUF (quantized)

**What it is**: A 1-billion parameter instruction-tuned language model quantized to 4-bit precision using the GGUF format. The specific variant is `hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF`.

**Why it was chosen**:
- Small enough to run on CPU with ~1 GB RAM
- Fast enough for interactive use (~2–10 second response times on modern hardware)
- Instruction-tuned — follows system prompts and JSON format instructions
- Available directly via Ollama without manual download
- Suitable for the structured tasks in Mnemos (triple extraction, memory classification, RAG generation)

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Llama 3.2 3B | More capable but 3× the RAM and slower on CPU |
| Llama 3.1 8B | Better quality but requires ~6 GB RAM, impractical on free Render |
| Mistral 7B | Good quality but same RAM constraint |
| Phi-3 Mini | Similar size, slightly less instruction following quality |
| TinyLlama 1.1B | Older model, weaker instruction following |

**Trade-off**: 1B models are not highly capable reasoners. They will occasionally ignore instructions, produce inconsistent JSON, or give incomplete answers. The code is defensive against this (JSON parse fallbacks, empty result handling).

---

## 3. Vector Database — ChromaDB

**What it is**: An open-source embedded vector database that stores text, embeddings, and metadata. It runs in-process or as a persistent server and supports metadata filtering.

**Why it was chosen**:
- Runs embedded in the FastAPI process — no separate service to manage
- Supports persistent storage (`PersistentClient`) — data survives restarts
- Built-in `where` filter for metadata — critical for user isolation without extra code
- Works directly with `sentence-transformers` embedding functions
- Free, open-source, no API keys

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Pinecone | Managed cloud service — cost, data sent externally, free tier has limited namespaces |
| Weaviate | Heavier deployment, separate service required |
| Qdrant | Good alternative but adds a separate service/container |
| pgvector (PostgreSQL) | Requires a PostgreSQL instance; overkill for this scale |
| FAISS | In-memory only, no persistence without manual serialisation, no metadata filtering |
| Milvus | Designed for large-scale deployments, too heavy for this use case |

**Trade-off**: ChromaDB on a Render persistent disk requires a paid plan ($7/mo). On the free tier, the disk is ephemeral and all vectors are lost on restart.

---

## 4. Primary Database — MongoDB Atlas

**What it is**: A managed cloud NoSQL document database. Used to store users, conversations, and messages.

**Why it was chosen**:
- Free tier (512 MB) is sufficient for user data and conversation history
- Flexible document schema — conversations and messages have varying shapes
- Atlas handles connection pooling, backups, and failover
- `pymongo` is mature, well-documented, and synchronous (compatible with FastAPI's threaded endpoints)
- Built-in indexes for `user_id` + `updated_at` queries (conversation listing)
- Survives Render restarts — cloud-hosted, not on the Render service

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| PostgreSQL (Supabase/Neon) | SQL schema is rigid for message/memory data; free tiers are smaller or have compute limits |
| SQLite | File-based, would need to live on Render's ephemeral disk; not suitable for production |
| Redis | Good for sessions but not a primary store; persistence is secondary |
| DynamoDB | AWS-specific, more complex IAM setup, less familiar |
| Firestore | Google Cloud lock-in; more complex querying |

**Trade-off**: MongoDB's free tier has a 512 MB storage limit. For a personal assistant with moderate use this is more than enough. At scale, sharding would be needed.

---

## 5. Embedding Model — all-MiniLM-L6-v2

**What it is**: A 22M parameter sentence embedding model from Hugging Face. It maps text to 384-dimensional vectors optimised for semantic similarity.

**Why it was chosen**:
- Very small (80 MB) — runs on CPU in milliseconds
- Good semantic similarity scores on standard benchmarks despite small size
- Included with `sentence-transformers` — no separate download needed
- Used both directly (`.encode()`) and as a ChromaDB embedding function
- Well-maintained and widely used

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| text-embedding-3-small (OpenAI) | API cost, data sent externally |
| all-mpnet-base-v2 | Larger (110M params), slower, marginal improvement |
| bge-small-en-v1.5 | Slightly better benchmarks but less familiar, more dependencies |
| instructor-xl | Much larger, designed for task-specific embeddings — overkill |
| E5-large | Requires prefixes ("query:", "passage:"), more complex usage |

**Trade-off**: 384 dimensions gives reasonable semantic capture. Larger models (768d+) capture more nuance but are slower and use more memory.

---

## 6. Full-Text Search — BM25 (bm25s)

**What it is**: BM25 (Best Match 25) is a probabilistic keyword ranking algorithm. `bm25s` is a fast Python implementation with PyStemmer for English stemming.

**Why it was chosen**:
- Complements vector search — catches exact keyword matches that semantic search misses
- No additional infrastructure — runs entirely in-process
- Fast enough for corpora of thousands of chunks
- Stemming with PyStemmer improves recall (e.g., "running" matches "run")

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Elasticsearch | Requires a separate service; heavy for this scale |
| Whoosh | Pure Python, slower than `bm25s`; less maintained |
| rank-bm25 | Slower Python implementation; `bm25s` is a direct, faster replacement |
| TF-IDF (scikit-learn) | No BM25 saturation parameter; slightly worse retrieval quality |
| ChromaDB full-text | ChromaDB does not support BM25 — only vector similarity |

**Trade-off**: The BM25 index is held in process memory and rebuilt from ChromaDB at startup. If ChromaDB data is not persistent, the BM25 index is empty after restart.

---

## 7. Retrieval Fusion — Reciprocal Rank Fusion (RRF)

**What it is**: RRF combines ranked lists from multiple retrievers into a single ranked list. Each document's score is `Σ 1 / (k + rank)` across all lists. `k=60` is the standard constant.

**Why it was chosen**:
- Requires no score calibration — BM25 scores and cosine similarity scores are on different scales and cannot be added directly
- Simple to implement correctly (10 lines of code)
- Empirically effective — often outperforms more complex fusion methods
- Used in production systems (Microsoft, Cohere hybrid search)

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Score normalisation + weighted sum | Requires calibrating weights for each retriever; unstable across corpora |
| CombSUM / CombMNZ | Similar to RRF but more sensitive to score scale |
| Cross-encoder reranker | More accurate but requires a second model inference call (slow on CPU) |
| Take top-N from each retriever separately | Duplicates, no rank fusion benefit |

**Trade-off**: RRF does not use the actual similarity scores — only the rank position. A document ranked 1st with very high confidence is treated the same as one ranked 1st with low confidence.

---

## 8. Knowledge Graph — NetworkX + JSON files

**What it is**: A directed multigraph stored as a NetworkX `MultiDiGraph` in-process and serialised to a per-user JSON file using `node_link_data`.

**Why it was chosen**:
- Zero external dependencies — NetworkX is pure Python
- Simple ego-graph retrieval for query-time context lookup
- JSON files are human-readable and debuggable
- Per-user isolation is trivial — each user gets `{user_id}.json`
- Atomic write (write to `.tmp`, then `os.replace()`) prevents corruption

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Neo4j | Requires a separate graph database service; significant operational overhead |
| Amazon Neptune | AWS cloud service; cost and lock-in |
| neomodel / py2neo | ORM wrappers around Neo4j — same infrastructure requirement |
| SQLite adjacency list | Possible but loses NetworkX's graph algorithms |
| In-memory only | Data lost on restart — unacceptable |

**Trade-off**: JSON files on Render's disk require a persistent disk (paid plan). The graph is also not scalable to millions of edges — fine for a personal assistant.

---

## 9. Triple Extraction — LLM-based

**What it is**: For every document chunk and chat message, the LLM is prompted to extract subject–relation–object triples in JSON format.

**Why it was chosen**:
- No additional NLP model needed (no spaCy dependency in production)
- Flexible — can handle informal language, not just formal sentences
- The same `LLMService` already used for chat generation
- Can extract implicit relationships that rule-based NER would miss

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| spaCy dependency parsing | Requires spaCy model download (~50–500 MB); brittle with informal text |
| OpenIE (Stanford) | Requires Java; complex setup |
| Rebel (HuggingFace model) | Separate 750M+ model; too large for CPU inference |
| Rule-based regex patterns | Too brittle; misses natural language relationships |
| Skip graph extraction | Users lose the knowledge graph feature |

**Trade-off**: The LLM is called once per sentence per document chunk during upload. A 10-page document generates ~100 LLM calls. This is slow (1–5 minutes on a small model).

---

## 10. Memory Architecture — Three separate collections

**What it is**: Three ChromaDB collections for different memory types: `memory` (semantic), `episodes` (episodic), `procedures` (procedural).

**Why it was chosen**:
- Each memory type has different retrieval semantics (facts vs events vs instructions)
- Separate collections allow different similarity thresholds and access patterns per type
- Procedural memories (behavioural instructions) always appear in the prompt
- Episodic memories are only stored for significant interactions — different LLM classifier
- Conceptually clean — maps to established cognitive science memory taxonomy

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Single `memories` collection with `type` metadata | Simpler but loses per-type retrieval tuning |
| All in MongoDB | MongoDB is not a vector store; no semantic similarity search |
| Memory as part of the conversation document | Would bloat conversation documents; no independent lifecycle |

**Trade-off**: Three collections mean three ChromaDB queries per chat message. With small collections this is fast (~10ms each).

---

## 11. Memory Decay — Score-based forgetting

**What it is**: A memory strength score is computed as `0.5 × importance + 0.3 × recency + 0.2 × usage`. Memories below `MEMORY_FORGET_THRESHOLD = 0.15` are deleted.

**Why it was chosen**:
- Prevents unbounded memory growth
- Mimics human forgetting — recent and frequently accessed memories survive
- `importance` (LLM-assigned 0–1) weights the base strength
- `recency` decays exponentially with `exp(-0.05 × age_days)` — ~50% at 14 days
- `usage` (access count) reinforces frequently retrieved memories

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Never delete memories | Memory grows without bound; retrieval slows and quality degrades |
| Delete oldest N memories | FIFO — ignores importance and recency independently |
| User-controlled deletion only | Puts maintenance burden on the user |
| TTL (time-to-live) | Hard cutoff ignores importance |

**Trade-off**: A memory that is important but was never accessed may decay and be deleted. Tuning `MEMORY_FORGET_THRESHOLD` matters.

---

## 12. Short-term Memory — In-process rolling window

**What it is**: A `ConversationMemory` Python object held in a dictionary keyed by `user_id` in the `RAGService`. Stores the last `SHORT_TERM_MESSAGES × 2 = 12` messages.

**Why it was chosen**:
- Zero latency — no database query for each turn
- LLM context is limited anyway — sending more than ~12 messages rarely helps a 1B model
- Simple — a Python list is sufficient

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Read last N messages from MongoDB on each turn | Adds a DB query per message; introduces latency |
| Redis session cache | Requires Redis service; not needed at this scale |
| Full conversation from MongoDB | Context window overflow on long conversations |

**Trade-off**: The in-process dictionary is lost on restart. After a restart, the rolling window is empty even if the conversation has history. This is acceptable because MongoDB stores all messages durably.

---

## 13. Text Splitting — RecursiveCharacterTextSplitter

**What it is**: LangChain's recursive splitter tries to split on paragraphs, then sentences, then words, then characters — in that order — to keep semantically coherent chunks.

**Why it was chosen**:
- Respects natural text boundaries rather than cutting arbitrarily
- 500 character chunk size with 70 character overlap balances context and granularity
- Overlap ensures that sentences near chunk boundaries appear in at least one retrievable chunk
- LangChain's implementation is well-tested

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Fixed-size character splitting | Cuts mid-sentence, losing context |
| Sentence-level splitting | Variable chunk size; very short sentences produce poor embedding quality |
| Semantic chunking | Requires embedding during splitting — slow; overkill for plain text |
| Paragraph-only splitting | Paragraphs vary wildly in length — some too long for embedding model context |

**Trade-off**: 500 characters (~100 words) is quite small. Some questions may require combining information from multiple chunks that a single retrieval step would miss.

---

## 14. Web Framework — FastAPI

**What it is**: A modern Python ASGI framework with automatic OpenAPI schema generation, Pydantic data validation, and dependency injection.

**Why it was chosen**:
- Pydantic v2 models for request/response validation with zero extra code
- Dependency injection (`Depends`) makes auth clean — `get_current_user` is one line at any endpoint
- Async support — does not block the event loop for I/O
- Auto-generated interactive docs at `/docs`
- `lifespan` context manager for clean startup/shutdown

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Flask | Synchronous; no built-in validation; no dependency injection |
| Django | Too heavyweight; ORM assumes SQL; REST APIs require DRF on top |
| Starlette (bare) | FastAPI is built on Starlette — using it directly gives no extra benefit |
| Express (Node.js) | Would require rewriting all Python ML/AI code |

---

## 15. ASGI Server — Uvicorn (single worker)

**What it is**: Uvicorn is a fast ASGI server. `--workers 1` limits it to a single process.

**Why single worker**:
The BM25 index and `ConversationMemory` are Python dictionaries held in process memory. With multiple workers, each process has its own copy. A document indexed by worker 1 is invisible to worker 2, and short-term conversation context is split across workers non-deterministically.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| `--workers N` (Gunicorn) | Multi-process breaks in-process state sharing |
| Multiple Render instances | Same problem — shared mutable state not supported |
| Externalise state to Redis | Would fix the multi-worker problem but adds Redis infrastructure |

**Trade-off**: Single worker means no horizontal scaling. For a personal assistant with a single user this is fine. For multi-user production scale, BM25 and conversation context would need to be externalised.

---

## 16. Authentication — Google OAuth + JWT

**What it is**: Users authenticate via Google OAuth 2.0. The backend exchanges the authorization code for a Google access token, fetches user info, and issues its own JWT.

**Why it was chosen**:
- No password management — Google handles credential security
- Users already have Google accounts — zero friction signup
- JWTs are stateless — no session store needed for access token validation
- Widely understood and audited protocol

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Email + password | Requires password hashing, reset flows, security hardening |
| GitHub OAuth | Narrower user base |
| Magic link (email) | Requires email delivery service |
| Auth0 / Clerk | External dependency, potential cost, loses control |
| Session cookies (server-side) | Requires session store (Redis); more complex with multiple services |

**Trade-off**: Google OAuth requires a Google Cloud project. If Google changes OAuth flow, the application breaks. This is a single point of failure for authentication.

---

## 17. Token Storage — React state (access) + HttpOnly cookie (refresh)

**What it is**: The short-lived access token is held in React `useState`. The long-lived refresh token is stored in an `HttpOnly; Secure; SameSite=None` cookie.

**Why this split**:

The access token needs to be accessible to JavaScript to add it to request headers. React state is the safest place — it is not persisted and is lost on page refresh (by design — the silent refresh restores it).

The refresh token must NOT be accessible to JavaScript. An `HttpOnly` cookie is invisible to `document.cookie` and cannot be read by any script, including injected scripts (XSS protection).

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Both in localStorage | localStorage is accessible to XSS — refresh token would be stolen |
| Both in sessionStorage | Lost on tab close; refresh token could still be stolen via XSS |
| Both in cookies | Refresh token cookie is fine; access token in cookie means every request sends it (CSRF risk) |
| Both in React state | Refresh token lost on page refresh — user must log in again every time |

---

## 18. Token Strategy — Short-lived JWT + rotating refresh tokens

**What it is**: Access tokens expire after 15 minutes. Each time a new access token is issued, the old refresh token is deleted and replaced with a new one (rotation).

**Why rotation**:
If a refresh token is stolen and used by an attacker, the next legitimate use of that token (by the real user) will fail because it was already rotated. The server can detect this and invalidate the entire session.

**Why 15 minutes for access tokens**:
Short enough that a stolen token has limited utility. Long enough that normal browsing does not trigger constant refreshes.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| No refresh tokens (long-lived JWT, e.g. 30 days) | A stolen token is valid for 30 days with no revocation |
| Opaque tokens (random strings stored server-side) | Requires a DB lookup on every request |
| Static refresh tokens (no rotation) | Stolen refresh token can be used indefinitely |

---

## 19. CORS Strategy — Explicit origins, credentials: include

**What it is**: `ALLOWED_ORIGINS` is a comma-separated environment variable. The backend never uses `allow_origins=["*"]`. The frontend always sets `credentials: "include"`.

**Why explicit origins**:
`allow_origins=["*"]` with `allow_credentials=True` is rejected by browsers. Even if it were allowed, wildcards would permit any website to make authenticated requests to your API.

**Why `credentials: "include"`**:
Without this, the browser strips the `Cookie` header on cross-origin requests. The HttpOnly refresh token cookie would never be sent to the backend, breaking silent refresh.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| `allow_origins=["*"]` | Incompatible with `allow_credentials=True`; security risk |
| Proxy frontend requests through backend | Avoids CORS entirely but requires Nginx/reverse proxy setup |
| Same origin (same domain) | Would require frontend and backend on the same domain with path routing |

---

## 20. Conversation ID — Server-assigned UUID

**What it is**: The backend creates the conversation record and returns its UUID. The frontend stores and uses this server-assigned ID for all subsequent requests.

**Why server-assigned**:
If the frontend generated its own UUID and sent it to the backend, the backend would have no record of that conversation and would return 404. The backend must be the source of truth for what conversations exist and who owns them.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Frontend-generated UUID, backend upserts | Backend cannot enforce ownership — any UUID could be injected |
| Auto-create conversation on first message | Creates a race condition if two messages are sent quickly |
| Conversation embedded in user document | Denormalised; complicates querying and pagination |

---

## 21. Frontend Framework — React + Vite + TypeScript

**What it is**: React 19 for UI, Vite 8 for bundling and dev server, TypeScript for type safety.

**Why Vite over CRA or Next.js**:
- CRA (Create React App) is deprecated
- Next.js server-side rendering adds complexity with no benefit here — Mnemos is a fully client-side authenticated SPA
- Vite is fast, modern, and minimal

**Why TypeScript**:
Strong typing prevents entire classes of bugs in the frontend/backend contract — if the API response shape changes, TypeScript catches mismatches at build time rather than runtime.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Next.js | SSR not needed; adds server infrastructure; complicates Render deployment |
| Vue 3 | Different ecosystem; less widespread |
| Svelte | Smaller ecosystem; less mature component libraries |
| Plain JavaScript | No type safety; API contract errors only caught at runtime |
| Angular | Heavyweight; opinionated; steep learning curve |

---

## 22. State Management — React Context + custom hooks (no library)

**What it is**: `AuthContext` manages authentication state. Feature state (`useChat`, `useUpload`, etc.) lives in custom hooks co-located with the pages that use them. No Redux, Zustand, or Jotai.

**Why no library**:
- The only truly global state is the access token — a single `useState` in one context is sufficient
- Each page's data is independent — no cross-page state sharing needed
- Hooks are composable and colocated with their consumers
- Fewer dependencies, smaller bundle

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Redux Toolkit | Significant boilerplate; overkill for this state surface area |
| Zustand | Good but unnecessary for this scale; adds a dependency |
| Jotai / Recoil | Atomic state — useful for complex interdependencies that don't exist here |
| React Query (TanStack Query) | Would improve cache invalidation but adds complexity |

**Trade-off**: Without a caching layer (like React Query), every page mount triggers a fresh API fetch.

---

## 23. Chat Persistence — LocalStorage + MongoDB

**What it is**: Message history is stored both in MongoDB (durable, server-side) and localStorage (fast, client-side). LocalStorage is the source of truth for UI rendering. MongoDB is the source of truth for durability.

**Why both**:
- LocalStorage: instant reads, no network latency, works offline
- MongoDB: survives clearing localStorage, accessible across devices, permanent

**Trade-off**: The two stores can diverge if a network error occurs mid-conversation. Currently there is no sync mechanism — localStorage is the authoritative source for what the UI shows.

---

## 24. Graph Visualisation — ReactFlow (@xyflow/react)

**What it is**: ReactFlow is a React library for interactive node-edge graph diagrams with built-in zoom, pan, minimap, and controls.

**Why it was chosen**:
- Purpose-built for graph/network diagrams
- Handles layout, interaction, and rendering out of the box
- Active maintenance and good TypeScript types
- `fitView` automatically positions nodes sensibly

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| D3.js | Very powerful but requires writing all interaction logic manually |
| Cytoscape.js | Good but less React-native; requires a wrapper |
| Vis.js | Less maintained; harder to style |
| Sigma.js | Designed for large graphs (1M+ nodes) — overkill here |
| SVG from scratch | No pan/zoom/interaction without significant work |

**Trade-off**: ReactFlow adds ~130 KB to the bundle.

---

## 25. Markdown Rendering — react-markdown

**What it is**: A React component that parses Markdown AST and renders it as styled HTML elements using a custom component map.

**Why it was chosen**:
- LLMs naturally output Markdown (bold, lists, code blocks, headings)
- Rendering raw strings with asterisks and `#` characters is a bad user experience
- `react-markdown` is the standard React Markdown solution — 3M+ weekly downloads
- Only applied to assistant bubbles — user input is always plain text

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| `dangerouslySetInnerHTML` with `marked` | XSS risk — `marked` produces HTML strings |
| `showdown` | Older, less React-native |
| Strip Markdown from LLM output | Fragile — small models often ignore "don't use Markdown" instructions |
| Instruct LLM to not use Markdown | Same fragility — unreliable with 1B models |

---

## 26. Deployment Platform — Render

**What it is**: Render is a cloud platform for hosting web services, static sites, cron jobs, and databases.

**Why it was chosen**:
- Blueprint (`render.yaml`) deploys both backend and frontend from a single config file
- Free tier available for prototyping (with limitations)
- Automatic HTTPS
- GitHub integration — pushes trigger redeploys automatically
- Persistent disk add-on available ($0.25/GB/month)
- No Kubernetes or Docker knowledge required

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| AWS (EC2, ECS, Lambda) | Complex setup; IAM, VPCs, security groups; significant learning curve |
| Google Cloud Run | Good alternative but requires Docker image; GCP setup complexity |
| Heroku | Eliminated free tier in 2022; more expensive than Render for equivalent specs |
| Fly.io | Good alternative; requires Docker; slightly more complex config |
| Railway | Similar to Render; less mature blueprint support |
| Vercel | Frontend-only (or Next.js-focused); backend Python support is limited |

---

## 27. Frontend Deployment — Render Static Site

**What it is**: The Vite production build (`dist/`) is deployed as a static site on Render. A rewrite rule maps all paths to `index.html` to support React Router's client-side routing.

**Why static site over a Node server**:
- No server process to maintain or pay for
- Zero cold starts — static files are served from CDN
- React Router handles all routing client-side

**The critical SPA rewrite rule**:
```yaml
routes:
  - type: rewrite
    source: /*
    destination: /index.html
```
Without this, navigating directly to `/chat` or `/memories` returns a 404 because those paths don't exist as files.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Vercel | Excellent for static sites but separate platform from the backend |
| Netlify | Good alternative; separate platform |
| GitHub Pages | Free but no environment variable support at build time |
| Serve frontend from FastAPI (`StaticFiles`) | Merges frontend and backend — harder to scale and deploy independently |

---

## 28. Persistent Storage — Render Disk (for ChromaDB + graphs)

**What it is**: A Render persistent disk is a mounted block storage volume at `/data`. ChromaDB and graph JSON files are stored here.

**Why needed**:
Render's default service filesystem is ephemeral — it is wiped on every deploy or restart. ChromaDB stores embeddings on disk. Without a persistent disk, all uploaded documents and built memories are lost every time the service restarts.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| AWS S3 + startup sync | Complex; startup time grows with data size; eventual consistency risk |
| Managed vector DB (Pinecone) | Cost; vendor lock-in; requires significant code changes |
| No persistence (accept data loss) | Documents, memories, and graph reset on every restart — unacceptable for a memory assistant |
| PostgreSQL + pgvector | Would require migrating away from ChromaDB |

---

## 29. Service Architecture — Two separate Render services

**What it is**: Backend and frontend are deployed as separate Render services (`mnemos-backend` as a Web Service, `mnemos-frontend` as a Static Site).

**Why separate**:
- Frontend and backend can be deployed independently — a CSS fix doesn't restart the Python process
- Static site for frontend has zero cold starts and serves from CDN
- CORS is explicitly configured — no implicit same-origin assumptions
- Easier to update only the service that changed

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Serve frontend from FastAPI (`StaticFiles`) | Single service; every frontend change restarts the backend; no CDN |
| Single Docker container (Nginx + uvicorn) | Requires Docker knowledge; no benefit over separate services on Render |

**Trade-off**: Cross-origin requests require CORS configuration and `credentials: "include"`. With same-origin serving this would not be needed.

---

## 30. RAG Architecture — Hybrid BM25 + vector, no reranker

**What it is**: BM25 retrieves keyword-matched chunks; vector search retrieves semantically similar chunks; their results are merged by deduplication and top-N is taken.

**Why no reranker**:
A cross-encoder reranker would score each (query, chunk) pair and produce better rankings. However:
- It requires a second model inference per candidate chunk (~10 candidates × ~100ms = 1 second extra latency on CPU)
- The 1B LLM is already the bottleneck — the RAG retrieval is fast by comparison
- Adding a reranker doubles the number of model-loading requirements

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Vector only (no BM25) | Misses exact keyword matches; worse for document lookups |
| BM25 only | Misses semantic similarity; worse for paraphrased queries |
| Reranker (cross-encoder) | Better quality but unacceptable CPU latency |
| ColBERT | State-of-the-art late interaction retrieval; complex; requires separate index |

---

## 31. Error Isolation — Per-step try/except in RAG pipeline

**What it is**: In `rag_service.py`, each of graph update, semantic memory update, episodic memory update, and procedural memory update is wrapped in its own `try/except`. Failures are logged but do not abort the chat response.

**Why this matters**:
If the LLM returns malformed JSON during triple extraction, or the graph file is temporarily unwritable, the user should still receive their answer. Background updates are non-critical for the immediate response.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Propagate exceptions | A graph write failure would cause the entire chat to 500 |
| FastAPI `BackgroundTasks` | Would decouple updates from the response — good idea for future work |

---

## 32. File Upload — Plain HTTP multipart, .txt only

**What it is**: Files are uploaded directly to `POST /documents/upload` as `multipart/form-data`. Only `.txt` files up to 10 MB are accepted.

**Why .txt only**:
PDF and DOCX parsing requires additional libraries (`pypdf`, `python-docx`) and adds complexity. Plain text is the simplest case and sufficient for demonstrating the RAG pipeline.

**Why 10 MB limit**:
A 10 MB text file is ~5 million characters. At 500-character chunks that is ~22,000 chunks, generating ~22,000 LLM calls for graph extraction. This is already impractical — the limit prevents abuse.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Pre-signed S3 URL upload | For large files to avoid backend memory; overkill for text files |
| PDF support | Requires `pypdf`; additional dependency; parsing quality varies |
| No file size limit | Risk of running out of memory on the Render instance |

---

## 33. Cookie SameSite Strategy — None in production, Lax in dev

**What it is**: `SameSite=None; Secure` in production (different origins), `SameSite=Lax` in local dev (same host, different ports).

**Why the difference**:
In production, the frontend (`mnemos-frontend.onrender.com`) and backend (`mnemos-backend.onrender.com`) are different origins. Cookies must explicitly opt in to cross-site sending via `SameSite=None`.

In local dev, both run on `localhost` but different ports. Browsers treat `localhost:5173` and `localhost:8000` as the same site. `SameSite=Lax` works and `Secure` is not needed because there is no HTTPS.

**`SameSite=None` requires `Secure=True`**: This is a browser rule. `SameSite=None` without `Secure` is silently downgraded to `SameSite=Strict` in modern browsers.

---

## 34. Graph Storage — Atomic write (tmp + rename)

**What it is**: Graph saves write to `{user_id}.json.tmp` first, then call `os.replace()` to rename it over the real file.

**Why atomic write**:
If the process crashes or is killed mid-write, a partial JSON file is created. `json.load()` would fail on the corrupted file, silently returning an empty graph and losing all previous data. With `os.replace()` (atomic on POSIX systems), either the old file exists or the new file exists — never a partial state.

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Direct write to final filename | Data loss on crash mid-write |
| Write-ahead log | Complex; overkill for a per-user JSON file |
| Database transaction | Would require moving graph storage to MongoDB/PostgreSQL |

---

## 35. User Isolation — user_id on every record

**What it is**: Every piece of stored data — MongoDB documents, ChromaDB entries, graph files — includes the `user_id` of the owner. Every query filters by the authenticated user's ID derived from the validated JWT.

**Why this matters**:
Without user isolation, any authenticated user could query any other user's documents, memories, and conversations.

**How it is enforced**:

```python
# Every API endpoint uses Depends(get_current_user)
# which validates the JWT and returns user_id

# MongoDB
conversations_collection.find({"user_id": user_id, ...})

# ChromaDB
collection.get(where={"user_id": user_id}, ...)

# Graph files
graph_path = f"data/graphs/{user_id}.json"
```

**Alternatives**:

| Alternative | Why not chosen |
|---|---|
| Separate database per user | Extreme overhead; impractical for a shared service |
| Database-level row security (PostgreSQL RLS) | Would work but requires PostgreSQL |
| Trust frontend to send correct user_id | Never trust client-supplied user identity — always derive from server-validated JWT |
