# 🎓 AI-Powered College Information Assistant (CampusRAG)

An enterprise-grade, full-stack **AI-Powered College Information Assistant** built with **FastAPI**, **React.js + Vite**, **Tailwind CSS**, and a **Document-Grounded Retrieval-Augmented Generation (RAG)** pipeline.

---

## 🌟 Key Highlights & Capabilities

- **Strict Document Grounding**: Every answer is retrieved from verified institutional regulations, circulars, fee structures, and handbooks before generation.
- **Zero-Hallucination Guardrails**: When information is unavailable in the college knowledge base, the system outputs `"I couldn't find reliable information about this in the college knowledge base."` rather than guessing.
- **Granular Page Citations**: Displays exact source documents, page numbers, and similarity match percentages.
- **Multi-Format Ingestion**: Extracts and cleans text from PDF (`PyMuPDF`), Word (`python-docx`), TXT, and Markdown files.
- **Semantic Vector & Hybrid Search**: Vector embeddings with cosine similarity and hybrid keyword term overlap (BM25) re-ranking.
- **Multi-Provider AI Support**: Compatible with Google Gemini (`gemini-1.5-flash`, `text-embedding-004`), OpenAI (`gpt-4o-mini`, `text-embedding-3-small`), and a deterministic local embedding & synthesis engine.
- **Pre-Seeded Knowledge Base**: Automatically loads official 2026 Academic Regulations, Admission Guidelines, Hostel & Fee Structures, Placement Policies, and Library/Scholarship circulars on first launch.
- **Role-Based Access Control**: Separate portals and dashboards for **Students** and **Campus Administrators**.

---

## 🏗️ System Architecture

```
Student / Admin Browser (React + Vite + Tailwind CSS)
                       │
                       ▼  [REST API / JWT Auth]
FastAPI Backend (app/main.py)
       ├── Routes / Controllers / Services
       │
       ├── RAG Ingestion Pipeline (Admin Upload)
       │     PDF / DOCX / TXT ──► PyMuPDF / docx ──► Splitter (500-800 tok) ──► Embeddings ──► Vector Store
       │
       └── RAG Query Pipeline (Student Chat)
             User Query ──► Vector Embedding ──► Cosine Similarity (Top-5)
                                                       │
                                                       ▼
                                            Hybrid Re-ranking (BM25)
                                                       │
                                                       ▼
                                            Grounded Context Builder
                                                       │
                                                       ▼
                                              LLM (Gemini / OpenAI)
                                                       │
                                                       ▼
                                             Answer + Page Citations
```

---

## 📦 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide React, Axios, React Router DOM, React Markdown |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy (Async), aiosqlite |
| **RAG / AI** | PyMuPDF (`fitz`), python-docx, Google Gemini API, OpenAI API, NumPy vector search |
| **Database** | SQLite (zero-config local async DB) / PostgreSQL + `pgvector` (Supabase compatible) |
| **Auth** | JWT (JSON Web Tokens), OAuth2 Password Bearer, bcrypt password hashing |

---

## 🚀 Step-by-Step Local Setup Guide

### 1. Prerequisites
Ensure you have the following installed on your machine:
- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+** & **npm 9+** (Tested on Node v22)
- **Git**

---

### 2. Backend Setup (FastAPI)

1. Open your terminal and navigate to the project directory:
   ```bash
   cd agenti_ai_project
   ```

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv server\venv
     .\server\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     python -m venv server\venv
     server\venv\Scripts\activate.bat
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv server/venv
     source server/venv/bin/activate
     ```

3. Install backend dependencies:
   ```bash
   pip install -r server/requirements.txt
   ```

4. Configure environment variables:
   - The default `server/.env` is pre-configured to work **100% locally out-of-the-box**.
   - *(Optional)* To enable Google Gemini or OpenAI cloud LLMs, add your API key in `server/.env`:
     ```env
     # LLM & Embedding Providers ("gemini", "openai", or "local")
     LLM_PROVIDER=gemini
     EMBEDDING_PROVIDER=gemini

     # Google Gemini API Key (https://aistudio.google.com/)
     GEMINI_API_KEY=your_gemini_api_key_here

     # Or OpenAI API Key
     OPENAI_API_KEY=your_openai_api_key_here
     ```

5. Start the FastAPI backend server:
   ```bash
   cd server
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   > 🚀 The backend will initialize the database and automatically seed default accounts and sample college policies.
   > - Backend API: `http://localhost:8000`
   > - Interactive Swagger Docs: `http://localhost:8000/docs`

---

### 3. Frontend Setup (React + Vite)

1. Open a **new terminal window** and navigate to the `client` directory:
   ```bash
   cd agenti_ai_project/client
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   > 🌐 Open your browser and visit: **`http://localhost:5173`**

---

## 🔑 Default Login Credentials

On first run, the system automatically creates two pre-configured accounts:

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Campus Admin** | `admin@college.edu` | `admin123` | Upload & delete documents, re-index vectors, view analytics |
| **Student** | `student@college.edu` | `student123` | Ask RAG queries, view page citations, submit feedback |

*Note: You can also register a new student or admin account anytime on the `/register` page.*

---

## 🧪 Testing the Grounded RAG Pipeline

Once logged in, open the **AI Chat** (`/chat`) and test with these institutional questions:

