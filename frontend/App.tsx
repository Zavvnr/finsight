import React, { useState } from 'react';
import { LayoutDashboard, Files, MessageSquare, BarChart3, Search } from 'lucide-react';
import { ViewState, Document } from './types';
import { MOCK_DOCUMENTS } from './mockData';

import Dashboard from './components/Dashboard';
import DocumentManager from './components/DocumentManager';
import ChatInterface from './components/ChatInterface';
import AnalysisView from './components/AnalysisView';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewState>('dashboard');
  const [documents, setDocuments] = useState<Document[]>(MOCK_DOCUMENTS);

  const handleAddDocument = (doc: Document) => {
    setDocuments(prev => [doc, ...prev]);
  };

  const handleRemoveDocument = (id: string) => {
    setDocuments(prev => prev.filter(d => d.id !== id));
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'documents':
        return <DocumentManager documents={documents} onAddDocument={handleAddDocument} onRemoveDocument={handleRemoveDocument} />;
      case 'chat':
        return <ChatInterface documents={documents} />;
      case 'analysis':
        return <AnalysisView documents={documents} />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col flex-shrink-0">
        <div className="p-6 flex items-center space-x-3">
          <div className="bg-indigo-500 p-2 rounded-lg">
            <Search size={24} className="text-white" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight">FinSight</span>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          <button
            onClick={() => setCurrentView('dashboard')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-colors ${currentView === 'dashboard' ? 'bg-indigo-600 text-white' : 'hover:bg-slate-800 hover:text-white'}`}
          >
            <LayoutDashboard size={20} />
            <span className="font-medium">Dashboard</span>
          </button>
          <button
            onClick={() => setCurrentView('documents')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-colors ${currentView === 'documents' ? 'bg-indigo-600 text-white' : 'hover:bg-slate-800 hover:text-white'}`}
          >
            <Files size={20} />
            <span className="font-medium">Documents</span>
            {documents.length > 0 && (
              <span className="ml-auto bg-slate-800 text-xs py-0.5 px-2 rounded-full">{documents.length}</span>
            )}
          </button>
          <button
            onClick={() => setCurrentView('chat')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-colors ${currentView === 'chat' ? 'bg-indigo-600 text-white' : 'hover:bg-slate-800 hover:text-white'}`}
          >
            <MessageSquare size={20} />
            <span className="font-medium">RAG Chat</span>
          </button>
          <button
            onClick={() => setCurrentView('analysis')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-colors ${currentView === 'analysis' ? 'bg-indigo-600 text-white' : 'hover:bg-slate-800 hover:text-white'}`}
          >
            <BarChart3 size={20} />
            <span className="font-medium">Analysis</span>
          </button>
        </nav>

        <div className="p-6 border-t border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sm font-bold text-white">
              FA
            </div>
            <div>
              <p className="text-sm font-medium text-white">Financial Analyst</p>
              <p className="text-xs text-slate-500">Pro Plan</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Topbar (Optional, keeping it clean for now) */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 flex-shrink-0">
          <div className="flex items-center text-sm text-slate-500">
            <span className="capitalize">{currentView}</span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-xs font-medium px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-full flex items-center">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5"></span>
              API Connected
            </span>
          </div>
        </header>

        {/* View Content */}
        <div className="flex-1 overflow-hidden">
          {renderView()}
        </div>
      </main>
    </div>
  );
};

export default App;
