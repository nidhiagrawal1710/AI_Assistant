````md
# DocuMind AI – Document RAG Assistant

DocuMind AI is a full-stack **AI document assistant** that allows users to upload documents and ask questions using a **Retrieval-Augmented Generation (RAG)** pipeline. It is designed for general document understanding, not limited to EDI.

The system supports multiple file types, stores document embeddings in **ChromaDB**, retrieves relevant context, and generates grounded answers using LLMs like **Gemini**, **Ollama**, and future-ready **OpenAI** support.

---

## Features

- Upload and chat with documents
- Supports PDF, TXT, CSV, DOCX, XLSX, EDI, and X12 files
- Specific document Q&A
- Multiple document Q&A
- All documents search mode
- Gemini API integration
- Ollama local LLM support
- OpenAI-ready architecture
- ChromaDB vector storage
- Metadata-based document filtering
- Chat history management
- Delete single chat
- Delete all chats
- Delete single document
- Delete all documents
- ChatGPT-style React frontend

---

## Tech Stack

### Backend
- Django
- Django REST Framework
- LangChain
- ChromaDB
- Sentence Transformers
- Gemini API
- Ollama
- OpenAI-ready integration

### Frontend
- React.js
- CSS
- REST API integration

---

## RAG Architecture

```text
Document Upload
      ↓
Text Extraction
      ↓
Chunking
      ↓
Embedding Generation
      ↓
ChromaDB Vector Storage
      ↓
Similarity Search
      ↓
Context Injection
      ↓
LLM Response
````

Each document chunk is stored with metadata:

```python
{
    "file_id": "document_id",
    "file_name": "uploaded_file_name"
}
```

This ensures the assistant retrieves answers only from the selected document or selected group of documents.

---

## Supported Document Modes

### 1. Specific Document

Ask questions from one selected document.

### 2. Multiple Documents

Ask questions across selected documents.

### 3. All Documents

Search and answer from all uploaded documents.

---

## API Endpoints

| Method | Endpoint                          | Description                          |
| ------ | --------------------------------- | ------------------------------------ |
| GET    | `/`                               | Backend health check                 |
| POST   | `/upload-document/`               | Upload and process document          |
| POST   | `/ask/`                           | Ask question from documents          |
| GET    | `/chat-history/`                  | Get chat history                     |
| GET    | `/documents/`                     | Get uploaded documents               |
| DELETE | `/chat-history/delete/`           | Delete all chat history              |
| DELETE | `/chat-history/delete/<chat_id>/` | Delete specific chat                 |
| DELETE | `/documents/delete/<file_id>/`    | Delete specific document             |
| DELETE | `/documents/delete-all/`          | Delete all documents and vector data |

---

## Example Ask API Request

```json
{
  "question": "Summarize this document",
  "model_type": "gemini",
  "document_mode": "specific",
  "file_ids": [1]
}
```

For multiple documents:

```json
{
  "question": "Compare these documents",
  "model_type": "gemini",
  "document_mode": "multiple",
  "file_ids": [1, 2]
}
```

For all documents:

```json
{
  "question": "Find all information related to this topic",
  "model_type": "gemini",
  "document_mode": "all"
}
```

---

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Backend runs on:

```text
http://127.0.0.1:8000/
```

---

## Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on:

```text
http://localhost:3000/
```

---

## Environment Variables

Create a `.env` file in backend:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

---

## Local LLM Setup with Ollama

Install Ollama and pull a model:

```bash
ollama pull llama3.2
```

Run Ollama locally before using the Ollama option.

---

## Project Highlights

This project demonstrates practical AI engineering concepts:

* Retrieval-Augmented Generation
* Vector database integration
* Semantic search
* Embedding-based document retrieval
* Multi-document context handling
* Prompt engineering
* Multi-LLM backend design
* Full-stack AI application development

---

## Project Status

This project is designed as a strong AI engineering portfolio project and can be extended for:

* Research paper assistants
* Legal document assistants
* Healthcare document assistants
* Enterprise knowledge base chatbots
* Resume and report analysis tools

```
```
"# AI_Assistant" 
"# AI_Assistant" 
