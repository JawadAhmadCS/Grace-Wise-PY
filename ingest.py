import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_core.documents import Document
from config import CONTENT_DIR, VECTORSTORE_DIR, EMBED_MODEL


def load_all_documents(base_path):
    docs = []

    for root, dirs, files in os.walk(base_path):
        for f in files:
            path = os.path.join(root, f)

            if f.lower().endswith(".txt"):
                loader = TextLoader(path, encoding="utf-8")

            elif f.lower().endswith(".pdf"):
                loader = PyPDFLoader(path)

            elif f.lower().endswith(".docx"):
                loader = Docx2txtLoader(path)

            else:
                continue

            loaded = loader.load()
            for d in loaded:
                d.metadata["source"] = path

            docs.extend(loaded)

    return docs


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300
    )
    return splitter.split_documents(documents)


def embed_documents(chunks):
    embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = FAISS.from_documents(chunks, embedding)

    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_DIR)

    return vectorstore


def build_index():
    print("🔍 Loading documents...")
    docs = load_all_documents(CONTENT_DIR)

    if not docs:
        raise ValueError("❌ No documents found in Content Library!")

    print(f"📄 Loaded {len(docs)} documents.")

    print("✂️ Chunking...")
    chunks = chunk_documents(docs)
    print(f"🔹 Created {len(chunks)} chunks.")

    print("🧠 Embedding chunks...")
    embed_documents(chunks)

    print("✅ FAISS index created successfully.")


if __name__ == "__main__":
    build_index()
