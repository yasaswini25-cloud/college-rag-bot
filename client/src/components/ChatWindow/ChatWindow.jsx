import React, { useRef, useEffect } from 'react';
import { Bot, Sparkles, BookOpen, Search, HelpCircle, ShieldCheck } from 'lucide-react';
import MessageBubble from '../MessageBubble/MessageBubble';

export default function ChatWindow({ messages = [], sending = false, onPromptClick }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const sampleQuestions = [
    {
      title: "Attendance Regulations",
      query: "What is the minimum attendance required and condonation rules?",
      category: "Regulations"
    },
    {
      title: "Hostel Fee & Curfew",
      query: "What are the hostel room charges and campus curfew timings?",
      category: "Hostel & Fees"
    },
    {
      title: "Placement Dream Policy",
      query: "How does the Tier 2 and Super Dream placement policy work?",
      category: "Placements"
    },
    {
      title: "Scholarships & Library",
      query: "What are the Founder's Excellence scholarships and library borrowing limits?",
      category: "Library & Scholarships"
    }
  ];

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
      {messages.length === 0 ? (
        <div className="max-w-3xl mx-auto py-12 px-4 text-center space-y-6">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center mx-auto shadow-xl shadow-indigo-600/20">
            <Sparkles className="w-8 h-8 text-white" />
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-bold tracking-tight text-white">
              Official College Knowledge Assistant
            </h2>
            <p className="text-sm text-slate-400 max-w-lg mx-auto">
              Every answer is strictly retrieved and cited from verified institutional policies, handbooks, and official circulars.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left pt-4">
            {sampleQuestions.map((sq, i) => (
              <button
                key={i}
                onClick={() => onPromptClick && onPromptClick(sq.query)}
                className="p-3.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-indigo-500/40 text-xs transition-all group shadow-sm text-left flex flex-col justify-between"
              >
                <div className="font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors flex items-center justify-between">
                  <span>{sq.title}</span>
                  <span className="text-[10px] font-mono text-slate-400">{sq.category}</span>
                </div>
                <div className="text-slate-400 mt-1 line-clamp-2">{sq.query}</div>
              </button>
            ))}
          </div>

          <div className="flex items-center justify-center gap-6 pt-4 text-xs text-slate-400">
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Zero-hallucination guardrails</span>
            </div>
            <div className="flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-indigo-400" />
              <span>Verified document sources</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((msg, idx) => (
            <MessageBubble key={msg.id || idx} message={msg} />
          ))}

          {/* Thinking / Retrieval state */}
          {sending && (
            <div className="flex gap-3.5 my-4 justify-start animate-fade-in">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shrink-0 shadow-md shadow-indigo-600/20 mt-1">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-slate-900/90 border border-slate-800/90 rounded-2xl p-4 text-xs text-slate-300 flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-slate-400 font-medium">
                  Performing semantic vector retrieval across college knowledge base...
                </span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}
