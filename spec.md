Category	Specification

Project Type	AI + RAG-based Web Application

Domain	Education / Generative AI

Primary Objective	Provide accurate, document-grounded answers to college-related student queries

Architecture	Retrieval-Augmented Generation (RAG)

Frontend	React.js + Vite

UI Framework	Tailwind CSS

Backend	Python + FastAPI

Programming Language	Python, JavaScript

LLM	Gemini / OpenAI

Embedding Model	Gemini / OpenAI / HuggingFace embeddings

Vector Database	PostgreSQL + pgvector

Database	Supabase PostgreSQL

File Storage	Supabase Storage

Authentication	Supabase Auth / JWT

RAG Framework	LangChain

PDF Processing	PyMuPDF

DOCX Processing	python-docx

OCR	Tesseract/PaddleOCR (optional)

Search	Semantic Vector Search

Advanced Search	Hybrid Search (bonus)

Deployment – Frontend	Vercel

Deployment – Backend	Render / Railway

Version Control	Git + GitHub

Functional Specifications

Feature	Specification

User Authentication	Student/Admin login and registration

Chat Interface	Conversational question-answer interface

Document Upload	Admin can upload PDF/DOC/DOCX files

Text Extraction	Extract text from uploaded documents

Chunking	Split documents into manageable text chunks

Embedding Generation	Convert chunks into vector embeddings

Vector Storage	Store embeddings using pgvector

Semantic Search	Retrieve relevant chunks based on user query

RAG Pipeline	Query → Embedding → Retrieval → Context → LLM → Answer

Source Citation	Display document name and page/source used

Unknown Handling	Refuse/indicate when information isn't available

Conversation History	Store and retrieve previous conversations

Admin Management	Upload, update and delete documents

Role Management	Student and Admin roles

Feedback	👍 / 👎 answer feedback

Deployment	Fully accessible web application

RAG Specifications

Parameter	Initial Specification

Chunk Size	500–800 tokens

Chunk Overlap	50–100 tokens

Retrieval Count (Top-K)	5

Search Method	Cosine similarity / vector similarity

Relevance Filtering	Similarity threshold

Context Generation	Retrieved chunks + metadata

LLM Input	User query + retrieved context

Hallucination Control	Answer only from retrieved knowledge

Citation Metadata	Document, page, chunk ID

Fallback	"Information unavailable in the knowledge base"

Supported Knowledge Areas

Admissions

Departments

Courses

Fees

Examinations

Academic Calendar

Hostel

Library

Clubs

Placements

Scholarships

College Policies

Events

Regulations

FAQs

Notices

Database Specification

users

id

name

email

role

created\_at

documents

id

title

filename

category

department

version

file\_url

status

uploaded\_by

created\_at

updated\_at

document\_chunks

id

document\_id

chunk\_index

content

page\_number

embedding

metadata

created\_at

conversations

id

user\_id

title

created\_at

updated\_at

messages

id

conversation\_id

role

content

created\_at

message\_sources

id

message\_id

document\_id

chunk\_id

page\_number

similarity\_score

API Specification

POST   /auth/register

POST   /auth/login



POST   /chat

GET    /chat/history

GET    /chat/{conversation\_id}

DELETE /chat/{conversation\_id}



POST   /documents/upload

GET    /documents

GET    /documents/{id}

PUT    /documents/{id}

DELETE /documents/{id}



POST   /feedback



GET    /admin/analytics

Hardware Requirements



No specialized hardware required.



Component	Minimum

Processor	Intel i3 / Ryzen 3 or equivalent

RAM	8 GB

Storage	10 GB available

Internet	Required

GPU	Not required if using cloud LLM/embedding APIs

Software Requirements

Python 3.10+

Node.js 18+

npm

Git

GitHub

VS Code

Supabase account

LLM API access

Vercel account

Render/Railway account

Bonus Specifications

Feature	Priority

Department-wise knowledge bases	⭐⭐⭐

Hybrid keyword + semantic search	⭐⭐⭐

Document re-ranking	⭐⭐⭐

Source highlighting	⭐⭐⭐

Document versioning	⭐⭐⭐

Multilingual chatbot	⭐⭐

OCR	⭐⭐

Streaming responses	⭐⭐

Voice input/output	⭐⭐

Analytics dashboard	⭐⭐

Automatic FAQ generation	⭐

Conversation export	⭐

Core system requirement



The project will NOT be considered complete unless this pipeline works end-to-end:



College Document

&#x20;     ↓

Text Extraction

&#x20;     ↓

Chunking

&#x20;     ↓

