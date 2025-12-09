# Legal Risk Analysis Web Application

A comprehensive Deep Agent-powered system for analyzing legal documents and identifying risks using Claude Sonnet 4.5 and Claude Haiku.

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Web Interface (React)                        │
├──────────────┬────────────────────────┬────────────────────────┤
│  Documents   │  Agent Workflow        │  Generated Files       │
│  List (20%)  │  & Approvals (60%)     │  (20%)                 │
│              │  ┌──────────────────┐  │                        │
│              │  │ Todo Panel (25%) │  │                        │
│              │  └──────────────────┘  │                        │
│              │  ┌──────────────────┐  │                        │
│              │  │ Workflow (75%)   │  │                        │
│              │  └──────────────────┘  │                        │
└──────────────┴────────────────────────┴────────────────────────┘
         │                     │                      │
         └─────────────────────┼──────────────────────┘
                               │
                          FastAPI Backend
                               │
         ┌─────────────────────┼──────────────────────┐
         │                     │                       │
    Document              Deep Agents           Human Approval
    Processor                                     System
         │                     │                       │
    ┌────┴────┐          ┌────┴────┐           ┌─────┴─────┐
    │ PDF →   │          │ Legal   │           │ Approvals │
    │ Images  │          │ Risk    │           │ Queue     │
    │ + Text  │          │ Agent   │           │           │
    │ + Page  │          │    ↓    │           └───────────┘
    │ Summaries│         │ Analysis│
    │ (Haiku) │          │ SubAgent│
    └─────────┘          │    ↓    │
                         │ Create  │
                         │ Report  │
                         │ SubAgent│
                         └─────────┘
```

### Deep Agent Architecture

1. **Legal Risk Analysis Agent** (Main)
   - Model: Claude Sonnet 4.5
   - Role: Coordinates the entire analysis workflow
   - Subagents: Analysis (unlimited), Create Report (use=1)
   - Middleware: TodoList, Filesystem, SubAgent

2. **Analysis SubAgent**
   - Model: Claude Sonnet 4.5
   - Role: Deep document analysis and legal research
   - Tools: Document analysis + Web research
   - Middleware: TodoList, Filesystem, SubAgent

3. **Create Report SubAgent**
   - Model: Claude Sonnet 4.5
   - Role: Generate comprehensive risk analysis reports
   - Tools: Document analysis only
   - Middleware: Filesystem

## 📋 Features

### Document Processing Pipeline
- **PDF Upload**: Upload legal documents via web interface
- **Page Extraction**: Extract each page as high-resolution images
- **Text Extraction**: Extract full text content from each page
- **Page Summarization**: Claude Haiku generates one-line summaries for each page
- **Document Summarization**: Claude Haiku creates overall document summary

### Database Schema
```sql
documents
  - id (primary key)
  - filename
  - summdesc (document summary)

pages
  - id (primary key)
  - document_id (foreign key)
  - page_num (1-indexed)
  - summdesc (page summary)
  - page_text (extracted text)
  - page_image_path (path to image)
```

### Document Analysis Tools
- **list_documents**: List all documents with summaries
- **get_documents**: Get detailed document information with all page summaries
- **get_page_text**: Get full text for specific pages
- **get_page_image**: Get images for specific pages (limited use)

### Web Research Tools
- **internet_search**: Search for legal information online
- **url_content**: Fetch and analyze content from URLs (limited use)

### Human-in-the-Loop Approval System
- **Approval Types**:
  - Todo list updates
  - Subagent task delegation
  - Document retrieval
  - Page text/image access
  - File operations
  - Web research

- **Actions**: Approve, Edit, Reject
- **Highlighting**: Visual highlights for affected documents, pages, and files

### Web Interface Features
- **Responsive Layout**:
  - Left 20%: Document list
  - Center 60%: Todo panel (25%) + Workflow (75%)
  - Right 20%: Generated files

- **PDF Viewer** (40% overlay):
  - Collapsible sidebar with page summaries
  - Page navigation
  - Image and text view

- **File Editor** (40% overlay):
  - View generated reports and files
  - Syntax highlighting for code

- **Real-time Updates**: WebSocket connection for live status updates

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Anthropic API key

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd legal-risk-app/backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

5. **Run the backend**:
   ```bash
   python -m app.main
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd legal-risk-app/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

   The web interface will be available at `http://localhost:3000`

## 📖 Usage

### 1. Upload Documents
- Click "Upload PDF Document" in the left panel
- Select one or more PDF files
- Click "Process All Documents" to extract and summarize

