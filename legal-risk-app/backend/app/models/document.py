from sqlalchemy import Column, Integer, String, Text, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Document(Base):
    """Document model representing a legal document"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, nullable=False)
    summdesc = Column(Text, nullable=True)  # Document summary description

    # Relationship to pages
    pages = relationship("Page", back_populates="document", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "summdesc": self.summdesc,
            "page_count": len(self.pages) if self.pages else 0
        }


class Page(Base):
    """Page model representing a single page in a document"""
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_num = Column(Integer, nullable=False)  # Page number (1-indexed)
    summdesc = Column(Text, nullable=True)  # Page summary description
    page_text = Column(Text, nullable=True)  # Extracted text from page
    page_image_path = Column(String, nullable=True)  # Path to page image

    # Relationship to document
    document = relationship("Document", back_populates="pages")

    def to_dict(self, include_text=False, include_image_path=False):
        result = {
            "id": self.id,
            "document_id": self.document_id,
            "page_num": self.page_num,
            "summdesc": self.summdesc,
        }
        if include_text:
            result["page_text"] = self.page_text
        if include_image_path:
            result["page_image_path"] = self.page_image_path
        return result
