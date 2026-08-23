import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink, Award } from 'lucide-react';

export default function SourceCard({ source }) {
  const [expanded, setExpanded] = useState(false);

  const docName = source.documentName || source.filename || 'College Document';
  const page = source.page || source.page_number || 1;
  const score = source.similarityScore !== undefined ? source.similarityScore : source.similarity_score;
  const percentage = score !== undefined ? Math.round(score * 100) : null;
  const snippet = source.snippet || source.content || '';
  const category = source.category || 'General';

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 overflow-hidden hover:border-indigo-500/40 transition-all text-xs">
      <div 
        onClick={() => setExpanded(!expanded)}
        className="p-3 flex items-center justify-between cursor-pointer hover:bg-slate-800/40 transition-colors"
      >
        <div className="flex items-center gap-2.5 min-w-0 pr-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0">
            <FileText className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="truncate">
            <div className="font-medium text-slate-200 truncate">{docName}</div>
            <div className="flex items-center gap-2 text-[11px] text-slate-400">
              <span>Page {page}</span>
              <span>•</span>
              <span className="text-slate-400">{category}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {percentage !== null && (
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold border ${
              percentage >= 70 
                ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20' 
                : percentage >= 45 
                ? 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20'
                : 'bg-amber-500/10 text-amber-300 border-amber-500/20'
            }`}>
              {percentage}% Match
            </span>
          )}
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </div>

      {expanded && snippet && (
        <div className="px-3 pb-3 pt-1 border-t border-slate-800/50 bg-slate-950/40 text-slate-300 font-mono text-[11px] leading-relaxed">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-sans font-semibold">
            Retrieved Excerpt:
          </div>
          <div className="p-2 rounded bg-slate-900/80 border border-slate-800 text-slate-300 whitespace-pre-wrap">
            {snippet}
          </div>
        </div>
      )}
    </div>
  );
}
