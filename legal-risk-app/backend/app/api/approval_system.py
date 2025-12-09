"""
Human-in-the-loop approval system
Based on Deep Agents documentation: Human-in-the-loop configuration
"""
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
import uuid


class ApprovalType(str, Enum):
    """Types of actions requiring approval"""
    TODO = "todos"
    SUBAGENT_TASK = "subagent_task"
    GET_DOCUMENTS = "get_documents"
    GET_PAGE_TEXT = "get_page_text"
    GET_PAGE_IMAGE = "get_page_image"
    WRITE_FILE = "write_file"
    EDIT_FILE = "edit_file"
    INTERNET_SEARCH = "internet_search"
    URL_CONTENT = "url_content"


class ApprovalStatus(str, Enum):
    """Status of approval requests"""
    PENDING = "pending"
    APPROVED = "approved"
    EDITED = "edited"
    REJECTED = "rejected"


class ApprovalRequest(BaseModel):
    """Approval request model"""
    id: str
    type: ApprovalType
    timestamp: datetime
    status: ApprovalStatus
    data: Dict[str, Any]
    agent_name: str
    description: str
    highlights: Optional[Dict[str, Any]] = None


class ApprovalResponse(BaseModel):
    """Response to approval request"""
    id: str
    status: ApprovalStatus
    modified_data: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None


class HumanApprovalSystem:
    """
    Human-in-the-loop approval system
    Manages approval requests for agent actions
    """

    def __init__(self):
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.approval_history: List[ApprovalRequest] = []

    def create_approval_request(
        self,
        approval_type: ApprovalType,
        data: Dict[str, Any],
        agent_name: str,
        description: str,
        highlights: Optional[Dict[str, Any]] = None
    ) -> ApprovalRequest:
        """Create a new approval request"""

        request = ApprovalRequest(
            id=str(uuid.uuid4()),
            type=approval_type,
            timestamp=datetime.now(),
            status=ApprovalStatus.PENDING,
            data=data,
            agent_name=agent_name,
            description=description,
            highlights=highlights
        )

        self.pending_approvals[request.id] = request
        return request

    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get all pending approval requests"""
        return list(self.pending_approvals.values())

    def get_approval_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a specific approval request"""
        return self.pending_approvals.get(request_id)

    def respond_to_approval(
        self,
        request_id: str,
        status: ApprovalStatus,
        modified_data: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None
    ) -> Optional[ApprovalRequest]:
        """Respond to an approval request"""

        request = self.pending_approvals.get(request_id)
        if not request:
            return None

        # Update request status
        request.status = status

        # If edited, update data
        if status == ApprovalStatus.EDITED and modified_data:
            request.data = modified_data

        # Move to history
        self.approval_history.append(request)
        del self.pending_approvals[request_id]

        return request

    def clear_pending_approvals(self):
        """Clear all pending approvals"""
        self.approval_history.extend(self.pending_approvals.values())
        self.pending_approvals.clear()

    def get_approval_history(self, limit: int = 50) -> List[ApprovalRequest]:
        """Get approval history"""
        return self.approval_history[-limit:]


# Global approval system instance
approval_system = HumanApprovalSystem()


def create_todo_approval(todos: List[Dict[str, str]], agent_name: str) -> ApprovalRequest:
    """Create approval for todo list updates"""
    return approval_system.create_approval_request(
        approval_type=ApprovalType.TODO,
        data={"todos": todos},
        agent_name=agent_name,
        description=f"{agent_name} wants to update the todo list"
    )


def create_subagent_approval(
    subagent_name: str,
    task: str,
    parent_agent: str
) -> ApprovalRequest:
    """Create approval for subagent task delegation"""
    return approval_system.create_approval_request(
        approval_type=ApprovalType.SUBAGENT_TASK,
        data={"subagent": subagent_name, "task": task},
        agent_name=parent_agent,
        description=f"{parent_agent} wants to delegate task to {subagent_name}"
    )


def create_document_tool_approval(
    tool_type: ApprovalType,
    tool_params: Dict[str, Any],
    agent_name: str,
    highlights: Optional[Dict[str, Any]] = None
) -> ApprovalRequest:
    """Create approval for document tool usage"""

    descriptions = {
        ApprovalType.GET_DOCUMENTS: "wants to retrieve document details",
        ApprovalType.GET_PAGE_TEXT: "wants to read page text",
        ApprovalType.GET_PAGE_IMAGE: "wants to view page images",
    }

    return approval_system.create_approval_request(
        approval_type=tool_type,
        data=tool_params,
        agent_name=agent_name,
        description=f"{agent_name} {descriptions.get(tool_type, 'wants to use document tool')}",
        highlights=highlights
    )


def create_file_operation_approval(
    operation: ApprovalType,
    file_path: str,
    content: Optional[str],
    agent_name: str
) -> ApprovalRequest:
    """Create approval for file operations"""

    descriptions = {
        ApprovalType.WRITE_FILE: f"wants to write file: {file_path}",
        ApprovalType.EDIT_FILE: f"wants to edit file: {file_path}",
    }

    return approval_system.create_approval_request(
        approval_type=operation,
        data={"file_path": file_path, "content": content},
        agent_name=agent_name,
        description=f"{agent_name} {descriptions.get(operation, 'wants to perform file operation')}",
        highlights={"file": file_path}
    )


def create_web_tool_approval(
    tool_type: ApprovalType,
    query_or_url: str,
    agent_name: str
) -> ApprovalRequest:
    """Create approval for web research tools"""

    descriptions = {
        ApprovalType.INTERNET_SEARCH: f"wants to search: {query_or_url}",
        ApprovalType.URL_CONTENT: f"wants to fetch content from: {query_or_url}",
    }

    return approval_system.create_approval_request(
        approval_type=tool_type,
        data={"query" if tool_type == ApprovalType.INTERNET_SEARCH else "url": query_or_url},
        agent_name=agent_name,
        description=f"{agent_name} {descriptions.get(tool_type, 'wants to use web tool')}"
    )
