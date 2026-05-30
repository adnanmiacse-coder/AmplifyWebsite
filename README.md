# 🎓 Amplify — AI-Driven Adaptive Learning Assistant

An intelligent, multimodal learning platform built for Bengali learners. StyleTutor combines multi-provider LLM orchestration, local Ollama inference, document-based RAG, adaptive assessments, and voice interaction — all powered by a Laravel backend for classroom and teacher management.

---

## ✨ Features

- 🤖 **Hybrid LLM strategy** — cloud providers (GROQ, OpenRouter) + local Ollama inference with quantized models
- 🔒 **Fully local mode** — run open-weight models on-device with no data sent to external APIs
- 📄 **Document ingestion** via PDF parsing, OCR, chunking, and graph analysis
- 🔍 **Multi-layer RAG** — TF-IDF, FAISS vector search, and Graph RAG for semantic & structural retrieval
- 📝 **Adaptive assessments** in Bengali with real-time student model updates
- 🔊 **Voice interaction** — TTS for learners, speech recognition for teachers
- 🏫 **Classroom management** through a Laravel backend and teacher portal
- 📊 **Topic graph visualization** using Cytoscape
- 💾 **Offline-capable persistence** via Neo4j or browser localStorage

---

## 🧠 Models

StyleTutor supports two inference modes — **cloud** (for scalability) and **local** (for privacy and offline use):

### ☁️ Cloud Models

| Role | Model | Provider |
|------|-------|----------|
| Primary chat / lecture generation | `llama-3.3-70b-versatile` | GROQ AI |
| Fallback LLMs | `llama-3.3-70b-specdec`, `gemma2-9b-it`, `llama-3.1-8b-instant` | GROQ AI |
| Alternative provider fallback | `openrouter/auto` | OpenRouter |
| Vision / OCR | `meta-llama/llama-4-scout-17b-16e-instruct` | Meta (via API) |
| Slide / content generation | Gemini endpoint | Google |

### 🖥️ Local Models (via Ollama)

| Role | Examples |
|------|---------|
| Primary local inference | Llama 3, Gemma, Phi (quantized) |
| Embeddings | `all-MiniLM-L6-v2` or similar Sentence Transformers |

- Low temperature settings (**0.1–0.2**) for deterministic, factual outputs
- Quantized models for efficient inference on consumer hardware
- Zero external API calls — full data privacy and offline capability

---

## 🗂️ RAG Architecture

The core AI experience (`styletutor.js`) implements a multi-layer retrieval-augmented generation pipeline. The model is instructed to answer **only from retrieved content** — no reliance on parametric memory.

### 1. TF-IDF Vector Store *(browser-side)*
- Text split into ~300-word chunks with 60-word overlap
- Browser-side TF-IDF index built from chunk tokens
- Retrieval via cosine similarity + diversity-aware selection

### 2. FAISS Vector Index *(local Python pipeline)*
- PDF books loaded → text chunked with overlap for context preservation
- Embeddings generated via local Sentence Transformer models
- Stored in a FAISS index for fast top-*k* similarity search
- Retrieved chunks injected into LLM context as grounding evidence

### 3. Graph RAG
- Extracts entity-like tokens from each chunk
- Builds an entity co-occurrence graph
- Retrieval via direct entity overlap and graph traversal

Together, these layers enable answering questions using **semantic relevance**, **dense vector similarity**, and **topic structure** from the source document.

---

## 📚 Data Sources

| Source | Details |
|--------|---------|
| PDF books / documents | User-provided; parsed with `pdf.js` / `pdfplumber`, page-by-page extraction, AI vision OCR fallback |
| FAISS index | Chunked + embedded PDFs stored locally for fast retrieval |
| Persisted documents | Neo4j graph (with localStorage fallback) |
| Session & behavioral data | Chat history, attention logs, quiz performance, session summaries → n8n webhook |
| Classroom records | Teacher/student/classroom data via Laravel backend |

> **Privacy:** In local mode, no data is sent to external APIs. All PDF processing, embedding, and inference happen on-device.

---

## 👤 Personalization & Adaptive Learning

The student model is maintained and updated in real time:

- Tracks `overallLevel`, `conceptMastery`, `weakConcepts`, `correctStreak`, `wrongStreak`
- Updated after each quiz answer using an LLM prompt
- MCQs generated **in Bengali**, with difficulty adjusted to the student model
- Question selection biased toward weak concepts
- Replay recommendations computed from concept score thresholds and hint history
- **Session memory** — conversation context maintained within a chat session
- **Future:** User feedback loop to refine retrieval relevance

