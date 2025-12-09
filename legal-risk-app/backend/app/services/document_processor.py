import os
import base64
from pathlib import Path
from typing import List, Dict, Tuple
import fitz  # PyMuPDF
from PIL import Image
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from config.settings import settings
from app.models.document import Document, Page
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class DocumentProcessor:
    """Service for processing legal documents"""

    def __init__(self):
        self.documents_path = settings.documents_path
        self.images_path = settings.images_path
        # Claude Haiku for summarization
        self.haiku = ChatAnthropic(
            model=settings.summary_model,
            anthropic_api_key=settings.anthropic_api_key
        )

    async def process_document(self, pdf_path: str, db: AsyncSession) -> Document:
        """
        Process a PDF document:
        1. Extract each page as image
        2. Extract text from each page
        3. Summarize each page using Claude Haiku
        4. Combine page summaries and create document summary
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Check if document already exists
        result = await db.execute(
            select(Document).where(Document.filename == pdf_file.name)
        )
        existing_doc = result.scalar_one_or_none()
        if existing_doc:
            return existing_doc

        # Create document record
        document = Document(filename=pdf_file.name)
        db.add(document)
        await db.flush()  # Get document ID

        # Open PDF
        pdf_document = fitz.open(pdf_path)
        page_summaries = []

        # Process each page
        for page_num in range(len(pdf_document)):
            print(f"Processing page {page_num + 1}/{len(pdf_document)} of {pdf_file.name}")

            # Extract page
            page = pdf_document[page_num]

            # Extract text
            page_text = page.get_text()

            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x resolution
            image_filename = f"{document.id}_page_{page_num + 1}.png"
            image_path = self.images_path / image_filename
            pix.save(str(image_path))

            # Summarize page using Claude Haiku
            page_summary = await self._summarize_page(page_text, str(image_path))

            # Create page record
            page_record = Page(
                document_id=document.id,
                page_num=page_num + 1,
                summdesc=page_summary,
                page_text=page_text,
                page_image_path=str(image_path)
            )
            db.add(page_record)
            page_summaries.append(f"Page {page_num + 1}: {page_summary}")

        pdf_document.close()

        # Combine all page summaries and create document summary
        combined_summaries = "\n".join(page_summaries)
        document_summary = await self._summarize_document(combined_summaries)
        document.summdesc = document_summary

        await db.commit()
        await db.refresh(document)

        return document

    async def _summarize_page(self, page_text: str, image_path: str) -> str:
        """
        Summarize a single page using Claude Haiku.
        Sends both the page image and text to get a one-line description.
        """
        # Read and encode image
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode("utf-8")

        # Create message with both image and text
        message = HumanMessage(
            content=[
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": f"""Analyze this legal document page and provide a ONE-LINE summary (max 150 characters) that describes what this page contains.

Page text:
{page_text[:2000]}  # Limit text to avoid token limits

Provide only the summary, no preamble."""
                }
            ]
        )

        response = await self.haiku.ainvoke([message])
        return response.content.strip()

    async def _summarize_document(self, combined_page_summaries: str) -> str:
        """
        Summarize the entire document using Claude Haiku.
        Takes combined page summaries and creates a one-sentence document summary.
        """
        message = HumanMessage(
            content=f"""Given the following page-by-page summaries of a legal document, provide a ONE-SENTENCE summary (max 200 characters) of the entire document.

Page summaries:
{combined_page_summaries}

Provide only the document summary, no preamble."""
        )

        response = await self.haiku.ainvoke([message])
        return response.content.strip()

    async def process_all_documents(self, db: AsyncSession) -> List[Document]:
        """Process all PDF documents in the documents folder"""
        documents = []
        pdf_files = list(self.documents_path.glob("*.pdf"))

        for pdf_file in pdf_files:
            try:
                document = await self.process_document(str(pdf_file), db)
                documents.append(document)
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")

        return documents

    async def get_page_image_as_base64(self, image_path: str) -> str:
        """Get page image as base64 encoded string"""
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode("utf-8")
        return image_data
