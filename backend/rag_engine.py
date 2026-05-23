import os
from dotenv import load_dotenv

import google.generativeai as genai
from openai import OpenAI

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "documents"


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def retrieve_context(question, file_ids=None):
    vector_db = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embeddings(),
        collection_name=COLLECTION_NAME
    )

    search_kwargs = {"k": 5}

    if file_ids:
        file_ids = [str(file_id) for file_id in file_ids]

        search_kwargs["filter"] = {
            "file_id": {
                "$in": file_ids
            }
        }

    retriever = vector_db.as_retriever(
        search_kwargs=search_kwargs
    )

    docs = retriever.invoke(question)

    context_parts = []

    for doc in docs:
        file_name = doc.metadata.get("file_name", "Unknown file")

        context_parts.append(
            f"Source File: {file_name}\n"
            f"Content:\n{doc.page_content}"
        )

    return "\n\n".join(context_parts)


def build_prompt(question, context):
    return f"""
You are a helpful Document AI Assistant.

Answer only using the uploaded document context.
Do not use outside knowledge.

If the answer is not available in the provided document context, say:
"I could not find this information in the uploaded document."

Document Context:
{context}

User Question:
{question}

Answer:
"""


def ask_with_gemini(question, context):
    prompt = build_prompt(question, context)

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    return response.text


def ask_with_ollama(question, context):
    prompt = build_prompt(question, context)

    llm = Ollama(
        model="llama3.2",
        temperature=0
    )

    return llm.invoke(prompt)


def ask_with_openai(question, context):
    prompt = build_prompt(question, context)

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


def ask_question(question, model_type="gemini", file_ids=None):
    context = retrieve_context(
        question=question,
        file_ids=file_ids
    )

    if not context.strip():
        return "I could not find this information in the uploaded document."

    model_type = model_type.lower()

    if model_type == "gemini":
        return ask_with_gemini(question, context)

    if model_type == "ollama":
        return ask_with_ollama(question, context)

    if model_type == "openai":
        return ask_with_openai(question, context)

    return "Invalid model_type. Use 'gemini', 'ollama', or 'openai'."
