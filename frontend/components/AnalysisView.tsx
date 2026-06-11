import React, { useState } from 'react';
import { FileText, GitCompare, Download, Loader2, AlertCircle } from 'lucide-react';
import { Document } from '../types';
import { generateSummary, compareDocuments } from '../services/gemini';

interface AnalysisViewProps {
  documents: Document[];
}

const AnalysisView: React.FC<AnalysisViewProps> = ({ documents }) => {
  const [mode, setMode] = useState<'summary' | 'compare'>('summary');
  
  // Summary State
  const [selectedDocForSummary, setSelectedDocForSummary] = useState<string>('');
  const [summaryResult, setSummaryResult] = useState<string>('');
  
  // Compare State
  const [doc1Id, setDoc1Id] = useState<string>('');
  const [doc2Id, setDoc2Id] = useState<string>('');
  const [compareResult, setCompareResult] = useState<string>('');
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateSummary = async () => {
    if (!selectedDocForSummary) return;
    const doc = documents.find(d => d.id === selectedDocForSummary);
    if (!doc) return;

    setIsLoading(true);
    setError(null);
    try {
      const result = await generateSummary(doc.content);
      setSummaryResult(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompare = async () => {
    if (!doc1Id || !doc2Id || doc1Id === doc2Id) {
      setError("Please select two different documents to compare.");
      return;
    }
    const doc1 = documents.find(d => d.id === doc1Id);
    const doc2 = documents.find(d => d.id === doc2Id);
    if (!doc1 || !doc2) return;

    setIsLoading(true);
    setError(null);
    try {
      const result = await compareDocuments(doc1.name, doc1.content, doc2.name, doc2.content);
      setCompareResult(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Simple markdown renderer for the results
  const renderMarkdown = (text: string) => {
    if (!text) return null;
    const lines = text.split('\n');
    return lines.map((line, i) => {
      if (line.startsWith('## ')) return <h2 key={i} className="text-xl font-bold mt-6 mb-3 text-slate-800">{line.replace('## ', '')}</h2>;
      if (line.startsWith('# ')) return <h1 key={i} className="text-2xl font-bold mt-6 mb-4 text-slate-900">{line.replace('# ', '')}</h1>;
      if (line.startsWith('- **') || line.startsWith('* **')) {
        const parts = line.split('**');
        return <li key={i} className="ml-4 mb-2 text-slate-700"><span className="font-bold">{parts[1]}</span>{parts.slice(2).join('**')}</li>;
      }
      if (line.startsWith('- ') || line.startsWith('* ')) return <li key={i} className="ml-4 mb-2 text-slate-700">{line.substring(2)}</li>;
      if (line.trim() === '') return <br key={i} />;
      // Handle bold text within paragraphs
      const boldParts = line.split('**');
      if (boldParts.length > 1) {
         return (
           <p key={i} className="mb-3 text-slate-700 leading-relaxed">
             {boldParts.map((part, j) => j % 2 === 1 ? <strong key={j}>{part}</strong> : part)}
           </p>
         );
      }
      return <p key={i} className="mb-3 text-slate-700 leading-relaxed">{line}</p>;
    });
  };

  return (
    <div className="p-6 h-full overflow-y-auto bg-slate-50">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Deep Analysis</h1>
        <p className="text-slate-500">Generate structured summaries or compare multiple filings.</p>
      </div>

      {/* Mode Toggle */}
      <div className="flex space-x-1 bg-slate-200 p-1 rounded-lg w-fit mb-8">
        <button
          onClick={() => setMode('summary')}
          className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${mode === 'summary' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
        >
          <FileText size={16} className="mr-2" />
          Structured Summary
        </button>
        <button
          onClick={() => setMode('compare')}
          className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${mode === 'compare' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
        >
          <GitCompare size={16} className="mr-2" />
          Compare Documents
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-lg flex items-start text-rose-700">
          <AlertCircle size={20} className="mr-3 mt-0.5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Summary Mode */}
      {mode === 'summary' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <label className="block text-sm font-medium text-slate-700 mb-2">Select Document to Summarize</label>
            <div className="flex space-x-4">
              <select 
                className="flex-1 border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                value={selectedDocForSummary}
                onChange={(e) => setSelectedDocForSummary(e.target.value)}
              >
                <option value="">-- Select a document --</option>
                {documents.map(doc => (
                  <option key={doc.id} value={doc.id}>{doc.name}</option>
                ))}
              </select>
              <button 
                onClick={handleGenerateSummary}
                disabled={!selectedDocForSummary || isLoading}
                className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 flex items-center transition-colors"
              >
                {isLoading ? <Loader2 size={18} className="animate-spin mr-2" /> : <FileText size={18} className="mr-2" />}
                Generate
              </button>
            </div>
          </div>

          {summaryResult && (
            <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm relative">
              <button 
                onClick={() => handleExport(summaryResult, 'Summary_Report')}
                className="absolute top-6 right-6 text-slate-400 hover:text-indigo-600 flex items-center text-sm font-medium transition-colors"
              >
                <Download size={16} className="mr-1" /> Export
              </button>
              <div className="prose prose-slate max-w-none">
                {renderMarkdown(summaryResult)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Compare Mode */}
      {mode === 'compare' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Document A (Baseline)</label>
                <select 
                  className="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                  value={doc1Id}
                  onChange={(e) => setDoc1Id(e.target.value)}
                >
                  <option value="">-- Select first document --</option>
                  {documents.map(doc => (
                    <option key={doc.id} value={doc.id}>{doc.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Document B (Comparison)</label>
                <select 
                  className="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                  value={doc2Id}
                  onChange={(e) => setDoc2Id(e.target.value)}
                >
                  <option value="">-- Select second document --</option>
                  {documents.map(doc => (
                    <option key={doc.id} value={doc.id}>{doc.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex justify-end">
              <button 
                onClick={handleCompare}
                disabled={!doc1Id || !doc2Id || doc1Id === doc2Id || isLoading}
                className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 flex items-center transition-colors"
              >
                {isLoading ? <Loader2 size={18} className="animate-spin mr-2" /> : <GitCompare size={18} className="mr-2" />}
                Compare Documents
              </button>
            </div>
          </div>

          {compareResult && (
            <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm relative">
               <button 
                onClick={() => handleExport(compareResult, 'Comparison_Report')}
                className="absolute top-6 right-6 text-slate-400 hover:text-indigo-600 flex items-center text-sm font-medium transition-colors"
              >
                <Download size={16} className="mr-1" /> Export
              </button>
              <div className="prose prose-slate max-w-none">
                {renderMarkdown(compareResult)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnalysisView;
