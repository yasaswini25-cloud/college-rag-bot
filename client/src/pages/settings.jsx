import React, { useEffect, useState } from 'react';
import { User, Shield, Key, Cpu, Sliders, Database, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../store/authStore';
import api from '../services/api';

export default function SettingsPage() {
  const { user } = useAuth();
  const [ragStatus, setRagStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStatus() {
      try {
        const res = await api.get('/rag/status');
        setRagStatus(res.data);
      } catch (err) {
        console.error("Failed to load RAG status:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchStatus();
  }, []);

  return (
    <div className="flex-1 max-w-4xl mx-auto w-full p-4 sm:p-6 lg:p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System & Account Settings</h1>
        <p className="text-xs text-slate-400">View user profile details and current RAG engine parameters.</p>
      </div>

      {/* User Profile Card */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <User className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">{user?.name || 'User Profile'}</h2>
            <p className="text-xs text-slate-400">{user?.email}</p>
          </div>
          <span className="ml-auto px-3 py-1 rounded-full text-xs font-mono font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 uppercase">
            {user?.role || 'STUDENT'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-slate-800 text-xs">
          <div>
            <span className="text-slate-400 block">User Identifier</span>
            <span className="font-mono text-slate-300 text-[11px]">{user?.id}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Account Created</span>
            <span className="text-slate-300">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Active'}
            </span>
          </div>
        </div>
      </div>

      {/* RAG Engine Runtime Config */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center gap-2.5">
          <Sliders className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-bold text-white">RAG Engine Configuration</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-slate-400">LLM Provider</div>
            <div className="text-sm font-bold text-slate-200 uppercase mt-0.5">
              {ragStatus?.llm_provider || 'Gemini / Auto'}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-slate-400">Embedding Engine</div>
            <div className="text-sm font-bold text-slate-200 uppercase mt-0.5">
              {ragStatus?.embedding_provider || 'Gemini / Local 768-D'}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-slate-400">Retrieval Top-K</div>
            <div className="text-sm font-bold text-slate-200 font-mono mt-0.5">
              {ragStatus?.top_k || 5} Documents
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-slate-400">Chunk Size / Overlap</div>
            <div className="text-sm font-bold text-slate-200 font-mono mt-0.5">
              {ragStatus?.chunk_size || 600} / {ragStatus?.chunk_overlap || 80} tok
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-slate-400">Similarity Threshold</div>
            <div className="text-sm font-bold text-slate-200 font-mono mt-0.5">
              {ragStatus?.similarity_threshold || 0.40} Cosine
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-slate-400">Hybrid Search (BM25)</div>
            <div className="text-sm font-bold text-emerald-400 flex items-center gap-1 mt-0.5">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Enabled
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