---

## 🛠️ Tech Stack & Integrations

### 🤖 Local AI
- **Ollama** — local LLM runtime for open-weight models
- **FAISS** — vector search and similarity retrieval
- **Sentence Transformers** — local embedding generation (`all-MiniLM-L6-v2` or similar)
- **LangChain / LlamaIndex** *(optional)* — RAG pipeline orchestration
- **PyPDF / pdfplumber** — PDF text extraction

### ☁️ Cloud AI & APIs
- **GROQ AI + OpenRouter** — chained with key rotation and retry logic
- **Google Gemini** — generative slide/content creation
- **Vision OCR** — image-to-text via LLM prompts

### 🔊 Browser & Voice
- `window.speechSynthesis` — Bengali TTS for learners
- `SpeechRecognition` — voice-based notification entry for teachers

### 📊 Visualization
- **Cytoscape** — interactive topic graph from lecture entity relationships

### 🏗️ Backend
- **Laravel** — classroom/auth management, teacher and student records, API routes

### 💾 Persistence
- **Neo4j** — graph-based document persistence
- **localStorage** — offline fallback

---

## 📁 Project Structure

```
├── styletutor.js          # Core AI tutoring experience (browser)
├── index.html             # AI Copilot teacher portal
├── classroom.html         # Voice-enabled teacher notification portal
├── rag/                   # Local RAG pipeline (FAISS + embeddings)
│   ├── ingest.py          # PDF loading, chunking, embedding, FAISS indexing
│   └── retriever.py       # Query → top-k chunk retrieval
├── app/                   # Laravel backend (auth, classroom, user models)
└── routes/                # Laravel API routes
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js, PHP / Laravel
- Python 3.9+ (for local RAG pipeline)
- [Ollama](https://ollama.ai) installed and running
- *(Optional)* Neo4j instance

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-org/styletutor.git
cd styletutor

# 2. Install frontend dependencies
npm install

# 3. Set up Laravel backend
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate

# 4. Install Python dependencies (local RAG)
pip install faiss-cpu sentence-transformers pdfplumber langchain

# 5. Pull a local model via Ollama
ollama pull llama3
```

### Configuration

```bash
# .env — configure API keys (cloud mode) and optional services
GROQ_API_KEY=...
OPENROUTER_API_KEY=...
GEMINI_API_KEY=...
NEO4J_URI=...          # optional
N8N_WEBHOOK_URL=...    # optional
```

> In **local-only mode**, leave cloud API keys blank. All inference runs through Ollama.

### Ingest your PDFs

```bash
# Build the FAISS index from your PDF books
python rag/ingest.py --input ./docs --output ./index
```

---

## 🌐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Primary cloud LLM provider | Cloud mode |
| `OPENROUTER_API_KEY` | Fallback cloud LLM provider | Cloud mode |
| `GEMINI_API_KEY` | Slide/content generation | Cloud mode |
| `OLLAMA_BASE_URL` | Ollama server URL (default: `http://localhost:11434`) | Local mode |
| `NEO4J_URI` | Graph database URI | Optional |
| `N8N_WEBHOOK_URL` | Session data reporting webhook | Optional |

---

## 🏗️ Architecture Overview

```
User (Bengali Learner)
        │
        ▼
  styletutor.js  ──────────────────────────────────────────────────┐
        │                                                            │
   ┌────┴──────────┐   ┌──────────────┐   ┌──────────────────────┐ │
   │   RAG Layer   │   │ Student Model│   │    Quiz Generator    │ │
   │  TF-IDF +     │   │  (adaptive)  │   │   (Bengali MCQs)     │ │
   │  FAISS +      │   └──────┬───────┘   └──────────┬───────────┘ │
   │  Graph RAG    │          │                       │             │
   └────┬──────────┘          └──────────┬────────────┘             │
        │                               ▼                           │
        │              ┌────────────────────────────────┐           │
        │              │  LLM Inference                 │           │
        │              │  Local: Ollama (Llama3/Gemma)  │           │
        │              │  Cloud: GROQ → OpenRouter      │           │
        │              └────────────────────────────────┘           │
        │                                                            │
   ┌────┴──────────────────────────────────────────────────────┐    │
   │              PDF Ingestion + OCR + FAISS Indexing          │    │
   └───────────────────────────────────────────────────────────┘    │
                                                                     │
                          Laravel Backend ◄──────────────────────────┘
                       (Auth, Classrooms, Users)
```

---

## 📄 License

[MIT](LICENSE) — feel free to use, modify, and build on this project.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.
