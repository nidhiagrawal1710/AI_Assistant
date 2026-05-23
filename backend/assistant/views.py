import os
from rest_framework.decorators import api_view
from rest_framework.response import Response

from vector_store import create_text_file_from_document, create_vector_database
from rag_engine import ask_question
from .models import UploadedDocument, ChatHistory
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_DIR = os.path.join(BASE_DIR, "media", "uploads")
PROCESSED_DIR = os.path.join(BASE_DIR, "media", "processed")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


@api_view(["GET"])
def home(request):
    return Response({
        "message": "Document RAG Chatbot Backend is running successfully"
    })


@api_view(["POST"])
def upload_document(request):
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return Response({
            "error": "No file uploaded. Use key name 'file'."
        }, status=400)

    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

    with open(file_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    text_file_path = os.path.join(
        PROCESSED_DIR,
        uploaded_file.name + "_readable.txt"
    )

    document_record = UploadedDocument.objects.create(
        file_name=uploaded_file.name,
        file_path=file_path,
        processed_text_path=text_file_path
    )

    try:
        create_text_file_from_document(file_path, text_file_path)

        create_vector_database(
            text_file_path=text_file_path,
            file_id=document_record.id,
            file_name=document_record.file_name
        )

    except Exception as e:
        document_record.delete()
        return Response({
            "error": "File processing failed",
            "details": str(e)
        }, status=500)

    return Response({
        "message": "Document uploaded and processed successfully",
        "file_id": document_record.id,
        "file_name": document_record.file_name,
        "status": "success"
    })


@api_view(["POST"])
def ask_question_api(request):
    question = request.data.get("question")
    model_type = request.data.get("model_type", "gemini")
    document_mode = request.data.get("document_mode", "specific")
    file_ids = request.data.get("file_ids", [])

    if not question:
        return Response({"error": "Question is required"}, status=400)

    allowed_models = ["gemini", "ollama", "openai"]

    if model_type not in allowed_models:
        return Response({
            "error": "Invalid model_type. Use 'gemini', 'ollama', or 'openai'."
        }, status=400)

    if document_mode not in ["specific", "multiple", "all"]:
        return Response({
            "error": "Invalid document_mode. Use 'specific', 'multiple', or 'all'."
        }, status=400)

    selected_documents = []

    if document_mode == "specific":
        if not file_ids or len(file_ids) != 1:
            return Response({
                "error": "For specific mode, provide exactly one file_id in file_ids."
            }, status=400)

    if document_mode == "multiple":
        if not file_ids or len(file_ids) < 2:
            return Response({
                "error": "For multiple mode, provide at least two file_ids."
            }, status=400)

    if document_mode in ["specific", "multiple"]:
        try:
            selected_documents = list(
                UploadedDocument.objects.filter(id__in=file_ids)
            )

            if len(selected_documents) != len(file_ids):
                return Response({
                    "error": "One or more file_ids are invalid."
                }, status=404)

        except Exception as e:
            return Response({
                "error": "Invalid file_ids",
                "details": str(e)
            }, status=400)

    if document_mode == "all":
        file_ids = None

    answer = ask_question(
        question=question,
        model_type=model_type,
        file_ids=file_ids
    )

    chat = ChatHistory.objects.create(
        question=question,
        answer=answer,
        model_type=model_type,
        document_mode=document_mode
    )

    if selected_documents:
        chat.documents.set(selected_documents)

    return Response({
        "chat_id": chat.id,
        "document_mode": document_mode,
        "file_ids": file_ids,
        "question": question,
        "model_type": model_type,
        "answer": answer
    })

@api_view(["GET"])
def get_chat_history(request):
    chats = ChatHistory.objects.all().order_by("-created_at")

    data = []

    for chat in chats:
        documents = chat.documents.all()

        data.append({
            "chat_id": chat.id,
            "documents": [
                {
                    "file_id": document.id,
                    "file_name": document.file_name
                }
                for document in documents
            ],
            "document_mode": chat.document_mode,
            "question": chat.question,
            "answer": chat.answer,
            "model_type": chat.model_type,
            "created_at": chat.created_at
        })

    return Response(data)


@api_view(["GET"])
def get_uploaded_documents(request):
    documents = UploadedDocument.objects.all().order_by("-uploaded_at")

    data = []

    for document in documents:
        data.append({
            "file_id": document.id,
            "file_name": document.file_name,
            "uploaded_at": document.uploaded_at
        })

    return Response(data)



@api_view(["DELETE"])
def delete_chat_history(request):
    ChatHistory.objects.all().delete()

    return Response({
        "message": "Chat history deleted successfully"
    })

@api_view(["DELETE"])
def delete_specific_chat(request, chat_id):
    try:
        chat = ChatHistory.objects.get(id=chat_id)

        chat.delete()

        return Response({
            "message": "Chat deleted successfully"
        })

    except ChatHistory.DoesNotExist:
        return Response({
            "error": "Chat not found"
        }, status=404)


@api_view(["DELETE"])
def delete_uploaded_document(request, file_id):
    try:
        document = UploadedDocument.objects.get(id=file_id)

        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        if os.path.exists(document.processed_text_path):
            os.remove(document.processed_text_path)

        document.delete()

        return Response({
            "message": "Document deleted successfully"
        })

    except UploadedDocument.DoesNotExist:
        return Response({
            "error": "Document not found"
        }, status=404)


@api_view(["DELETE"])
def delete_all_uploaded_documents(request):
    UploadedDocument.objects.all().delete()

    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    if os.path.exists(PROCESSED_DIR):
        shutil.rmtree(PROCESSED_DIR)
        os.makedirs(PROCESSED_DIR, exist_ok=True)

    if os.path.exists("chroma_db"):
        shutil.rmtree("chroma_db")

    return Response({
        "message": "All uploaded documents and vector data deleted successfully"
    })