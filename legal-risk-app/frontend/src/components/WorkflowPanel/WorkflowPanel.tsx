import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import type { ApprovalRequest, ApprovalStatus } from '../../types';

interface WorkflowPanelProps {
  onHighlightDocument: (docIds: number[]) => void;
  onHighlightPages: (docId: number, pageNums: number[]) => void;
  onHighlightFile: (filePath: string) => void;
}

export const WorkflowPanel: React.FC<WorkflowPanelProps> = ({
  onHighlightDocument,
  onHighlightPages,
  onHighlightFile
}) => {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadApprovals();
    const interval = setInterval(loadApprovals, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, []);

  const loadApprovals = async () => {
    try {
      const pending = await api.getPendingApprovals();
      setApprovals(pending);
      setLoading(false);
    } catch (error) {
      console.error('Error loading approvals:', error);
      setLoading(false);
    }
  };

  const handleApproval = async (
    approvalId: string,
    status: ApprovalStatus,
    modifiedData?: Record<string, any>
  ) => {
    try {
      await api.respondToApproval(approvalId, {
        id: approvalId,
        status,
        modified_data: modifiedData,
      });
      await loadApprovals();
    } catch (error) {
      console.error('Error responding to approval:', error);
      alert('Error responding to approval');
    }
  };

  const handleApprovalClick = (approval: ApprovalRequest) => {
    // Trigger highlights based on approval type
    if (approval.type === 'get_documents' && approval.data.doc_ids) {
      onHighlightDocument(approval.data.doc_ids);
    } else if (
      (approval.type === 'get_page_text' || approval.type === 'get_page_image') &&
      approval.data.doc_id &&
      approval.data.page_nums
    ) {
      onHighlightDocument([approval.data.doc_id]);
      onHighlightPages(approval.data.doc_id, approval.data.page_nums);
    } else if (
      (approval.type === 'write_file' || approval.type === 'edit_file') &&
      approval.data.file_path
    ) {
      onHighlightFile(approval.data.file_path);
    }
  };

  const renderApprovalData = (approval: ApprovalRequest) => {
    const data = approval.data;
    switch (approval.type) {
      case 'get_documents':
        return `Document IDs: ${data.doc_ids?.join(', ')}`;
      case 'get_page_text':
      case 'get_page_image':
        return `Document ID: ${data.doc_id}, Pages: ${data.page_nums?.join(', ')}`;
      case 'write_file':
      case 'edit_file':
        return `File: ${data.file_path}`;
      case 'internet_search':
        return `Query: ${data.query}`;
      case 'url_content':
        return `URL: ${data.url}`;
      case 'subagent_task':
        return `Subagent: ${data.subagent}, Task: ${data.task}`;
      default:
        return JSON.stringify(data, null, 2);
    }
  };

  return (
    <div className="workflow-section">
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Agent Workflow & Approvals</h3>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          Loading...
        </div>
      ) : approvals.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">✓</div>
          <div className="empty-state-text">
            No pending approvals. The agent is working autonomously.
          </div>
        </div>
      ) : (
        approvals.map((approval) => (
          <div
            key={approval.id}
            className="approval-card"
            onClick={() => handleApprovalClick(approval)}
          >
            <div className="approval-header">
              <span className="approval-type">{approval.type.replace(/_/g, ' ').toUpperCase()}</span>
              <span className="approval-timestamp">
                {new Date(approval.timestamp).toLocaleTimeString()}
              </span>
            </div>

            <div className="approval-description">
              <strong>{approval.agent_name}</strong> {approval.description}
            </div>

            <div className="approval-data">{renderApprovalData(approval)}</div>

            <div className="approval-actions">
              <button
                className="btn btn-approve"
                onClick={(e) => {
                  e.stopPropagation();
                  handleApproval(approval.id, 'approved' as ApprovalStatus);
                }}
              >
                ✓ Approve
              </button>
              <button
                className="btn btn-reject"
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm('Are you sure you want to reject this action?')) {
                    handleApproval(approval.id, 'rejected' as ApprovalStatus);
                  }
                }}
              >
                ✗ Reject
              </button>
              <button
                className="btn btn-edit"
                onClick={(e) => {
                  e.stopPropagation();
                  alert('Edit functionality would allow modifying the approval data before approving');
                }}
              >
                ✎ Edit
              </button>
            </div>
          </div>
        ))
      )}

      <div style={{ marginTop: '24px' }}>
        <button
          className="btn btn-primary"
          onClick={async () => {
            if (confirm('Start the legal risk analysis?')) {
              try {
                await api.startAnalysis();
                alert('Analysis started! Monitor progress above.');
              } catch (error) {
                console.error('Error starting analysis:', error);
                alert('Error starting analysis');
              }
            }
          }}
          style={{ width: '100%' }}
        >
          🚀 Start Legal Risk Analysis
        </button>
      </div>
    </div>
  );
};
