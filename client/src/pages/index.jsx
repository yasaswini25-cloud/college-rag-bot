import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  GraduationCap, 
  BookOpen, 
  ShieldCheck, 
  Layers, 
  Search, 
  ArrowRight, 
  CheckCircle2, 
  Database, 
  Cpu, 
  FileCheck,
  Building2,
  Users
} from 'lucide-react';
import { useAuth } from '../store/authStore';

export default function LandingPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const pipelineSteps = [
    { title: "1. Official Documents", desc: "PDFs, DOCX, circulars & regulations ingested directly", icon: BookOpen },
    { title: "2. PyMuPDF Extraction", desc: "Page-aware clean text parsing & structure retention", icon: FileCheck },
    { title: "3. Semantic Chunking", desc: "500-800 token slices with 50-100 token overlap", icon: Layers },
    { title: "4. Vector Embeddings", desc: "Dense 768-dim embeddings generated via Gemini / OpenAI", icon: Cpu },
    { title: "5. pgvector Search", desc: "Cosine similarity retrieval & hybrid BM25 re-ranking", icon: Database },
    { title: "6. Grounded Answer", desc: "Strictly cited answers with page numbers & zero hallucinations", icon: ShieldCheck },
  ];

  const features = [
    {
      title: "Document-Grounded Answers",
      desc: "Every answer is synthesized strictly from official college handbooks, regulations, and fee circulars.",
      icon: BookOpen,
      color: "from-blue-500 to-indigo-500"
    },
    {
      title: "Exact Page Citations",
      desc: "Instant source attribution displaying document title, page number, and similarity score percentage.",
      icon: FileCheck,
      color: "from-indigo-500 to-purple-500"
    },
    {
      title: "Zero-Hallucination Guardrails",
      desc: "Explicit fallback when information is unavailable rather than fabricating unsupported claims.",
      icon: ShieldCheck,
      color: "from-emerald-500 to-teal-500"
    },
    {
      title: "Department & Knowledge Area Filtering",
      desc: "Target specific departments (CSE, ECE, Mech) and domains (Admissions, Hostel, Placements, Exams).",
      icon: Building2,
      color: "from-purple-500 to-pink-500"
    }
  ];

  const sampleQueries = [
    "What is the minimum attendance requirement for semester exams?",
    "What are the hostel room charges and mess timings?",
    "How does the placement Dream & Super Dream policy work?",
    "What scholarships are offered for merit rank holders?"
  ];

  const handleQueryClick = (query) => {
    navigate(isAuthenticated ? `/chat?prompt=${encodeURIComponent(query)}` : '/login');
  };

  return (
    <div className="flex-1 space-y-20 pb-20">
      {/* Hero Section */}
      <section className="relative pt-12 pb-8 sm:pt-20 sm:pb-16 overflow-hidden">
        {/* Background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-indigo-600/15 blur-[120px] rounded-full pointer-events-none" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-6 relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-card text-xs font-semibold text-indigo-300 border border-indigo-500/30 shadow-lg shadow-indigo-500/10">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>AI + RAG College Information Assistant</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Accurate, Grounded Answers for <br className="hidden sm:inline" />
            <span className="gradient-text">Every College Student Query</span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed">
            Eliminate guesswork. Ask questions in natural language and receive answers retrieved directly from official college regulations, admission rules, and fee structures.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <Link
              to={isAuthenticated ? "/chat" : "/login"}
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all hover:scale-105"
            >
              <span>Start Asking Questions</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to={isAuthenticated ? "/dashboard" : "/register"}
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-200 font-semibold text-sm flex items-center justify-center gap-2 transition-all"
            >
              <span>Explore Student Dashboard</span>
            </Link>
          </div>

          {/* Quick Questions Chips */}
          <div className="pt-8">
            <div className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">
              Popular Student Inquiries
            </div>
            <div className="flex flex-wrap items-center justify-center gap-2 max-w-3xl mx-auto">
              {sampleQueries.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleQueryClick(q)}
                  className="px-3.5 py-1.5 rounded-lg bg-slate-900/60 hover:bg-slate-800 border border-slate-800 hover:border-indigo-500/40 text-xs text-slate-300 hover:text-white transition-all text-left"
                >
                  "{q}"
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* RAG Pipeline Visualizer */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center space-y-3 mb-10">
          <div className="text-xs font-mono font-semibold uppercase text-indigo-400 tracking-wider">
            Architecture & Pipeline
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">
            How The RAG Retrieval Pipeline Works
          </h2>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            Not a generic LLM wrapper. Every query is resolved against the institutional knowledge base using vector similarity.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {pipelineSteps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={idx}
                className="p-5 rounded-2xl glass-card relative group hover:-translate-y-1 transition-all duration-200"
              >
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-3 group-hover:scale-110 transition-transform">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-sm font-bold text-slate-200 mb-1">{step.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center space-y-3 mb-10">
          <div className="text-xs font-mono font-semibold uppercase text-indigo-400 tracking-wider">
            Core Capabilities
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">
            Built for Students & Campus Administrators
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div
                key={idx}
                className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900/70 hover:border-slate-700 transition-all flex gap-4 items-start"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${feat.color} flex items-center justify-center text-white shrink-0 shadow-md`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white mb-1.5">{feat.title}</h3>
                  <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">{feat.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA Banner */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="rounded-3xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-slate-900/80 p-8 sm:p-12 text-center space-y-6 shadow-2xl relative overflow-hidden">
          <div className="space-y-2">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
              Ready to explore your college knowledge base?
            </h2>
            <p className="text-sm text-slate-300 max-w-lg mx-auto">
              Get immediate answers to admissions, hostel rules, exam policies, and curriculum details.
            </p>
          </div>

          <div className="flex justify-center">
            <Link
              to={isAuthenticated ? "/chat" : "/login"}
              className="px-6 py-3.5 rounded-xl bg-white text-slate-950 font-bold text-sm hover:bg-slate-100 shadow-xl transition-all hover:scale-105"
            >
              Open AI Chat Assistant
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
