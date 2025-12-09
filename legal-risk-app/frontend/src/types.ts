/**
 * Type definitions for Legal Risk Analysis application
 */

export interface Document {
  id: number;
  filename: string;
  summdesc: string;
  page_count: number;
}

export interface Page {
  id: number;
  document_id: number;
  page_num: number;
  summdesc: string;
  page_text?: string;
  page_image_path?: string;
}

export interface Todo {
  task: string;
  status: 'pending' | 'in_progress' | 'completed';
}

export enum ApprovalType {
  TODO = 'todos',
  SUBAGENT_TASK = 'subagent_task',
  GET_DOCUMENTS = 'get_documents',
  GET_PAGE_TEXT = 'get_page_text',
  GET_PAGE_IMAGE = 'get_page_image',
  WRITE_FILE = 'write_file',
  EDIT_FILE = 'edit_file',
  INTERNET_SEARCH = 'internet_search',
  URL_CONTENT = 'url_content',
}

export enum ApprovalStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  EDITED = 'edited',
  REJECTED = 'rejected',
}

export interface ApprovalRequest {
  id: string;
  type: ApprovalType;
  timestamp: string;
  status: ApprovalStatus;
  data: Record<string, any>;
  agent_name: string;
  description: string;
  highlights?: Record<string, any>;
}

export interface ApprovalResponse {
  id: string;
  status: ApprovalStatus;
  modified_data?: Record<string, any>;
  feedback?: string;
}

export interface AgentFile {
  path: string;
  content: string;
}