Embedding Generation

&#x20;     ↓

Vector Database

&#x20;     ↓

Semantic Similarity Search

&#x20;     ↓

Relevant Context

&#x20;     ↓

LLM

&#x20;     ↓

Answer + Source



This is the spec sheet I'd use as the baseline for the actual implementation.



Pasted markdown.md

File

this is the reference spec sheet...now give specs for my project



Yes — now I understand what you mean. You don't want a generic list of RAG features. You want a specification sheet written in the same level of detail and structure as your reference spec sheet, but customized for your AI-Powered College Information Assistant. The reference is a full implementation specification covering stack, architecture, APIs, database, folder structure, phases, UI, security, and final outcome.



Below is the equivalent spec for your project.



AI-Powered College Information Assistant — Full Specification

1\. Project Overview \& Tech Stack

Project Overview



Build a full-stack AI-powered College Information Assistant that allows students to ask questions about college-related information in natural language. The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from official college documents before generating an answer.



The platform must support document upload and processing, text extraction, intelligent chunking, embedding generation, vector storage, semantic retrieval, LLM-based answer generation, source citations, authentication, conversation history, and administrator document management.



The system must not function as a simple LLM chatbot. Every knowledge-based answer must go through the retrieval pipeline:



College Documents

&#x20;      ↓

Text Extraction

&#x20;      ↓

Text Cleaning

&#x20;      ↓

Chunking

&#x20;      ↓

Embedding Generation

&#x20;      ↓

Vector Database

&#x20;      ↓

Semantic Search

&#x20;      ↓

Relevant Context

&#x20;      ↓

LLM

&#x20;      ↓

Answer + Sources

Tech Stack

Frontend: React.js, Vite, Tailwind CSS, Axios

Backend: Python, FastAPI

Database: PostgreSQL / Supabase

Vector Database: PostgreSQL with pgvector

Authentication: Supabase Auth / JWT

Storage: Supabase Storage

RAG Framework: LangChain

LLM: Google Gemini / OpenAI

Embedding Model: Gemini Embeddings / OpenAI Embeddings

PDF Processing: PyMuPDF

DOCX Processing: python-docx

OCR: Tesseract/PaddleOCR

Real-time Responses: Server-Sent Events / streaming

Deployment: Vercel + Render/Railway

Version Control: Git + GitHub



This stack directly supports the core requirement of combining document retrieval with generation rather than simply calling an LLM.



2\. Authentication, Chat \& RAG Orchestration

Authentication



The authentication system must support:



Student registration

Student login

Admin login

Session management

Protected routes

Role-based authorization

Password security

User profile retrieval

Persistent login state



Roles:



STUDENT

ADMIN

Student



Students can:



Ask questions

View answers

View sources

Create conversations

View chat history

Submit feedback

Admin



Administrators can:



Upload documents

Update documents

Delete documents

Manage document categories

Manage departments

View document processing status

View usage analytics

3\. Document Management



Admins must be able to upload college resources including:



PDF

DOC

DOCX

TXT



Supported documents can include:



Academic regulations

Admission brochures

Fee structures

Examination regulations

Academic calendars

Hostel rules

Library rules

Placement information

Scholarship information

Department information

Course curriculum

College notices

FAQs

Student policies



Each document must have metadata:



documentId

title

filename

category

department

version

uploadedBy

uploadDate

status

4\. RAG Pipeline

Document Ingestion



When an administrator uploads a document:



Upload

&#x20; ↓

File Validation

&#x20; ↓

Text Extraction

&#x20; ↓

Cleaning

&#x20; ↓

Chunking

&#x20; ↓

Metadata Assignment

&#x20; ↓

Embedding Generation

&#x20; ↓

Vector Storage



The system must store both the original document metadata and the individual chunks.



Chunking



Initial configuration:



Chunk Size: 500–800 tokens

Chunk Overlap: 50–100 tokens



Each chunk should preserve:



document\_id

chunk\_id

page\_number

content

category

department

version

5\. Embedding \& Vector Search



The system must convert every document chunk into a numerical vector representation.



Document Chunk

&#x20;     ↓

Embedding Model

&#x20;     ↓

Vector

&#x20;     ↓

pgvector



When a student asks a question:



Student Query

&#x20;     ↓

Query Embedding

&#x20;     ↓

Vector Similarity Search

&#x20;     ↓

Top-K Relevant Chunks



Initial retrieval configuration:



Top-K = 5

Similarity Metric = Cosine Similarity



The retrieval threshold should be configurable and evaluated using representative college questions rather than assumed to be universally correct.



