import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, ThumbsUp, ThumbsDown, Copy, Check, Sparkles, BookOpen, Clock } from 'lucide-react';
import SourceCard from '../SourceCard/SourceCard';
import api from '../../services/api';

export default function MessageBubble({ message }) {
  const [copied, setCopied] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState(null); // 'helpful' or 'unhelpful'
  const isAssistant = message.role === 'assistant';

  const metadata = message.metadata || {};
  const sources = metadata.sources || [];
  const latency = metadata.latency_ms;
  const isGrounded = metadata.grounded !== false;

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleFeedback = async (rating) => {
    if (feedbackGiven) return;
    try {
      setFeedbackGiven(rating > 0 ? 'helpful' : 'unhelpful');
      await api.post('/feedback', {
        messageId: message.id,
        rating: rating
      });
    } catch (err) {
      console.error("Failed to submit feedback:", err);
    }
  };

  return (
    <div className={`flex gap-3.5 my-4 ${isAssistant ? 'justify-start' : 'justify-end'}`}>
      {isAssistant && (
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shrink-0 shadow-md shadow-indigo-600/20 mt-1">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={`max-w-3xl rounded-2xl p-4 sm:p-5 transition-all shadow-sm ${
        isAssistant 
          ? 'bg-slate-900/90 border border-slate-800/90 text-slate-200' 
          : 'bg-indigo-600 text-white shadow-indigo-600/10'
      }`}>
        {/* Message Header */}
        <div className="flex items-center justify-between gap-3 mb-2.5 pb-2 border-b border-slate-800/40 text-xs">
          <div className="flex items-center gap-2 font-medium">
            {isAssistant ? (
              <span className="flex items-center gap-1.5 text-indigo-400 font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                College AI Assistant
              </span>
            ) : (
              <span className="text-indigo-100 font-medium">You</span>
            )}
          </div>
          
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            {isAssistant && latency && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-400" />
                {latency}ms
              </span>
            )}
            <button
              onClick={handleCopy}
              title="Copy message text"
              className="p-1 rounded hover:bg-slate-800/60 text-slate-400 hover:text-slate-200 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        {/* Message Content */}
        <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-ul:my-2 prose-li:my-0.5">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Sources Section */}
        {isAssistant && sources && sources.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-800/80">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300 mb-2.5">
              <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
              <span>Cited Official Sources ({sources.length})</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {sources.map((src, idx) => (
                <SourceCard key={idx} source={src} />
              ))}
            </div>
          </div>
        )}

        {/* Feedback Actions for Assistant */}
        {isAssistant && (
          <div className="mt-3.5 pt-2.5 border-t border-slate-800/50 flex items-center justify-between text-xs text-slate-400">
            <span className="text-[11px]">Was this document-grounded answer helpful?</span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => handleFeedback(1)}
                disabled={!!feedbackGiven}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium border transition-colors ${
                  feedbackGiven === 'helpful'
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                    : 'border-slate-800 hover:border-slate-700 hover:bg-slate-800/60 text-slate-300'
                }`}
              >
                <ThumbsUp className="w-3 h-3 text-emerald-400" />
                <span>Helpful</span>
              </button>
              <button
                onClick={() => handleFeedback(-1)}
                disabled={!!feedbackGiven}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium border transition-colors ${
                  feedbackGiven === 'unhelpful'
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                    : 'border-slate-800 hover:border-slate-700 hover:bg-slate-800/60 text-slate-300'
                }`}
              >
                <ThumbsDown className="w-3 h-3 text-rose-400" />
                <span>Not helpful</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {!isAssistant && (
        <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 shadow mt-1">
          <User className="w-4 h-4 text-indigo-300" />
        </div>
      )}
    </div>
  );
}
