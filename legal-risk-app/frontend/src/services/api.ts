/**
 * API service for communicating with backend
 */
import axios from 'axios';
import type { Document, Page, Todo, ApprovalRequest, ApprovalResponse } from '../types';

const API_BASE = '/api';

export const api = {
  // Document endpoints
  async getDocuments(): Promise<Document[]> {
    const response = await axios.get(`${API_BASE}/documents`);
    return response.data.documents;
  },

  async getDocument(docId: number): Promise<{ document: Document; pages: Page[] }> {
    const response = await axios.get(`${API_BASE}/documents/${docId}`);
    return response.data;
  },

  async getPageImage(docId: number, pageNum: number): Promise<string> {
    const response = await axios.get(`${API_BASE}/documents/${docId}/pages/${pageNum}/image`, {
      responseType: 'blob'
    });
    return URL.createObjectURL(response.data);
  },

  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(`${API_BASE}/documents/upload`, formData);
    return response.data.document;
  },

  async processAllDocuments(): Promise<Document[]> {
    const response = await axios.post(`${API_BASE}/documents/process-all`);
    return response.data.documents;
  },

  // Agent endpoints
  async startAnalysis(): Promise<any> {
    const response = await axios.post(`${API_BASE}/agent/start-analysis`);
    return response.data;
  },

  async getAgentStatus(): Promise<{ status: string; todos: Todo[] }> {
    const response = await axios.get(`${API_BASE}/agent/status`);
    return response.data;
  },

  // Approval endpoints
  async getPendingApprovals(): Promise<ApprovalRequest[]> {
    const response = await axios.get(`${API_BASE}/approvals/pending`);
    return response.data.approvals;
  },

  async respondToApproval(approvalId: string, approvalResponse: ApprovalResponse): Promise<void> {
    await axios.post(`${API_BASE}/approvals/${approvalId}/respond`, approvalResponse);
  },

  async getApprovalHistory(): Promise<ApprovalRequest[]> {
    const response = await axios.get(`${API_BASE}/approvals/history`);
    return response.data.history;
  },

  // File endpoints
  async getFiles(): Promise<string[]> {
    const response = await axios.get(`${API_BASE}/files`);
    return response.data.files;
  },

  async getFileContent(filePath: string): Promise<string> {
    const response = await axios.get(`${API_BASE}/files/${filePath}`);
    return response.data.content;
  },

  // Health check
  async healthCheck(): Promise<any> {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  },
};
