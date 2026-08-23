import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Filter, X } from 'lucide-react';

export default function ChatInput({ onSendMessage, sending = false, initialPrompt = '' }) {
  const [input, setInput] = useState(initialPrompt);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDept, setSelectedDept] = useState('All');
  const [showFilters, setShowFilters] = useState(false);
  const textareaRef = useRef(null);

  const categories = ['All', 'Regulations', 'Admissions', 'Hostel & Fees', 'Placements', 'Library & Scholarships'];
  const departments = ['All', 'Computer Science', 'Electronics & Comm', 'Mechanical', 'Civil', 'Information Tech'];

  useEffect(() => {
    if (initialPrompt) {
      setInput(initialPrompt);
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  }, [initialPrompt]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (!input.trim() || sending) return;
    onSendMessage(
      input.trim(),
      selectedCategory !== 'All' ? selectedCategory : null,
      selectedDept !== 'All' ? selectedDept : null
    );
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  // Auto-resize textarea
  const handleChange = (e) => {
    setInput(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  };

  return (
    <div className="border-t border-slate-800 bg-slate-950/90 p-3 sm:p-4">
      <div className="max-w-4xl mx-auto space-y-2">
        {/* Filter Badges & Toggle */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium border transition-colors ${
                showFilters || selectedCategory !== 'All' || selectedDept !== 'All'
                  ? 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Filter className="w-3 h-3" />
              <span>Target Knowledge Area</span>
              {(selectedCategory !== 'All' || selectedDept !== 'All') && (
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
              )}
            </button>

            {selectedCategory !== 'All' && (
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-800 text-[11px] text-slate-300 border border-slate-700">
                Category: {selectedCategory}
                <X className="w-3 h-3 cursor-pointer hover:text-rose-400" onClick={() => setSelectedCategory('All')} />
              </span>
            )}
            {selectedDept !== 'All' && (
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-800 text-[11px] text-slate-300 border border-slate-700">
                Dept: {selectedDept}
                <X className="w-3 h-3 cursor-pointer hover:text-rose-400" onClick={() => setSelectedDept('All')} />
              </span>
            )}
          </div>

          <span className="text-[11px] text-slate-400 hidden sm:inline">
            Press <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[10px] text-slate-300">Enter ↵</kbd> to query RAG
          </span>
        </div>

        {/* Filter Dropdowns Tray */}
        {showFilters && (
          <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2 animate-fade-in text-xs">
            <div>
              <label className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Document Category</label>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {categories.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => setSelectedCategory(c)}
                    className={`px-2 py-1 rounded-md text-[11px] font-medium transition-colors ${
                      selectedCategory === c
                        ? 'bg-indigo-600 text-white'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Department</label>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {departments.map((d) => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => setSelectedDept(d)}
                    className={`px-2 py-1 rounded-md text-[11px] font-medium transition-colors ${
                      selectedDept === d
                        ? 'bg-purple-600 text-white'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Text Input Container */}
        <div className="relative flex items-end gap-2 p-2 rounded-2xl bg-slate-900/90 border border-slate-800 focus-within:border-indigo-500/60 focus-within:ring-1 focus-within:ring-indigo-500/30 transition-all shadow-inner">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about admissions, attendance rules, fee structure, placements, hostel..."
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-400 focus:outline-none resize-none max-h-40 py-1.5 px-2"
          />

          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className={`p-2.5 rounded-xl flex items-center justify-center shrink-0 transition-all ${
              input.trim() && !sending
                ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 hover:scale-105 active:scale-95'
                : 'bg-slate-800 text-slate-400 cursor-not-allowed'
            }`}
          >
            {sending ? (
              <div className="w-4 h-4 border-2 border-slate-400 border-t-white rounded-full animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
