# 🐝 DocuMind — AI Document Q&A Agent

DocuMind is an AI-powered document question-answering system that allows users to upload documents, retrieve relevant information, ask questions conversationally, and use AI-powered tools to analyze document content.

The project combines **Retrieval-Augmented Generation (RAG), vector search, Gemini, conversation memory, OCR, custom tools, and Model Context Protocol (MCP)** into a single document intelligence application.

---

## ✨ Features

- 📄 Upload multiple documents
- 🔎 Retrieval-Augmented Generation (RAG)
- 🧠 Conversational question answering
- 💾 Persistent conversation memory using SQLite
- 🗂️ Multi-document support
- 🔐 Document-level retrieval isolation
- 📕 PDF text extraction
- 📝 DOCX support
- 📃 TXT support
- 🗒️ Markdown support
- 🖼️ Image OCR
- 📸 OCR-based scanned document processing
- 🤖 Google Gemini integration
- 🛠️ Custom AI tools
- 🧮 Safe mathematical calculator tool
- 📊 Document statistics tool
- 📝 Document summary tool
- 🔌 MCP server
- 🔗 MCP client
- 🧪 MCP Inspector testing
- 🌐 Flask backend
- 💻 Interactive web interface
- 🔄 Persistent selected-document state
- 🧹 File validation and error handling

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │       User           │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   DocuMind Web UI    │
                         │ HTML / CSS / JS      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     Flask Server     │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
        ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
        │ Document       │  │ Conversation   │  │ Custom Tools   │
        │ Processing     │  │ Memory         │  │                │
        └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
                │                   │                   │
                ▼                   ▼                   ▼
        ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
        │ Chunking       │  │ SQLite         │  │ Statistics     │
        │ Embeddings     │  │ conversation.db│  │ Calculator     │
        └───────┬────────┘  └────────────────┘  │ Summary        │
                │                               └───────┬────────┘
                ▼                                       │
        ┌────────────────┐                              │
        │   ChromaDB     │◄─────────────────────────────┘
        │ Vector Store   │
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │ Relevant       │
        │ Context        │
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │ Google Gemini  │
        │ AI Model       │
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │    Answer      │
        └────────────────┘


                 MCP Layer
        ┌─────────────────────────┐
        │      MCP Client        │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │      MCP Server         │
        │ document_statistics     │
        └─────────────────────────┘