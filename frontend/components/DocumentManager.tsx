import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Trash2, File, CheckCircle } from 'lucide-react';
import { Document } from '../types';

interface DocumentManagerProps {
  documents: Document[];
  onAddDocument: (doc: Document) => void;
  onRemoveDocument: (id: string) => void;
}

const DocumentManager: React.FC<DocumentManagerProps> = ({ documents, onAddDocument, onRemoveDocument }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const simulateUpload = (file: File) => {
    setIsUploading(true);
    // Simulate network delay and text extraction
    setTimeout(() => {
      const newDoc: Document = {
        id: `doc-${Date.now()}`,
        name: file.name,
        uploadDate: new Date().toISOString().split('T')[0],
        size: `${(file.size / (1024 * 1024)).toFixed(2)} MB`,
        content: `Simulated extracted content for ${file.name}. This document contains financial data, revenue figures, and strategic outlook for the upcoming quarters. (In a real app, this would be the parsed text from the PDF).`
      };
      onAddDocument(newDoc);
      setIsUploading(false);
    }, 1500);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      simulateUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      simulateUpload(e.target.files[0]);
    }
  };

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Document Knowledge Base</h1>
        <p className="text-slate-500">Upload financial reports, 10-Ks, and earnings transcripts for AI analysis.</p>
      </div>

      {/* Upload Zone */}
      <div 
        className={`border-2 border-dashed rounded-xl p-10 text-center transition-colors mb-8 ${
          isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 bg-white hover:bg-slate-50'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileInput} 
          className="hidden" 
          accept=".pdf,.txt,.csv"
        />
        
        {isUploading ? (
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
            <p className="text-slate-600 font-medium">Processing document and generating embeddings...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center space-y-4 cursor-pointer" onClick={() => fileInputRef.current?.click()}>
            <div className="p-4 bg-indigo-100 text-indigo-600 rounded-full">
              <UploadCloud size={32} />
            </div>
            <div>
              <p className="text-lg font-medium text-slate-700">Click to upload or drag and drop</p>
              <p className="text-sm text-slate-500 mt-1">PDF, TXT, or CSV (Max 10MB)</p>
            </div>
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
          <h2 className="font-semibold text-slate-800">Indexed Documents ({documents.length})</h2>
        </div>
        <ul className="divide-y divide-slate-200">
          {documents.length === 0 ? (
            <li className="p-8 text-center text-slate-500">No documents uploaded yet.</li>
          ) : (
            documents.map((doc) => (
              <li key={doc.id} className="p-4 hover:bg-slate-50 flex items-center justify-between group transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-rose-100 text-rose-600 rounded-lg">
                    <FileText size={24} />
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">{doc.name}</p>
                    <div className="flex items-center text-xs text-slate-500 mt-1 space-x-3">
                      <span>{doc.size}</span>
                      <span>•</span>
                      <span>Uploaded {doc.uploadDate}</span>
                      <span>•</span>
                      <span className="flex items-center text-emerald-600"><CheckCircle size={12} className="mr-1"/> Indexed</span>
                    </div>
                  </div>
                </div>
                <button 
                  onClick={() => onRemoveDocument(doc.id)}
                  className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-md opacity-0 group-hover:opacity-100 transition-all"
                  title="Remove document"
                >
                  <Trash2 size={18} />
                </button>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
};

export default DocumentManager;
