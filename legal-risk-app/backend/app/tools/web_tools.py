from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_community.document_loaders import WebBaseLoader
import os

class InternetSearchInput(BaseModel):
    """Input for internet search tool"""
    query: str = Field(description="Search query")


class InternetSearchTool(BaseTool):
    """Tool for searching the internet"""
    name: str = "internet_search"
    description: str = """Search the internet for information related to legal topics, regulations, case law, etc.
    Input: Search query string
    Returns: Search results with titles, snippets, and URLs"""
    args_schema: type[BaseModel] = InternetSearchInput

    async def _arun(self, query: str) -> str:
        """Search the internet"""
        try:
            # Note: This requires GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables
            # For now, we'll return a mock response
            return f"""Search results for: {query}

Note: To enable real internet search, set up Google Custom Search API:
1. Get a Google API key from https://console.cloud.google.com/
2. Create a Custom Search Engine at https://cse.google.com/
3. Set GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables

For testing purposes, consider searching manually or using alternative search tools."""
        except Exception as e:
            return f"Error performing search: {str(e)}"

    def _run(self, query: str) -> str:
        raise NotImplementedError("Use async version")


class URLContentInput(BaseModel):
    """Input for URL content fetching tool"""
    url: str = Field(description="URL to fetch content from")


class URLContentTool(BaseTool):
    """Tool for fetching content from URLs (LIMITED USE)"""
    name: str = "url_content"
    description: str = """Fetch and read content from a specific URL. USE SPARINGLY - this is resource intensive.
    Only use when you need to read the full content of a specific webpage for detailed analysis.
    Input: URL string
    Returns: Extracted text content from the webpage"""
    args_schema: type[BaseModel] = URLContentInput

    async def _arun(self, url: str) -> str:
        """Fetch URL content"""
        try:
            loader = WebBaseLoader([url])
            documents = loader.load()

            if not documents:
                return f"No content found at URL: {url}"

            # Extract text from documents
            content = "\n\n".join([doc.page_content for doc in documents])

            # Limit content length to avoid token limits
            max_length = 10000
            if len(content) > max_length:
                content = content[:max_length] + "\n\n[Content truncated...]"

            return content
        except Exception as e:
            return f"Error fetching URL content: {str(e)}"

    def _run(self, url: str) -> str:
        raise NotImplementedError("Use async version")


def create_web_tools() -> list[BaseTool]:
    """Create all web research tools"""
    return [
        InternetSearchTool(),
        URLContentTool(),
    ]
