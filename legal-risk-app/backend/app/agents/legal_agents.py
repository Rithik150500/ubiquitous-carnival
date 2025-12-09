"""
Legal Risk Analysis Deep Agents
Implements the three-tier agent architecture:
1. Legal Risk Analysis Agent (main)
2. Analysis SubAgent
3. Create Report SubAgent
"""
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool, tool
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base_agent import BaseDeepAgent, TodoListMiddleware, FilesystemMiddleware
from app.tools.document_tools import create_document_tools
from app.tools.web_tools import create_web_tools
from config.settings import settings
import json


class AnalysisSubAgent(BaseDeepAgent):
    """
    Analysis Deep SubAgent
    - Model: Claude Sonnet 4.5
    - System Prompt: Legal Analysis
    - Middleware: TodoList, Filesystem, SubAgent
    - Tools: Document Analysis + Web Research
    """

    def __init__(self, db_session: AsyncSession):
        self.todo_middleware = TodoListMiddleware()
        self.filesystem_middleware = FilesystemMiddleware()

        # Document analysis tools
        document_tools = create_document_tools(db_session)

        # Web research tools
        web_tools = create_web_tools()

        # Combine all tools
        all_tools = document_tools + web_tools

        system_prompt = """You are a Legal Analysis expert assistant. Your role is to:

1. Analyze company legal documents for potential risks, obligations, and key clauses
2. Research relevant laws, regulations, and case precedents
3. Identify compliance requirements and potential liabilities
4. Compare contract terms against industry standards

You have access to:
- Document analysis tools (list_documents, get_documents, get_page_text, get_page_image)
- Web research tools (internet_search, url_content)

When analyzing documents:
1. Start by listing all available documents
2. Review document summaries to identify which documents to analyze in depth
3. For critical sections, get the full page text
4. Only use get_page_image when you need to see visual elements like tables or signatures
5. Research relevant legal precedents or regulations when needed

Focus on identifying:
- Legal risks and liabilities
- Compliance issues
- Ambiguous or problematic clauses
- Missing protections or rights
- Conflicts with regulations

Be thorough but efficient with tool usage."""

        super().__init__(
            name="Analysis SubAgent",
            system_prompt=system_prompt,
            model=settings.agent_model,
            tools=all_tools,
            max_iterations=30,
        )


class CreateReportSubAgent(BaseDeepAgent):
    """
    Create Report SubAgent
    - System Prompt: Create Legal Risk Analysis Report
    - Middleware: Filesystem
    - Tools: Document Analysis only
    """

    def __init__(self, db_session: AsyncSession):
        self.filesystem_middleware = FilesystemMiddleware()

        # Document analysis tools only
        document_tools = create_document_tools(db_session)

        system_prompt = """You are a Legal Report Generation specialist. Your role is to:

Create comprehensive, well-structured legal risk analysis reports based on the analysis provided.

Report Structure:
1. Executive Summary
   - Overview of analyzed documents
   - Key findings and risk level

2. Risk Assessment
   - High-priority risks
   - Medium-priority risks
   - Low-priority risks

3. Detailed Findings
   - For each document analyzed:
     * Document name and summary
     * Key clauses and terms
     * Identified risks
     * Compliance concerns

4. Recommendations
   - Immediate actions required
   - Medium-term improvements
   - Long-term considerations

5. Appendix
   - Document references
   - Relevant regulations cited

Format the report in Markdown with clear headings, bullet points, and tables where appropriate.
Save the report using the filesystem tools available to you.

You have access to document analysis tools if you need to reference specific details."""

        super().__init__(
            name="Create Report SubAgent",
            system_prompt=system_prompt,
            model=settings.agent_model,
            tools=document_tools,
            max_iterations=15,
        )


class LegalRiskAnalysisAgent(BaseDeepAgent):
    """
    Main Legal Risk Analysis Deep Agent
    - Model: Claude Sonnet 4.5
    - System Prompt: Company Legal Risk Analysis
    - Subagents: Analysis (unlimited), Create Report (use=1)
    - Middleware: TodoList, Filesystem, SubAgent
    """

    def __init__(self, db_session: AsyncSession):
        self.todo_middleware = TodoListMiddleware()
        self.filesystem_middleware = FilesystemMiddleware()
        self.db_session = db_session

        # Create subagents
        self.analysis_subagent = AnalysisSubAgent(db_session)
        self.create_report_subagent = CreateReportSubAgent(db_session)

        # Create tools for delegating to subagents
        @tool
        async def delegate_to_analysis(task: str) -> str:
            """
            Delegate a legal analysis task to the Analysis SubAgent.
            Use this for in-depth document analysis, risk identification, and legal research.
            Input: Task description for the analysis subagent.
            """
            result = await self.analysis_subagent.run(task)
            return result.get("output", "Analysis completed")

        @tool
        async def delegate_to_create_report(analysis_summary: str) -> str:
            """
            Delegate report creation to the Create Report SubAgent.
            Use this ONCE at the end to generate the final risk analysis report.
            Input: Summary of all analysis findings to be compiled into a report.
            """
            result = await self.create_report_subagent.run(
                f"Create a comprehensive legal risk analysis report based on:\n\n{analysis_summary}"
            )
            return result.get("output", "Report created")

        subagent_tools = [delegate_to_analysis, delegate_to_create_report]

        system_prompt = """You are the main Legal Risk Analysis coordinator. Your role is to:

1. Coordinate comprehensive legal risk analysis of company documents
2. Delegate analysis tasks to specialized subagents
3. Synthesize findings into actionable insights
4. Ensure thorough coverage of all legal documents

You have access to two subagents:
- delegate_to_analysis: Use this to perform detailed legal analysis (unlimited use)
- delegate_to_create_report: Use this ONCE at the end to create the final report (use=1)

Workflow:
1. Start by understanding what documents are available
2. Delegate analysis tasks to the Analysis SubAgent:
   - Analyze each document for risks
   - Research relevant legal requirements
   - Identify compliance issues
3. Review and synthesize all findings
4. Create a todo list of critical actions
5. Finally, delegate to Create Report SubAgent to generate the comprehensive report

You will be provided with summaries of all company legal documents to begin."""

        super().__init__(
            name="Legal Risk Analysis Agent",
            system_prompt=system_prompt,
            model=settings.agent_model,
            tools=subagent_tools,
            subagents={
                "analysis": self.analysis_subagent,
                "create_report": self.create_report_subagent,
            },
            max_iterations=40,
        )

    async def analyze_company_documents(self) -> Dict[str, Any]:
        """Main entry point for legal risk analysis"""

        # Get all document summaries
        from sqlalchemy import select
        from app.models.document import Document

        result = await self.db_session.execute(select(Document))
        documents = result.scalars().all()

        if not documents:
            return {
                "status": "error",
                "message": "No documents found in database. Please upload documents first."
            }

        # Format document summaries
        doc_summaries = []
        for doc in documents:
            doc_summaries.append(f"- Document {doc.id}: {doc.filename}\n  Summary: {doc.summdesc}")

        all_summaries = "\n".join(doc_summaries)

        # Start analysis
        initial_message = f"""Company Legal Documents Analysis Request

Available documents:
{all_summaries}

Please perform a comprehensive legal risk analysis of all company legal documents:

1. Analyze each document for:
   - Legal risks and liabilities
   - Compliance requirements
   - Problematic clauses or terms
   - Missing protections

2. Research relevant regulations and legal requirements

3. Create a comprehensive risk analysis report

Begin the analysis process."""

        result = await self.run(initial_message)

        return result