6\. RAG Answer Generation



The retrieved chunks are passed to the LLM as context.



Example:



SYSTEM:

You are a college information assistant.



Answer the user's question using only the

provided college knowledge base.



If the information is unavailable,

clearly state that it was not found.



CONTEXT:

\[Retrieved Chunk 1]



\[Retrieved Chunk 2]



\[Retrieved Chunk 3]



USER QUESTION:

What is the minimum attendance required?



The generated response must include:



Answer

\+

Source References

7\. Unknown Question Handling



The assistant must avoid hallucinating information.



If retrieval does not produce sufficiently relevant information:



I couldn't find reliable information about this

in the college knowledge base.



The system must not generate an unsupported answer simply because the LLM knows something about the topic.



This is an important acceptance criterion for the RAG system.



8\. Source / Citation System



Every knowledge-based answer should contain source information.



Example:



Answer:



The minimum attendance requirement is 75%.



Sources:



📄 Academic Regulations 2026

Page 12



Internally, each source should retain:



document\_id

document\_name

chunk\_id

page\_number

similarity\_score



This allows the frontend to display where the answer came from.



9\. Conversation Management



Students must be able to:



Start a new conversation

Continue previous conversations

View conversation history

Rename conversations

Delete conversations

Maintain contextual conversation history



Example:



Conversation

&#x20;├── User: What is the attendance requirement?

&#x20;├── AI: It is 75%.

&#x20;├── User: What happens if I have 70%?

&#x20;└── AI: According to the regulations...



The RAG pipeline should use the conversation context carefully when resolving follow-up questions.



10\. Advanced RAG Pipeline



For the enhanced version, the retrieval system should support:



&#x20;                 User Query

&#x20;                     │

&#x20;                     ▼

&#x20;               Query Processing

&#x20;                     │

&#x20;            ┌────────┴────────┐

&#x20;            ▼                 ▼

&#x20;      Keyword Search    Semantic Search

&#x20;            │                 │

&#x20;            └────────┬────────┘

&#x20;                     ▼

&#x20;               Hybrid Results

&#x20;                     │

&#x20;                     ▼

&#x20;                 Re-ranking

&#x20;                     │

&#x20;                     ▼

&#x20;               Top Relevant

&#x20;                  Chunks

&#x20;                     │

&#x20;                     ▼

&#x20;               Context Builder

&#x20;                     │

&#x20;                     ▼

&#x20;                    LLM

&#x20;                     │

&#x20;                     ▼

&#x20;            Answer + Citations



Hybrid retrieval and re-ranking are enhancements, not requirements for the first MVP.



11\. Frontend Pages



The frontend should contain:



/



Landing page containing:



Project introduction

AI assistant explanation

RAG explanation

Feature highlights

Login button

Start Chat button

/login



Login page with:



Email

Password

Validation

Error handling

/register



Registration page with:



Name

Email

Password

Confirm password

/dashboard



Student dashboard containing:



Welcome section

New conversation

Recent conversations

Suggested questions

Frequently asked topics

/chat



Main AI assistant interface containing:



Conversation sidebar

Message area

Question input

AI response

Source references

Loading/streaming state

Feedback buttons

/admin



Admin dashboard containing:



Document statistics

Uploaded documents

Processing status

Upload controls

Search/filter

Delete/update actions

/admin/documents



Document management page containing:



Upload

Search

Category filter

Department filter

Version information

Processing status

Delete

Update

/settings



User settings containing:



Profile

Password/security

Account information

Preferences

12\. Backend Architecture



The backend should follow a layered architecture:



Routes

&#x20;  ↓

Controllers

&#x20;  ↓

Services

&#x20;  ↓

RAG / AI Layer

&#x20;  ↓

Database / Vector Store

Routes



Handle:



HTTP routing

Authentication middleware

Validation

Request/response handling

Controllers



Controllers should remain thin.



They should:



Receive request

Validate input

Call service

Return response

Services



Business logic should live here:



authService

documentService

processingService

embeddingService

ragService

chatService

conversationService

adminService

feedbackService

RAG Layer



Responsible for:



Query embedding

Retrieval

Context construction

Prompt generation

LLM invocation

Citation extraction

Unknown-question handling

13\. Database Tables

Users

Users

&#x20;├── id

&#x20;├── name

&#x20;├── email

&#x20;├── role

&#x20;├── created\_at

&#x20;└── last\_login

Documents

Documents

&#x20;├── id

&#x20;├── title

&#x20;├── filename

&#x20;├── category

&#x20;├── department