### 2. Start Analysis
- Once documents are processed, click "Start Legal Risk Analysis"
- The main agent will begin coordinating the analysis

### 3. Monitor Progress
- Watch the Todo Panel for task progress
- View agent workflow in the center panel

### 4. Human Approvals
- Approval requests appear in the workflow panel
- Click on an approval to see highlights in documents/pages/files
- Choose: Approve, Edit, or Reject

### 5. View Results
- Click documents to open PDF viewer
- Click files to view generated reports
- Review the comprehensive risk analysis report

## 🔧 API Endpoints

### Documents
- `POST /api/documents/upload` - Upload a PDF document
- `POST /api/documents/process-all` - Process all PDFs in folder
- `GET /api/documents` - List all documents
- `GET /api/documents/{doc_id}` - Get document details
- `GET /api/documents/{doc_id}/pages/{page_num}/image` - Get page image

### Agent
- `POST /api/agent/start-analysis` - Start legal risk analysis
- `GET /api/agent/status` - Get current agent status and todos

### Approvals
- `GET /api/approvals/pending` - Get pending approval requests
- `POST /api/approvals/{approval_id}/respond` - Respond to approval
- `GET /api/approvals/history` - Get approval history

### Files
- `GET /api/files` - List generated files
- `GET /api/files/{file_path}` - Get file content

### Health
- `GET /api/health` - Health check endpoint

## 🧪 Testing

### Test the Document Pipeline
```bash
# 1. Place PDF files in backend/data/documents/
# 2. Call the process-all endpoint
curl -X POST http://localhost:8000/api/documents/process-all
```

### Test the Agent
```bash
# Start analysis
curl -X POST http://localhost:8000/api/agent/start-analysis

# Check status
curl http://localhost:8000/api/agent/status
```

## 📁 Project Structure

```
legal-risk-app/
├── backend/
│   ├── app/
│   │   ├── agents/          # Deep agents implementation
│   │   │   ├── base_agent.py
│   │   │   └── legal_agents.py
│   │   ├── api/             # API routes and approval system
│   │   │   └── approval_system.py
│   │   ├── database/        # Database configuration
│   │   │   └── db.py
│   │   ├── models/          # SQLAlchemy models
│   │   │   └── document.py
│   │   ├── services/        # Business logic
│   │   │   └── document_processor.py
│   │   ├── tools/           # LangChain tools
│   │   │   ├── document_tools.py
│   │   │   └── web_tools.py
│   │   └── main.py          # FastAPI application
│   ├── config/              # Configuration
│   │   └── settings.py
│   ├── data/                # Data storage
│   │   ├── documents/       # PDF files
│   │   ├── images/          # Page images
│   │   └── legal_docs.db    # SQLite database
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── DocumentList/
│   │   │   ├── TodoPanel/
│   │   │   ├── WorkflowPanel/
│   │   │   ├── PDFViewer/
│   │   │   └── FileEditor/
│   │   ├── services/        # API service
│   │   │   └── api.ts
│   │   ├── styles/          # CSS styles
│   │   │   └── App.css
│   │   ├── types.ts         # TypeScript types
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── documents/               # Sample documents (optional)
└── README.md
```

## 🔐 Security Considerations

- **API Keys**: Never commit `.env` files to version control
- **File Upload**: PDF files only, with size limits
- **Sandboxing**: Agent file operations are sandboxed to workspace directory
- **Human Approval**: Critical operations require human approval
- **Input Validation**: All API inputs are validated

## 🚧 Known Limitations

- **Internet Search**: Requires Google Custom Search API setup (mock implementation provided)
- **Token Limits**: Very large documents may need chunking
- **Concurrent Analysis**: Only one analysis session at a time
- **Real-time Updates**: Uses polling (can be upgraded to WebSockets for production)

## 🔄 Future Enhancements

- [ ] Support for multiple document formats (DOCX, TXT)
- [ ] Advanced search and filtering
- [ ] Export reports to PDF
- [ ] User authentication and multi-tenancy
- [ ] Persistent WebSocket connections
- [ ] Background job processing with Celery
- [ ] PostgreSQL database for production
- [ ] Docker containerization
- [ ] Kubernetes deployment configuration

## 📄 License

This project is a demonstration of Deep Agents architecture for legal document analysis.

## 🤝 Contributing

This is a reference implementation following LangChain Deep Agents patterns. Feel free to fork and adapt for your use case.

## 📞 Support

For issues or questions about the Deep Agents framework, refer to the documentation in this repository.

---

Built with ❤️ using Claude Sonnet 4.5, LangChain Deep Agents, FastAPI, and React.
