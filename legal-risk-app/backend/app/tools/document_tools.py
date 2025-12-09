from typing import List, Dict, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document, Page
from app.services.document_processor import DocumentProcessor
import json

class DocumentDatabase:
    """Shared database connection for tools"""
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.processor = DocumentProcessor()


class ListDocumentsInput(BaseModel):
    """Input for list documents tool"""
    pass


class ListDocumentsTool(BaseTool):
    """Tool to list all documents with their summaries"""
    name: str = "list_documents"
    description: str = """Lists all company legal documents with their ID, summary, and page count.
    Use this to get an overview of all available documents."""
    args_schema: type[BaseModel] = ListDocumentsInput
    db: DocumentDatabase = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self) -> str:
        """List all documents"""
        result = await self.db.db.execute(select(Document))
        documents = result.scalars().all()

        if not documents:
            return "No documents found in the database."

        doc_list = []
        for doc in documents:
            doc_list.append({
                "doc_id": doc.id,
                "filename": doc.filename,
                "summdesc": doc.summdesc,
                "page_count": len(doc.pages)
            })

        return json.dumps(doc_list, indent=2)

    def _run(self) -> str:
        raise NotImplementedError("Use async version")


class GetDocumentsInput(BaseModel):
    """Input for get documents tool"""
    doc_ids: List[int] = Field(description="List of document IDs to retrieve")


class GetDocumentsTool(BaseTool):
    """Tool to get detailed information about specific documents"""
    name: str = "get_documents"
    description: str = """Get detailed information about specific documents including all page summaries.
    Input: List of document IDs
    Returns: Combined summaries of all pages for each document."""
    args_schema: type[BaseModel] = GetDocumentsInput
    db: DocumentDatabase = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, doc_ids: List[int]) -> str:
        """Get documents with all page summaries"""
        result = await self.db.db.execute(
            select(Document).where(Document.id.in_(doc_ids))
        )
        documents = result.scalars().all()

        if not documents:
            return "No documents found with the provided IDs."

        doc_details = []
        for doc in documents:
            pages_info = []
            for page in sorted(doc.pages, key=lambda p: p.page_num):
                pages_info.append({
                    "page_num": page.page_num,
                    "summdesc": page.summdesc
                })

            doc_details.append({
                "doc_id": doc.id,
                "filename": doc.filename,
                "document_summary": doc.summdesc,
                "pages": pages_info
            })

        return json.dumps(doc_details, indent=2)

    def _run(self, doc_ids: List[int]) -> str:
        raise NotImplementedError("Use async version")


class GetPageTextInput(BaseModel):
    """Input for get page text tool"""
    doc_id: int = Field(description="Document ID")
    page_nums: List[int] = Field(description="List of page numbers to retrieve (1-indexed)")


class GetPageTextTool(BaseTool):
    """Tool to get text content of specific pages"""
    name: str = "get_page_text"
    description: str = """Get the full text content of specific pages from a document.
    Input: Document ID and list of page numbers (1-indexed)
    Returns: Page text for each requested page."""
    args_schema: type[BaseModel] = GetPageTextInput
    db: DocumentDatabase = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, doc_id: int, page_nums: List[int]) -> str:
        """Get page text for specific pages"""
        result = await self.db.db.execute(
            select(Page).where(
                Page.document_id == doc_id,
                Page.page_num.in_(page_nums)
            )
        )
        pages = result.scalars().all()

        if not pages:
            return f"No pages found for document {doc_id} with the provided page numbers."

        pages_text = []
        for page in sorted(pages, key=lambda p: p.page_num):
            pages_text.append({
                "page_num": page.page_num,
                "summdesc": page.summdesc,
                "page_text": page.page_text
            })

        return json.dumps(pages_text, indent=2)

    def _run(self, doc_id: int, page_nums: List[int]) -> str:
        raise NotImplementedError("Use async version")


class GetPageImageInput(BaseModel):
    """Input for get page image tool"""
    doc_id: int = Field(description="Document ID")
    page_nums: List[int] = Field(description="List of page numbers to retrieve images for (1-indexed)")


class GetPageImageTool(BaseTool):
    """Tool to get images of specific pages (LIMITED USE)"""
    name: str = "get_page_image"
    description: str = """Get images of specific pages from a document. USE SPARINGLY - this is resource intensive.
    Only use when you need to visually inspect the document layout, tables, or diagrams.
    Input: Document ID and list of page numbers (1-indexed)
    Returns: Base64 encoded images for each requested page."""
    args_schema: type[BaseModel] = GetPageImageInput
    db: DocumentDatabase = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    async def _arun(self, doc_id: int, page_nums: List[int]) -> str:
        """Get page images for specific pages"""
        result = await self.db.db.execute(
            select(Page).where(
                Page.document_id == doc_id,
                Page.page_num.in_(page_nums)
            )
        )
        pages = result.scalars().all()

        if not pages:
            return f"No pages found for document {doc_id} with the provided page numbers."

        pages_images = []
        for page in sorted(pages, key=lambda p: p.page_num):
            # Get image as base64
            image_data = await self.db.processor.get_page_image_as_base64(page.page_image_path)

            pages_images.append({
                "page_num": page.page_num,
                "summdesc": page.summdesc,
                "image_base64": image_data
            })

        return json.dumps(pages_images, indent=2)

    def _run(self, doc_id: int, page_nums: List[int]) -> str:
        raise NotImplementedError("Use async version")


def create_document_tools(db_session: AsyncSession) -> List[BaseTool]:
    """Create all document analysis tools with shared database connection"""
    db = DocumentDatabase(db_session)

    return [
        ListDocumentsTool(db=db),
        GetDocumentsTool(db=db),
        GetPageTextTool(db=db),
        GetPageImageTool(db=db),
    ]