&#x20;├── version

&#x20;├── file\_url

&#x20;├── status

&#x20;├── uploaded\_by

&#x20;├── created\_at

&#x20;└── updated\_at

Document Chunks

DocumentChunks

&#x20;├── id

&#x20;├── document\_id

&#x20;├── chunk\_index

&#x20;├── content

&#x20;├── page\_number

&#x20;├── embedding

&#x20;├── metadata

&#x20;└── created\_at

Conversations

Conversations

&#x20;├── id

&#x20;├── user\_id

&#x20;├── title

&#x20;├── created\_at

&#x20;└── updated\_at

Messages

Messages

&#x20;├── id

&#x20;├── conversation\_id

&#x20;├── role

&#x20;├── content

&#x20;├── created\_at

&#x20;└── metadata

Message Sources

MessageSources

&#x20;├── id

&#x20;├── message\_id

&#x20;├── document\_id

&#x20;├── chunk\_id

&#x20;├── page\_number

&#x20;└── similarity\_score

Feedback

Feedback

&#x20;├── id

&#x20;├── message\_id

&#x20;├── user\_id

&#x20;├── rating

&#x20;├── comment

&#x20;└── created\_at

14\. API Endpoints

Health

GET /api/health

Authentication

POST /api/auth/register

POST /api/auth/login

POST /api/auth/logout

GET  /api/auth/me

Chat

POST /api/chat

GET  /api/chat/history

GET  /api/chat/:conversationId

DELETE /api/chat/:conversationId

Documents

POST   /api/documents/upload

GET    /api/documents

GET    /api/documents/:id

PUT    /api/documents/:id

DELETE /api/documents/:id

RAG

POST /api/rag/query

POST /api/rag/reindex

GET  /api/rag/status

Feedback

POST /api/feedback

Admin

GET /api/admin/dashboard

GET /api/admin/analytics

15\. API Chat Response



Example:



{

&#x20; "answer": "The minimum attendance requirement is 75%.",

&#x20; "conversationId": "conv\_001",

&#x20; "sources": \[

&#x20;   {

&#x20;     "documentId": "doc\_001",

&#x20;     "documentName": "Academic Regulations 2026.pdf",

&#x20;     "page": 12,

&#x20;     "similarityScore": 0.91

&#x20;   }

&#x20; ]

}

16\. Folder Structure

Frontend

client/

└── src/

&#x20;   ├── components/

&#x20;   │   ├── AppShell/

&#x20;   │   ├── ChatWindow/

&#x20;   │   ├── ChatInput/

&#x20;   │   ├── MessageBubble/

&#x20;   │   ├── SourceCard/

&#x20;   │   ├── ConversationSidebar/

&#x20;   │   ├── DocumentTable/

&#x20;   │   └── ProtectedRoute/

&#x20;   │

&#x20;   ├── pages/

&#x20;   │   ├── index.jsx

&#x20;   │   ├── login.jsx

&#x20;   │   ├── register.jsx

&#x20;   │   ├── dashboard.jsx

&#x20;   │   ├── chat.jsx

&#x20;   │   ├── settings.jsx

&#x20;   │   └── admin/

&#x20;   │       ├── index.jsx

&#x20;   │       └── documents.jsx

&#x20;   │

&#x20;   ├── store/

&#x20;   │   ├── authStore.js

&#x20;   │   └── chatStore.js

&#x20;   │

&#x20;   └── services/

&#x20;       └── api.js

Backend

server/

└── app/

&#x20;   ├── config/

&#x20;   │   ├── settings.py

&#x20;   │   └── database.py

&#x20;   │

&#x20;   ├── routes/

&#x20;   │   ├── auth.py

&#x20;   │   ├── chat.py

&#x20;   │   ├── documents.py

&#x20;   │   ├── rag.py

&#x20;   │   └── admin.py

&#x20;   │

&#x20;   ├── controllers/

&#x20;   │   ├── auth\_controller.py

&#x20;   │   ├── chat\_controller.py

&#x20;   │   └── document\_controller.py

&#x20;   │

&#x20;   ├── services/

&#x20;   │   ├── auth\_service.py

&#x20;   │   ├── document\_service.py

&#x20;   │   ├── processing\_service.py

&#x20;   │   ├── embedding\_service.py

&#x20;   │   ├── rag\_service.py

&#x20;   │   └── chat\_service.py

&#x20;   │

&#x20;   ├── rag/

&#x20;   │   ├── loader.py

&#x20;   │   ├── splitter.py

&#x20;   │   ├── embeddings.py

