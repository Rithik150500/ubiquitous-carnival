"""
Main FastAPI application for Legal Risk Analysis
"""
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import uvicorn
import os

from config.settings import settings
from app.database.db import init_db, get_db
from app.models.document import Document, Page
from app.services.document_processor import DocumentProcessor
from app.agents.legal_agents import LegalRiskAnalysisAgent
from app.api.approval_system import (
    approval_system,
    ApprovalResponse,
    ApprovalStatus,
    ApprovalType
)
from sqlalchemy import select

# Initialize FastAPI app
app = FastAPI(
    title="Legal Risk Analysis API",
    description="Deep Agent-powered legal document risk analysis system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
document_processor = DocumentProcessor()
current_agent: LegalRiskAnalysisAgent = None


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    print("Database initialized")
    print(f"Documents path: {settings.documents_path}")
    print(f"Images path: {settings.images_path}")


# ============================================================================
# Document Management Endpoints
# ============================================================================

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a PDF document"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save uploaded file
    file_path = settings.documents_path / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Process document
    try:
        document = await document_processor.process_document(str(file_path), db)
        return {
            "status": "success",
            "document": document.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/api/documents/process-all")
async def process_all_documents(db: AsyncSession = Depends(get_db)):
    """Process all PDF documents in the documents folder"""
    try:
        documents = await document_processor.process_all_documents(db)
        return {
            "status": "success",
            "processed_count": len(documents),
            "documents": [doc.to_dict() for doc in documents]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")


@app.get("/api/documents")
async def list_documents(db: AsyncSession = Depends(get_db)):
    """List all documents"""
    result = await db.execute(select(Document))
    documents = result.scalars().all()
    return {
        "documents": [doc.to_dict() for doc in documents]
    }


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific document with all pages"""
    result = await db.execute(select(Document).where(Document.id == doc_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document": document.to_dict(),
        "pages": [page.to_dict(include_text=True) for page in document.pages]
    }


@app.get("/api/documents/{doc_id}/pages/{page_num}/image")
async def get_page_image(doc_id: int, page_num: int, db: AsyncSession = Depends(get_db)):
    """Get page image"""
    result = await db.execute(
        select(Page).where(Page.document_id == doc_id, Page.page_num == page_num)
    )
    page = result.scalar_one_or_none()

    if not page or not page.page_image_path:
        raise HTTPException(status_code=404, detail="Page image not found")

    if not os.path.exists(page.page_image_path):
        raise HTTPException(status_code=404, detail="Image file not found")

    return FileResponse(page.page_image_path, media_type="image/png")


# ============================================================================
# Agent Endpoints
# ============================================================================

@app.post("/api/agent/start-analysis")
async def start_analysis(db: AsyncSession = Depends(get_db)):
    """Start the legal risk analysis"""
    global current_agent

    try:
        # Create agent
        current_agent = LegalRiskAnalysisAgent(db)

        # Start analysis (this will run in background in production)
        result = await current_agent.analyze_company_documents()

        return {
            "status": "success",
            "message": "Analysis started",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting analysis: {str(e)}")


@app.get("/api/agent/status")
async def get_agent_status():
    """Get current agent status"""
    if not current_agent:
        return {
            "status": "not_started",
            "message": "No analysis in progress"
        }

    return {
        "status": "running",
        "todos": current_agent.todo_middleware.get_todos(),
    }


# ============================================================================
# Human Approval Endpoints
# ============================================================================

@app.get("/api/approvals/pending")
async def get_pending_approvals():
    """Get all pending approval requests"""
    approvals = approval_system.get_pending_approvals()
    return {
        "approvals": [approval.dict() for approval in approvals]
    }


@app.post("/api/approvals/{approval_id}/respond")
async def respond_to_approval(
    approval_id: str,
    response: ApprovalResponse
):
    """Respond to an approval request"""
    request = approval_system.respond_to_approval(
        request_id=approval_id,
        status=response.status,
        modified_data=response.modified_data,
        feedback=response.feedback
    )

    if not request:
        raise HTTPException(status_code=404, detail="Approval request not found")

    return {
        "status": "success",
        "request": request.dict()
    }


@app.get("/api/approvals/history")
async def get_approval_history():
    """Get approval history"""
    history = approval_system.get_approval_history()
    return {
        "history": [approval.dict() for approval in history]
    }


# ============================================================================
# File System Endpoints
# ============================================================================

@app.get("/api/files")
async def list_files():
    """List all files in agent workspace"""
    if not current_agent:
        return {"files": []}

    files = await current_agent.filesystem_middleware.list_files()
    return {"files": files}


@app.get("/api/files/{file_path:path}")
async def get_file(file_path: str):
    """Get file content"""
    if not current_agent:
        raise HTTPException(status_code=400, detail="No agent running")

    content = await current_agent.filesystem_middleware.read_file(file_path)
    return {"content": content}


# ============================================================================
# Health Check
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "anthropic_api_configured": bool(settings.anthropic_api_key)
    }


# ============================================================================
# WebSocket for Real-time Updates
# ============================================================================

@app.websocket("/ws/agent-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time agent updates"""
    await websocket.accept()
    try:
        while True:
            # Send agent status updates
            if current_agent:
                await websocket.send_json({
                    "type": "status",
                    "todos": current_agent.todo_middleware.get_todos(),
                })

            # Check for pending approvals
            pending = approval_system.get_pending_approvals()
            if pending:
                await websocket.send_json({
                    "type": "approval_required",
                    "count": len(pending)
                })

            # Wait before next update
            import asyncio
            await asyncio.sleep(2)

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
