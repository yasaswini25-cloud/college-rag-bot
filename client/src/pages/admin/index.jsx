import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Layers, 
  Users, 
  MessageSquare, 
  ThumbsUp, 
  ThumbsDown, 
  ShieldCheck, 
  ArrowRight,
  RefreshCw,
  PieChart,
  FolderOpen
} from 'lucide-react';
import api from '../../services/api';

export default function AdminDashboardPage() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const res = await api.get('/admin/dashboard');
      setMetrics(res.data);
    } catch (err) {
      console.error("Failed to load admin metrics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const metricCards = [
    { title: "Indexed Documents", value: metrics?.totalDocuments || 0, icon: FileText, color: "from-blue-600 to-indigo-600" },
    { title: "Vector Chunks", value: metrics?.totalChunks || 0, icon: Layers, color: "from-indigo-600 to-purple-600" },
    { title: "Registered Users", value: metrics?.totalUsers || 0, icon: Users, color: "from-purple-600 to-pink-600" },
    { title: "Queries Answered", value: metrics?.totalQueries || 0, icon: MessageSquare, color: "from-emerald-600 to-teal-600" },
  ];

  return (
    <div className="flex-1 max-w-7xl mx-auto w-full p-4 sm:p-6 lg:p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4" />
            <span>Administrator Control Console</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight mt-1">
            Knowledge Base & System Analytics
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchMetrics}
            className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <Link
            to="/admin/documents"
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all hover:scale-105"
          >
            <FolderOpen className="w-4 h-4" />
            <span>Manage Documents</span>
          </Link>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 flex items-center gap-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${card.color} flex items-center justify-center text-white shrink-0 shadow`}>
                <Icon className="w-6 h-6" />
              </div>
              <div>
                <div className="text-xs font-medium text-slate-400">{card.title}</div>
                <div className="text-2xl font-bold text-white tracking-tight mt-0.5">
                  {card.value}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Category & Status Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Knowledge Area Distribution */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Category Distribution
            </h2>
            <PieChart className="w-4 h-4 text-indigo-400" />
          </div>

          <div className="space-y-2.5">
            {metrics?.categories && Object.keys(metrics.categories).length > 0 ? (
              Object.entries(metrics.categories).map(([cat, count]) => (
                <div key={cat} className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs">
                  <span className="font-medium text-slate-300">{cat}</span>
                  <span className="font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                    {count} doc(s)
                  </span>
                </div>
              ))
            ) : (
              <div className="py-6 text-center text-xs text-slate-400">No category data yet.</div>
            )}
          </div>
        </div>

        {/* Student Feedback Breakdown */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Student Answer Satisfaction
          </h2>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                <ThumbsUp className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-bold text-emerald-300">
                  {metrics?.feedback?.positive || 0}
                </div>
                <div className="text-xs text-slate-400">Helpful Answers</div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/20 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-rose-500/20 flex items-center justify-center text-rose-400">
                <ThumbsDown className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-bold text-rose-300">
                  {metrics?.feedback?.negative || 0}
                </div>
                <div className="text-xs text-slate-400">Needs Review</div>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-400 space-y-1">
            <div className="font-semibold text-slate-300">Quality Assurance Guideline</div>
            <p>Every negative feedback report is logged to assist in updating outdated handbooks and adding missing circulars.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
