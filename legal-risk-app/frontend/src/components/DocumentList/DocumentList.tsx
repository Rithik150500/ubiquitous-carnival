import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import type { Document } from '../../types';

interface DocumentListProps {
  onDocumentSelect: (doc: Document) => void;
  highlightedDocuments: number[];
  selectedDocumentId: number | null;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  onDocumentSelect,
  highlightedDocuments,
  selectedDocumentId
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const newDoc = await api.uploadDocument(file);
      setDocuments([...documents, newDoc]);
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Error uploading document');
    } finally {
      setUploading(false);
    }
  };

  const handleProcessAll = async () => {
    setLoading(true);
    try {
      await api.processAllDocuments();
      await loadDocuments();
    } catch (error) {
      console.error('Error processing documents:', error);
      alert('Error processing documents');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="left-panel">
        <div className="panel-header">Company Legal Documents</div>
        <div className="loading">
          <div className="spinner"></div>
          Loading...
        </div>
      </div>
    );
  }

  return (
    <div className="left-panel">
      <div className="panel-header">Company Legal Documents</div>
      <div className="panel-content">
        <div className="upload-area" onClick={() => document.getElementById('file-upload')?.click()}>
          <input
            id="file-upload"
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={uploading}
          />
          {uploading ? '⏳ Uploading...' : '📁 Upload PDF Document'}
        </div>

        {documents.length > 0 && (
          <button
            className="btn btn-primary"
            onClick={handleProcessAll}
            style={{ width: '100%', marginBottom: '12px' }}
          >
            🔄 Process All Documents
          </button>
        )}

        {documents.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📄</div>
            <div className="empty-state-text">No documents yet. Upload a PDF to get started.</div>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.id}
              className={`document-item ${
                highlightedDocuments.includes(doc.id) ? 'highlighted' : ''
              } ${selectedDocumentId === doc.id ? 'selected' : ''}`}
              onClick={() => onDocumentSelect(doc)}
            >
              <div className="document-name">📄 {doc.filename}</div>
              <div className="document-summary">{doc.summdesc || 'Processing...'}</div>
              <div className="document-meta">{doc.page_count} pages</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
