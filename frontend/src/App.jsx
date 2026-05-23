
import React, { useCallback, useEffect, useRef, useState } from "react";
import "./App.css";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function App() {
  const [documents, setDocuments] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [selectedFileIds, setSelectedFileIds] = useState([]);
  const [question, setQuestion] = useState("");

  const [modelType, setModelType] = useState("gemini");
  const [documentMode, setDocumentMode] = useState("specific");

  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  const chatEndRef = useRef(null);

  const showMessage = (msg) => {
    setMessage(msg);
    setTimeout(() => setMessage(""), 3000);
  };

  const getDocId = (doc) => doc.file_id || doc.id;
  const getDocName = (doc) => doc.file_name || doc.name || doc.title || "Document";

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/documents/`);
      const data = await res.json();
      setDocuments(Array.isArray(data) ? data : data.documents || []);
    } catch {
      showMessage("Failed to load documents.");
    }
  }, []);

  const fetchChatHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/chat-history/`);
      const data = await res.json();
      setChatHistory(Array.isArray(data) ? data : data.chat_history || data.history || []);
    } catch {
      showMessage("Failed to load chat history.");
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
    fetchChatHistory();
  }, [fetchDocuments, fetchChatHistory]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, loading]);

  const uploadDocuments = async () => {
    if (selectedFiles.length === 0) {
      showMessage("Please select at least one file.");
      return;
    }

    setUploading(true);

    try {
      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${API_BASE_URL}/upload-document/`, {
          method: "POST",
          body: formData,
        });

        if (!res.ok) throw new Error("Upload failed");
      }

      setSelectedFiles([]);
      document.getElementById("fileInput").value = "";
      showMessage("Document uploaded successfully.");
      fetchDocuments();
    } catch {
      showMessage("Upload failed. Check backend upload field name.");
    } finally {
      setUploading(false);
    }
  };

  const toggleDocumentSelection = (fileId) => {
    if (documentMode === "specific") {
      setSelectedFileIds([fileId]);
      return;
    }

    if (documentMode === "multiple") {
      setSelectedFileIds((prev) =>
        prev.includes(fileId)
          ? prev.filter((id) => id !== fileId)
          : [...prev, fileId]
      );
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) {
      showMessage("Please enter your question.");
      return;
    }

    if (documentMode === "specific" && selectedFileIds.length !== 1) {
      showMessage("Please select exactly one document.");
      return;
    }

    if (documentMode === "multiple" && selectedFileIds.length < 2) {
      showMessage("Please select at least two documents.");
      return;
    }

    const currentQuestion = question;
    setQuestion("");
    setLoading(true);

    const tempChat = {
      temp_id: Date.now(),
      question: currentQuestion,
      answer: "",
      pending: true,
    };

    setChatHistory((prev) => [...prev, tempChat]);

    try {
      const payload = {
        question: currentQuestion,
        model_type: modelType,
        document_mode: documentMode,
      };

      if (documentMode !== "all") {
        payload.file_ids = selectedFileIds;
      }

      const res = await fetch(`${API_BASE_URL}/ask/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) throw new Error("Ask failed");

      setChatHistory((prev) =>
        prev.map((chat) =>
          chat.temp_id === tempChat.temp_id
            ? {
                id: data.chat_id || data.id || null,
                temp_id: tempChat.temp_id,
                question: currentQuestion,
                answer: data.answer || data.response || data.message || "No answer received.",
              }
            : chat
        )
      );

      // fetchChatHistory();
    } catch {
      setChatHistory((prev) =>
        prev.map((chat) =>
          chat.temp_id === tempChat.temp_id
            ? {
                ...chat,
                pending: false,
                answer: "Something went wrong. Please check your backend.",
              }
            : chat
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const deleteSpecificDocument = async (fileId) => {
    if (!fileId) {
      showMessage("Invalid document id.");
      return;
    }

    if (!window.confirm("Delete this document?")) return;

    try {
      const res = await fetch(`${API_BASE_URL}/documents/delete/${fileId}/`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Delete failed");

      setDocuments((prev) => prev.filter((doc) => getDocId(doc) !== fileId));
      setSelectedFileIds((prev) => prev.filter((id) => id !== fileId));
      showMessage("Document deleted.");
    } catch {
      showMessage("Failed to delete document.");
    }
  };

  const deleteAllDocuments = async () => {
    if (!window.confirm("Delete all uploaded documents?")) return;

    try {
      const res = await fetch(`${API_BASE_URL}/documents/delete-all/`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Delete all failed");

      setDocuments([]);
      setSelectedFileIds([]);
      showMessage("All documents deleted.");
    } catch {
      showMessage("Failed to delete all documents.");
    }
  };

  const deleteAllChats = async () => {
    if (!window.confirm("Delete all chat history?")) return;

    try {
      const res = await fetch(`${API_BASE_URL}/chat-history/delete/`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Delete chats failed");

      setChatHistory([]);
      showMessage("Chat history cleared.");
    } catch {
      showMessage("Failed to clear chat history.");
    }
  };

  const deleteSpecificChat = async (chatId) => {
    if (!chatId) {
      showMessage("This chat is not saved in backend yet.");
      return;
    }
  
    if (!window.confirm("Delete this chat?")) return;
  
    try {
      const res = await fetch(`${API_BASE_URL}/chat-history/delete/${chatId}/`, {
        method: "DELETE",
      });
    
      if (!res.ok) {
        const errorText = await res.text();
        console.error("Delete chat error:", errorText);
        throw new Error("Delete chat failed");
      }
    
      setChatHistory((prev) =>
        prev.filter(
          (chat) =>
            chat.id !== chatId &&
            chat.chat_id !== chatId &&
            chat.temp_id !== chatId
        )
      );
    
      showMessage("Chat deleted.");
    } catch (error) {
      console.error(error);
      showMessage("Unable to delete this chat.");
    }
  };

  const handleDocumentModeChange = (mode) => {
    setDocumentMode(mode);
    setSelectedFileIds([]);
  };

  const handleEnter = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">AI</div>
          <div>
            <h2>DocuMind AI</h2>
            <p>Chat with your documents</p>
          </div>
        </div>

        <div className="card">
          <h3>Upload Documents</h3>

          <label className="upload-area" htmlFor="fileInput">
            <span>
              {selectedFiles.length > 0
                ? `${selectedFiles.length} file(s) selected`
                : "Choose files"}
            </span>
            <small>PDF, TXT, DOCX, CSV, XLSX, EDI, X12</small>
          </label>

          <input
            id="fileInput"
            type="file"
            multiple
            accept=".pdf,.txt,.doc,.docx,.csv,.xlsx,.edi,.x12"
            hidden
            onChange={(e) => setSelectedFiles(Array.from(e.target.files))}
          />

          <button onClick={uploadDocuments} disabled={uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </div>

        <div className="card">
          <h3>Model</h3>
          <select value={modelType} onChange={(e) => setModelType(e.target.value)}>
            <option value="gemini">Gemini</option>
            <option value="ollama">Ollama Local</option>
            <option value="openai" disabled>
              OpenAI - Future
            </option>
          </select>
        </div>

        <div className="card">
          <h3>Document Mode</h3>
          <select
            value={documentMode}
            onChange={(e) => handleDocumentModeChange(e.target.value)}
          >
            <option value="specific">Specific Document</option>
            <option value="multiple">Multiple Documents</option>
            <option value="all">All Documents</option>
          </select>

          <p className="hint">
            {documentMode === "specific" && "Select one document."}
            {documentMode === "multiple" && "Select two or more documents."}
            {documentMode === "all" && "Assistant will use all uploaded documents."}
          </p>
        </div>

        <div className="card documents-card">
          <div className="card-title">
            <h3>Documents</h3>
            {documents.length > 0 && (
              <button className="danger small" onClick={deleteAllDocuments}>
                Delete All
              </button>
            )}
          </div>

          {documents.length === 0 ? (
            <p className="empty">No documents uploaded.</p>
          ) : (
            <div className="document-list">
              {documents.map((doc) => {
                const fileId = getDocId(doc);
                const selected = selectedFileIds.includes(fileId);

                return (
                  <div
                    key={fileId}
                    className={`document-item ${selected ? "active" : ""} ${
                      documentMode === "all" ? "disabled" : ""
                    }`}
                  >
                    <div
                      className="document-info"
                      onClick={() =>
                        documentMode !== "all" && toggleDocumentSelection(fileId)
                      }
                    >
                      <span className="doc-icon">📄</span>
                      <div>
                        <strong>{getDocName(doc)}</strong>
                        <small>ID: {fileId}</small>
                      </div>
                    </div>

                    <button
                      className="delete-btn"
                      onClick={() => deleteSpecificDocument(fileId)}
                    >
                      ✕
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <button className="danger full" onClick={deleteAllChats}>
          Clear Chat History
        </button>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <h1>AI Document Assistant</h1>
            <p>
              Upload documents, select mode, choose model, and ask questions.
            </p>
          </div>

          <div className="status-pill">
            {documentMode === "all"
              ? "Using all documents"
              : `${selectedFileIds.length} selected`}
          </div>
        </header>

        {message && <div className="toast">{message}</div>}

        <section className="chat-box">
          {chatHistory.length === 0 ? (
            <div className="welcome">
              <h2>Start asking from your documents</h2>
              <p>
                Example: “Summarize this document”, “Find claim details”, or
                “Explain this PDF in simple words.”
              </p>
            </div>
          ) : (
            chatHistory.map((chat, index) => (
              <div className="chat-pair" key={chat.id || chat.temp_id || index}>
                <div className="message user">
                  <div className="bubble user-bubble">
                    {chat.question || chat.user_question || "Question"}
                  </div>
                </div>

                <div className="message assistant">
                  <div className="avatar">AI</div>
                  <div className="bubble assistant-bubble">
                    {chat.pending ? "Thinking..." : chat.answer || chat.response}

                    {chat.id && !chat.pending && (
                      <button
                        className="delete-chat"
                        onClick={() => deleteSpecificChat(chat.id)}
                      >
                        Delete this chat
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}

          <div ref={chatEndRef}></div>
        </section>

        <footer className="input-area">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleEnter}
            placeholder="Ask a question from your selected documents..."
          />

          <button onClick={askQuestion} disabled={loading}>
            {loading ? "Thinking..." : "Send"}
          </button>
        </footer>
      </main>
    </div>
  );
}

export default App;