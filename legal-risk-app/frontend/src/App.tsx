import React, { useState } from 'react';
import { DocumentList } from './components/DocumentList/DocumentList';
import { TodoPanel } from './components/TodoPanel/TodoPanel';
import { WorkflowPanel } from './components/WorkflowPanel/WorkflowPanel';
import { FileEditor } from './components/FileEditor/FileEditor';
import { PDFViewer } from './components/PDFViewer/PDFViewer';
import type { Document } from './types';
import './styles/App.css';

function App() {
  // Document state
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [highlightedDocuments, setHighlightedDocuments] = useState<number[]>([]);

  // PDF Viewer state
  const [showPDFViewer, setShowPDFViewer] = useState(false);
  const [highlightedPages, setHighlightedPages] = useState<number[]>([]);

  // File Editor state
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [highlightedFile, setHighlightedFile] = useState<string | null>(null);

  const handleDocumentSelect = (doc: Document) => {
    setSelectedDocument(doc);
    setShowPDFViewer(true);
  };

  const handleHighlightDocuments = (docIds: number[]) => {
    setHighlightedDocuments(docIds);
    // Auto-clear highlights after 5 seconds
    setTimeout(() => setHighlightedDocuments([]), 5000);
  };

  const handleHighlightPages = (docId: number, pageNums: number[]) => {
    setHighlightedPages(pageNums);
    // Auto-clear highlights after 5 seconds
    setTimeout(() => setHighlightedPages([]), 5000);
  };

  const handleHighlightFile = (filePath: string) => {
    setHighlightedFile(filePath);
    // Auto-clear highlights after 5 seconds
    setTimeout(() => setHighlightedFile(null), 5000);
  };

  const handleFileSelect = (filePath: string) => {
    setSelectedFile(filePath);
  };

  return (
    <div className="app-container">
      {/* Left Panel - Documents */}
      <DocumentList
        onDocumentSelect={handleDocumentSelect}
        highlightedDocuments={highlightedDocuments}
        selectedDocumentId={selectedDocument?.id || null}
      />

      {/* Center Panel - Todos and Workflow */}
      <div className="center-panel">
        <TodoPanel />
        <WorkflowPanel
          onHighlightDocument={handleHighlightDocuments}
          onHighlightPages={handleHighlightPages}
          onHighlightFile={handleHighlightFile}
        />
      </div>

      {/* Right Panel - Files */}
      <FileEditor
        highlightedFile={highlightedFile}
        selectedFile={selectedFile}
        onFileSelect={handleFileSelect}
        onClose={() => setSelectedFile(null)}
      />

      {/* PDF Viewer Overlay */}
      {showPDFViewer && selectedDocument && (
        <PDFViewer
          document={selectedDocument}
          highlightedPages={highlightedPages}
          onClose={() => {
            setShowPDFViewer(false);
            setHighlightedPages([]);
          }}
        />
      )}
    </div>
  );
}

export default App;
