from django.urls import path
from .views import (
    home,
    upload_document,
    ask_question_api,
    get_chat_history,
    get_uploaded_documents,
    delete_chat_history,
    delete_specific_chat,
    delete_uploaded_document,
    delete_all_uploaded_documents
)

urlpatterns = [
    path("", home, name="home"),
    path("upload-document/", upload_document, name="upload_document"),
    path("ask/", ask_question_api, name="ask_question"),
    path("chat-history/", get_chat_history, name="chat_history"),
    path("documents/", get_uploaded_documents, name="uploaded_documents"),
    path("chat-history/delete/", delete_chat_history, name="delete_chat_history"),
    path("documents/delete/<int:file_id>/", delete_uploaded_document, name="delete_uploaded_document"),
    path("documents/delete-all/", delete_all_uploaded_documents, name="delete_all_uploaded_documents"),
    path("chat-history/delete/<int:chat_id>/",delete_specific_chat,name="delete_specific_chat"),
]