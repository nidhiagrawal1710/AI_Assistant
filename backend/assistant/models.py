from django.db import models


class UploadedDocument(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    processed_text_path = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name


class ChatHistory(models.Model):
    documents = models.ManyToManyField(
        UploadedDocument,
        blank=True,
        related_name="chat_histories"
    )

    question = models.TextField()
    answer = models.TextField()
    model_type = models.CharField(max_length=50, default="gemini")
    document_mode = models.CharField(max_length=50, default="specific")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]