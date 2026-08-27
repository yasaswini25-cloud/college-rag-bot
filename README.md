# 🎓 AI-Powered College Information Assistant

An AI-powered college information assistant built using **Retrieval-Augmented Generation (RAG)**. The system allows students to ask questions about college-related information such as admissions, academics, hostel facilities, fees, placements, scholarships, library rules, and regulations.

Instead of relying only on the LLM's general knowledge, the application retrieves relevant information from the college's document knowledge base and uses it to generate grounded responses.

---

## 🚀 Live Demo

### Frontend
https://client-51czj1nt8-yasaswini25-clouds-projects.vercel.app/

### Backend API
https://college-rag-bot-akne.onrender.com/

### API Documentation
https://college-rag-bot-akne.onrender.com/docs

---

## 📌 Project Overview

The **AI-Powered College Information Assistant** is a full-stack RAG-based chatbot designed to provide accurate and context-aware answers to college-related questions.

Users can ask natural-language questions such as:

- "What are the hostel room charges?"
- "What is the hostel curfew timing?"
- "What are the admission requirements?"
- "What are the placement eligibility rules?"
- "What scholarships are available?"
- "What are the library timings?"
- "What are the academic regulations?"

The system retrieves relevant document chunks from the knowledge base and provides the retrieved context to the language model before generating the final answer.

---

## ✨ Features

### 🤖 AI Chatbot

- Natural-language question answering
- Context-aware responses
- RAG-based knowledge retrieval
- Grounded responses using college documents
- Conversation history
- Multiple conversations
- Conversation renaming
- Conversation deletion

### 📚 Knowledge Base

The system supports college documents containing information about:

- Admissions
- Academic regulations
- Hostel and residence fees
- Hostel regulations
- Placements
- Scholarships
- Library policies
- College guidelines

### 🔎 RAG Pipeline

The retrieval pipeline includes:

1. Document ingestion
2. Document processing
3. Text extraction
4. Text chunking
5. Embedding generation
6. Vector-based retrieval
7. Keyword matching
8. Hybrid retrieval
9. Reranking
10. LLM response generation

### 📄 Document Processing

Supported file formats:

- PDF
- DOCX
- DOC
- TXT
- Markdown

### 🔐 Authentication

The application provides:

- User registration
- User login
- JWT authentication
- Logout
- Current-user information
- Role-based users

### 👥 User Roles

The system supports different user roles including:

- Student
- Administrator

### 📊 Admin Features

Administrators can access:

- Dashboard
- Document management
- RAG status
- Document reindexing
- Analytics

### 💬 Feedback

Users can provide feedback on chatbot responses.


# 🏗️ System Architecture

                         ┌──────────────────────┐
                         │      User / Student  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   React Frontend     │
                         │      + Vite          │
                         └──────────┬───────────┘
                                    │
                                    │ REST API
                                    ▼
                    ┌─────────────────────────────┐
                    │        FastAPI Backend      │
                    │                             │
                    │ Authentication              │
                    │ Chat                        │
                    │ Documents                   │
                    │ RAG                         │
                    │ Admin                       │
                    │ Feedback                    │
                    └─────────────┬───────────────┘
                                  │
                     ┌────────────┴─────────────┐
                     │                          │
                     ▼                          ▼
             ┌───────────────┐          ┌────────────────┐
             │   Database    │          │   RAG Pipeline │
             │               │          │                │
             │ Users         │          │ Chunking       │
             │ Documents     │          │ Embeddings     │
             │ Chunks        │          │ Retrieval      │
             │ Conversations │          │ Reranking      │
             │ Messages      │          └───────┬────────┘
             └───────────────┘                  │
                                                ▼
                                      ┌──────────────────┐
                                      │ Knowledge Base   │
                                      │ College Docs     │
                                      └────────┬─────────┘
                                               │
                                               ▼
                                      ┌──────────────────┐
                                      │       LLM        │
                                      │ Gemini / OpenAI  │
                                      └──────────────────┘