### Grounded Questions (Knowledge Base Match)
1. **Attendance Regulations**:
   > *"What is the minimum attendance required and what is the condonation fee?"*
   - **Expected Grounding**: 75% minimum aggregate attendance, condonation between 65%-74.9% with medical proof, Rs. 1,500 per subject fee.
   - **Cited Source**: *Academic Regulations 2026 (Page 1)*.

2. **Hostel Charges & Curfew**:
   > *"What are the hostel room categories and what time is the night curfew?"*
   - **Expected Grounding**: Single AC (Rs. 1,40,000), Double AC (Rs. 1,10,000), Curfew at 9:00 PM weekdays / 9:30 PM weekends.
   - **Cited Source**: *Hostel & Residence Fee Structure 2026 (Page 1)*.

3. **Placements Dream Policy**:
   > *"How does the Tier 2 Dream and Super Dream placement policy work?"*
   - **Expected Grounding**: Tier 1 (up to 7 LPA), Tier 2 Dream (7.1 - 14 LPA), Tier 3 Super Dream (> 14 LPA).
   - **Cited Source**: *Placement Policy & Recruitment Rules 2026 (Page 1)*.

4. **Scholarships**:
   > *"What are the criteria for the Founder's Excellence Award?"*
   - **Expected Grounding**: 100% tuition fee waiver for top 3 department rank holders with CGPA >= 9.5.
   - **Cited Source**: *Library Guidelines & Scholarships 2026 (Page 2)*.

### Unknown Question Handling (Anti-Hallucination Guardrail)
Try asking an unrelated question outside the college knowledge base:
> *"What is the recipe for chocolate chip cookies?"* or *"Who won the 1994 FIFA World Cup?"*
- **Expected Output**:
  > `"I couldn't find reliable information about this in the college knowledge base."`

---

## 📂 Project Directory Structure

```
agenti_ai_project/
├── spec.md                            # Baseline project specification
├── README.md                          # Local setup and usage guide
├── client/                            # Frontend (React 18 + Vite + Tailwind CSS)
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css                  # Modern styling & glassmorphism
│       ├── components/
│       │   ├── AppShell/              # Navigation bar & layout
│       │   ├── ChatWindow/            # Messages viewport & suggestions
│       │   ├── ChatInput/             # Textarea & category filters
│       │   ├── MessageBubble/         # Grounded markdown & feedback
│       │   ├── SourceCard/            # Collapsible citation cards
│       │   ├── ConversationSidebar/   # Chat history & management
│       │   ├── DocumentTable/         # Document status & actions
│       │   └── ProtectedRoute/        # Student & Admin route guards
│       ├── pages/
│       │   ├── index.jsx              # Landing page
│       │   ├── login.jsx              # Login with demo quick-fill
│       │   ├── register.jsx           # Student registration
│       │   ├── dashboard.jsx          # Student dashboard
│       │   ├── chat.jsx               # Conversational RAG interface
│       │   ├── settings.jsx           # Profile & RAG config
│       │   └── admin/
│       │       ├── index.jsx          # Admin analytics dashboard
│       │       └── documents.jsx      # Admin document management
│       ├── store/                     # Reactive auth and chat stores
│       └── services/api.js            # Axios client with JWT interceptor
└── server/                            # Backend (FastAPI Layered Architecture)
    ├── requirements.txt
    ├── .env.example
    ├── .env
    ├── sample_docs/                   # Official college policies for instant seeding
    └── app/
        ├── main.py                    # App entry point & lifespan seeder
        ├── config/                    # Settings & Async SQLAlchemy database
        ├── models/                    # User, Document, Chunk, Message, Feedback
        ├── rag/                       # Loader, Splitter, Embeddings, Retriever, Generator
        ├── services/                  # Business logic services
        ├── controllers/               # Request validation controllers
        └── routes/                    # API endpoints
```

---

## 📡 REST API Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status | No |
| `POST` | `/api/auth/register` | Register new student/admin | No |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT token | No |
| `GET` | `/api/auth/me` | Current authenticated user profile | Yes |
| `POST` | `/api/chat` | Send question, execute RAG & get grounded answer | Yes |
| `GET` | `/api/chat/history` | List user's conversations | Yes |
| `GET` | `/api/chat/{id}` | Get messages for a conversation | Yes |
| `DELETE` | `/api/chat/{id}` | Delete a conversation | Yes |
| `POST` | `/api/documents/upload`| Upload PDF/DOCX/TXT file & trigger indexing | Admin Only |
| `GET` | `/api/documents` | List documents with category/dept filters | No |
| `DELETE` | `/api/documents/{id}` | Delete document and its vector chunks | Admin Only |
| `POST` | `/api/rag/query` | Direct RAG query testing endpoint | No |
| `POST` | `/api/rag/reindex` | Recompute all vector embeddings | Admin Only |
| `POST` | `/api/feedback` | Submit 👍 / 👎 rating on an answer | Yes |
| `GET` | `/api/admin/dashboard` | Aggregated system & query analytics | Admin Only |

---

## 🛡️ Security & Privacy

- Passwords hashed with `bcrypt` / salted cryptography.
- Protected routes guarded with JWT Bearer tokens.
- Strict MIME-type and size validation on all uploaded files.
- Administrator endpoints strictly enforce role authorization (`role == "ADMIN"`).
- API keys stored securely in `.env` and never exposed to the frontend client.

---

## 📜 License
Developed as an open, grounded AI campus assistant for higher education institutions.
