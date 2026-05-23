from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from document_loader import convert_uploaded_file_to_text


CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "documents"


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def create_text_file_from_document(file_path, output_text_path):
    readable_text = convert_uploaded_file_to_text(file_path)

    with open(output_text_path, "w", encoding="utf-8") as file:
        file.write(readable_text)

    return output_text_path


def create_vector_database(text_file_path, file_id, file_name):
    loader = TextLoader(text_file_path, encoding="utf-8")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    for chunk in chunks:
        chunk.metadata.update({
            "file_id": str(file_id),
            "file_name": file_name
        })

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME
    )

    return vector_db