import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  MessageSquare, 
  BookOpen, 
  ArrowRight, 
  Clock, 
  ShieldCheck, 
  GraduationCap, 
  Award,
  Building,
  Briefcase,
  HelpCircle
} from 'lucide-react';
import { useAuth } from '../store/authStore';
import api from '../services/api';

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await api.get('/chat/history');
        setConversations(res.data || []);
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const knowledgeCards = [
    {
      title: "Academic Regulations",
      desc: "Attendance requirements, condonation rules, grading scale & backlogs.",
      category: "Regulations",
      query: "What is the minimum attendance required and condonation rules?",
      icon: BookOpen,
      color: "from-blue-500/20 to-indigo-500/20 text-indigo-400"
    },
    {
      title: "Admissions 2026",
      desc: "Eligibility criteria, required documents, quotas & refund guidelines.",
      category: "Admissions",
      query: "What are the required documents for admission verification?",
      icon: GraduationCap,
      color: "from-emerald-500/20 to-teal-500/20 text-emerald-400"
    },
    {
      title: "Hostel & Fees",
      desc: "Room types, mess charges, biometric attendance & night curfew timings.",
      category: "Hostel & Fees",
      query: "What are the hostel room categories and annual fees?",
      icon: Building,
      color: "from-amber-500/20 to-orange-500/20 text-amber-400"
    },
    {
      title: "Placements & Career",
      desc: "Tier 1, Tier 2 Dream & Super Dream recruitment policies.",
      category: "Placements",
      query: "How does the Tier 2 Dream and Super Dream placement policy work?",
      icon: Briefcase,
      color: "from-purple-500/20 to-pink-500/20 text-purple-400"
    },
    {
      title: "Library & Scholarships",
      desc: "Borrowing limits, Founder's Excellence & means-cum-merit grants.",
      category: "Library & Scholarships",
      query: "What are the criteria for Founder's Excellence scholarships?",
      icon: Award,
      color: "from-rose-500/20 to-red-500/20 text-rose-400"
    }
  ];

  const handleAskQuestion = (query) => {
    navigate(`/chat?prompt=${encodeURIComponent(query)}`);
  };

  return (
    <div className="flex-1 max-w-7xl mx-auto w-full p-4 sm:p-6 lg:p-8 space-y-8">
      {/* Welcome Banner */}
      <div className="rounded-3xl border border-slate-800 bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-purple-950/30 p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Campus Intelligence Hub</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Hello, {user?.name || 'Student'}! 👋
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Ask any question about college rules, hostel policies, exams, or placements.
          </p>
        </div>

        <Link
          to="/chat"
          className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all hover:scale-105 shrink-0"
        >
          <MessageSquare className="w-4 h-4" />
          <span>New AI Conversation</span>
        </Link>
      </div>

      {/* Grid Layout: Left Knowledge Areas, Right Recent History */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Knowledge Topics */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">
              Institutional Knowledge Areas
            </h2>
            <span className="text-xs text-slate-400">Click topic to query</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            {knowledgeCards.map((card, idx) => {
              const Icon = card.icon;
              return (
                <div
                  key={idx}
                  onClick={() => handleAskQuestion(card.query)}
                  className="p-4 rounded-2xl border border-slate-800 bg-slate-900/50 hover:bg-slate-900 hover:border-indigo-500/40 cursor-pointer transition-all group flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className={`w-9 h-9 rounded-xl bg-gradient-to-tr ${card.color} flex items-center justify-center`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-200 group-hover:text-indigo-300 transition-colors">
                        {card.title}
                      </h3>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                        {card.desc}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-indigo-400 font-medium group-hover:translate-x-1 transition-transform">
                    <span>Ask assistant</span>
                    <ArrowRight className="w-3 h-3" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Recent Conversations */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">
              Recent Inquiries
            </h2>
            <Link to="/chat" className="text-xs text-indigo-400 hover:underline">
              View all
            </Link>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-3 space-y-2">
            {loading ? (
              <div className="py-8 text-center text-xs text-slate-400">Loading history...</div>
            ) : conversations.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400 space-y-2">
                <MessageSquare className="w-6 h-6 mx-auto opacity-30 text-slate-400" />
                <p>No previous conversations.</p>
                <Link to="/chat" className="text-indigo-400 underline block">
                  Start your first query
                </Link>
              </div>
            ) : (
              conversations.slice(0, 6).map((c) => (
                <Link
                  key={c.id}
                  to={`/chat?id=${c.id}`}
                  className="flex items-center justify-between p-2.5 rounded-xl hover:bg-slate-800/60 transition-colors text-xs group"
                >
                  <div className="flex items-center gap-2.5 min-w-0 pr-2">
                    <MessageSquare className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-400 shrink-0" />
                    <span className="text-slate-300 font-medium truncate group-hover:text-white">
                      {c.title}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-[10px] text-slate-400 shrink-0">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>{new Date(c.updated_at || c.created_at).toLocaleDateString()}</span>
                  </div>
                </Link>
              ))
            )}
          </div>

          {/* Institutional Trust Badge */}
          <div className="p-4 rounded-2xl border border-emerald-500/20 bg-emerald-950/10 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div className="text-xs text-slate-300">
              <div className="font-semibold text-emerald-300">Grounded in College Truth</div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                All answers are verified against official 2026-2027 college publications.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
