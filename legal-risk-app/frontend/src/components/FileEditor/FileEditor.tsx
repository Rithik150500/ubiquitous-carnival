import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

interface FileEditorProps {
  highlightedFile: string | null;
  selectedFile: string | null;
  onFileSelect: (filePath: string) => void;
  onClose?: () => void;
}

export const FileEditor: React.FC<FileEditorProps> = ({
  highlightedFile,
  selectedFile,
  onFileSelect,
  onClose
}) => {
  const [files, setFiles] = useState<string[]>([]);
  const [fileContent, setFileContent] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFiles();
    const interval = setInterval(loadFiles, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedFile) {
      loadFileContent(selectedFile);
    }
  }, [selectedFile]);

  const loadFiles = async () => {
    try {
      const fileList = await api.getFiles();
      setFiles(fileList);
      setLoading(false);
    } catch (error) {
      console.error('Error loading files:', error);
      setLoading(false);
    }
  };

  const loadFileContent = async (filePath: string) => {
    try {
      const content = await api.getFileContent(filePath);
      setFileContent(content);
    } catch (error) {
      console.error('Error loading file content:', error);
      setFileContent('Error loading file content');
    }
  };

  if (selectedFile) {
    return (
      <div className="file-editor-overlay">
        <div className="overlay-header">
          <span className="overlay-title">📝 {selectedFile}</span>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="overlay-content">
          <pre style={{
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            fontFamily: 'monospace',
            fontSize: '13px',
            lineHeight: '1.5'
          }}>
            {fileContent}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="right-panel">
      <div className="panel-header">Generated Files</div>
      <div className="panel-content">
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            Loading...
          </div>
        ) : files.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📁</div>
            <div className="empty-state-text">No files generated yet</div>
          </div>
        ) : (
          files.map((file) => (
            <div
              key={file}
              className={`file-item ${
                highlightedFile === file ? 'highlighted' : ''
              } ${selectedFile === file ? 'selected' : ''}`}
              onClick={() => onFileSelect(file)}
            >
              📄 {file}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
