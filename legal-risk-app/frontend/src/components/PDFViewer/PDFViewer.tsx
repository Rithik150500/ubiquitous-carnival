import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import type { Document, Page } from '../../types';

interface PDFViewerProps {
  document: Document | null;
  highlightedPages: number[];
  onClose: () => void;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({
  document,
  highlightedPages,
  onClose
}) => {
  const [pages, setPages] = useState<Page[]>([]);
  const [selectedPage, setSelectedPage] = useState<number | null>(null);
  const [pageImage, setPageImage] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (document) {
      loadDocument();
    }
  }, [document]);

  useEffect(() => {
    if (selectedPage !== null && document) {
      loadPageImage(document.id, selectedPage);
    }
  }, [selectedPage, document]);

  const loadDocument = async () => {
    if (!document) return;

    try {
      const data = await api.getDocument(document.id);
      setPages(data.pages);
      if (data.pages.length > 0) {
        setSelectedPage(data.pages[0].page_num);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading document:', error);
      setLoading(false);
    }
  };

  const loadPageImage = async (docId: number, pageNum: number) => {
    try {
      const imageUrl = await api.getPageImage(docId, pageNum);
      setPageImage(imageUrl);
    } catch (error) {
      console.error('Error loading page image:', error);
      setPageImage(null);
    }
  };

  if (!document) {
    return null;
  }

  const currentPage = pages.find(p => p.page_num === selectedPage);

  return (
    <div className="pdf-viewer-overlay">
      <div className="overlay-header">
        <span className="overlay-title">📄 {document.filename}</span>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Collapsible Sidebar */}
        <div style={{
          width: sidebarCollapsed ? '0' : '250px',
          borderRight: sidebarCollapsed ? 'none' : '1px solid #e0e0e0',
          overflow: 'hidden',
          transition: 'width 0.3s',
          backgroundColor: '#f9f9f9'
        }}>
          <div style={{ padding: '12px', borderBottom: '1px solid #e0e0e0', fontWeight: 600 }}>
            Page Summaries
          </div>
          <div style={{ overflowY: 'auto', height: 'calc(100% - 48px)' }}>
            {pages.map((page) => (
              <div
                key={page.id}
                className={`file-item ${
                  highlightedPages.includes(page.page_num) ? 'highlighted' : ''
                } ${selectedPage === page.page_num ? 'selected' : ''}`}
                onClick={() => setSelectedPage(page.page_num)}
                style={{ margin: '4px 8px' }}
              >
                <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                  Page {page.page_num}
                </div>
                <div style={{ fontSize: '11px', color: '#666' }}>
                  {page.summdesc || 'No summary'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Toggle Button */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          style={{
            width: '24px',
            border: 'none',
            backgroundColor: '#f0f0f0',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          {sidebarCollapsed ? '→' : '←'}
        </button>

        {/* PDF View */}
        <div style={{ flex: 1, overflow: 'auto', padding: '16px', backgroundColor: '#e0e0e0' }}>
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              Loading document...
            </div>
          ) : (
            <>
              <div style={{
                backgroundColor: 'white',
                padding: '16px',
                marginBottom: '16px',
                borderRadius: '4px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}>
                <h3 style={{ marginBottom: '8px' }}>
                  Page {selectedPage} of {pages.length}
                </h3>
                {currentPage && (
                  <p style={{ fontSize: '14px', color: '#666' }}>
                    {currentPage.summdesc}
                  </p>
                )}
              </div>

              {pageImage ? (
                <div style={{
                  backgroundColor: 'white',
                  padding: '16px',
                  borderRadius: '4px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  marginBottom: '16px'
                }}>
                  <img
                    src={pageImage}
                    alt={`Page ${selectedPage}`}
                    style={{
                      maxWidth: '100%',
                      height: 'auto',
                      display: 'block'
                    }}
                  />
                </div>
              ) : (
                <div className="loading">
                  <div className="spinner"></div>
                  Loading page image...
                </div>
              )}

              {currentPage?.page_text && (
                <div style={{
                  backgroundColor: 'white',
                  padding: '16px',
                  borderRadius: '4px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                  <h4 style={{ marginBottom: '12px' }}>Page Text</h4>
                  <pre style={{
                    whiteSpace: 'pre-wrap',
                    wordWrap: 'break-word',
                    fontSize: '13px',
                    lineHeight: '1.6',
                    fontFamily: 'Georgia, serif',
                    color: '#333'
                  }}>
                    {currentPage.page_text}
                  </pre>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
