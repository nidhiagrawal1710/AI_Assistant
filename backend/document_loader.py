import os
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document


def read_pdf(file_path):
    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def read_txt_like_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read()


def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df.to_string(index=False)


def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df.to_string(index=False)


def read_docx(file_path):
    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)


def convert_uploaded_file_to_text(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return read_pdf(file_path)

    if extension in [".txt", ".edi", ".x12"]:
        return read_txt_like_file(file_path)

    if extension == ".csv":
        return read_csv(file_path)

    if extension in [".xlsx", ".xls"]:
        return read_excel(file_path)

    if extension == ".docx":
        return read_docx(file_path)

    raise ValueError(
        "Unsupported file type. Supported types: PDF, TXT, EDI, X12, CSV, XLSX, DOCX"
    )