&#x20;   │   ├── retriever.py

&#x20;   │   ├── reranker.py

&#x20;   │   ├── prompt.py

&#x20;   │   └── generator.py

&#x20;   │

&#x20;   ├── models/

&#x20;   │   ├── user.py

&#x20;   │   ├── document.py

&#x20;   │   ├── chunk.py

&#x20;   │   ├── conversation.py

&#x20;   │   ├── message.py

&#x20;   │   └── feedback.py

&#x20;   │

&#x20;   └── main.py

17\. Development Phases

Phase 1 — Project Setup

React/Vite frontend

FastAPI backend

Supabase setup

Authentication

Basic UI

Protected routes

Phase 2 — Document Management

Admin dashboard

PDF upload

File storage

Text extraction

Document metadata

Document CRUD

Phase 3 — RAG Ingestion

Text cleaning

Chunking

Embedding generation

pgvector integration

Vector indexing

Phase 4 — RAG Query System

Query embedding

Semantic similarity search

Top-K retrieval

Context construction

LLM integration

Answer generation

Phase 5 — Chat System

Chat interface

Conversation history

Contextual follow-up questions

Source display

Unknown-question handling

Phase 6 — Advanced Features

Hybrid search

Re-ranking

OCR

Multilingual support

Streaming responses

Feedback

Analytics

Phase 7 — Deployment \& Testing

Frontend deployment

Backend deployment

Database configuration

Environment variables

Security testing

RAG evaluation

End-to-end testing

18\. UI/UX Requirements



The application should use a clean, modern AI-assistant interface.



Requirements:



Responsive design

Mobile-friendly interface

Student-friendly navigation

Chat-style conversation UI

Markdown rendering

Source cards

Loading states

Skeleton loaders

Streaming response animation

Error states

Empty states

Admin dashboard

Document upload progress

Document processing indicators

Dark/light theme support



The chat response should visually separate:



┌──────────────────────────────────┐

│ AI Assistant                     │

│                                  │

│ The attendance requirement is    │

│ 75%.                             │

│                                  │

│ Sources                          │

│ ┌──────────────────────────────┐ │

│ │ Academic Regulations 2026    │ │

│ │ Page 12                      │ │

│ └──────────────────────────────┘ │

│                                  │

│ 👍 Helpful    👎 Not helpful      │

└──────────────────────────────────┘

19\. Security Requirements



The application must:



Protect API endpoints with authentication

Enforce student/admin authorization

Store API keys only in environment variables

Validate uploaded file types

Limit upload file size

Sanitize extracted document content where appropriate

Use HTTPS in production

Protect database credentials

Restrict CORS to the frontend domain

Never expose LLM API keys to the frontend

Prevent unauthorized document deletion

Prevent students from accessing admin APIs



For uploaded documents, the backend should validate:



Allowed extensions

Maximum file size

MIME type

Processing status

20\. RAG Evaluation



This is something I'd strongly recommend adding to your spec, because it makes the project much stronger academically.



Create a test dataset containing:



Question

Expected Answer

Expected Source



Example:



Question	Expected Source

What is the minimum attendance?	Academic Regulations

When does semester examination begin?	Academic Calendar

What is the hostel fee?	Hostel Fee Structure

What scholarships are available?	Scholarship Policy



Evaluate:



Retrieval relevance

Retrieval precision

Answer correctness

Citation correctness

Hallucination rate

Unknown-question accuracy

Response latency

21\. Final Expected Outcome



The completed system must allow a student to ask a college-related question in natural language, retrieve relevant information from the college's uploaded knowledge base, generate an answer grounded in the retrieved context, and display the supporting document/source.



Administrators must be able to upload, update, and delete college documents, while the system automatically processes those documents into searchable vector representations.



The final application should provide:



Student

&#x20;  │

&#x20;  ▼

Ask Question

&#x20;  │

&#x20;  ▼

Query Embedding

&#x20;  │

&#x20;  ▼

Vector Search

&#x20;  │

&#x20;  ▼

Relevant College Documents

&#x20;  │

&#x20;  ▼

Context

&#x20;  │

&#x20;  ▼

LLM

&#x20;  │

&#x20;  ▼

Grounded Answer

&#x20;  │

&#x20;  ├── Source

&#x20;  ├── Page

&#x20;  └── Relevance



The key distinction from a normal chatbot is that the knowledge comes from the college's document repository through an actual retrieval pipeline. The reference spec follows the same philosophy of defining the complete stack, architecture, APIs, persistence, development phases, security, and final behavior rather than only describing the product idea.

