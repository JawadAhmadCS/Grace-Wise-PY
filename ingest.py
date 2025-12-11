import os
import json

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_core.documents import Document

# your config imports
from config import CONTENT_DIR, VECTORSTORE_DIR, EMBED_MODEL

# your NEW single-file input/output paths
INPUT_PATH = r"C:/Users/mjawa/Pictures/AI Projects/GraceWiseAi/Content Library/Curriculum & Learning Styles/Curriculum Options & Comparisons/Christian_Homeschool_Curriculum_Guide_Designed.txt"


# --------------------------------------------
# 1️⃣ NEW — embed only one uploaded text file
# --------------------------------------------
def embed_single_file():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"File not found: {INPUT_PATH}")

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = text.split("\n\n")

    docs = [Document(page_content=c, metadata={"source": INPUT_PATH}) for c in chunks]

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = FAISS.from_documents(docs, embeddings)

    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_DIR)

    print("✅ Single-file FAISS index created successfully.")

    return vectorstore


# --------------------------------------------
# 2️⃣ ORIGINAL — Loads ALL documents in folder
# --------------------------------------------
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

            loaded_docs = loader.load()

            for d in loaded_docs:
                d.metadata["source"] = path

            docs.extend(loaded_docs)

    return docs


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300
    )
    return splitter.split_documents(documents)


def embed_documents(chunks):
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_DIR)

    return vectorstore


# --------------------------------------------
# 3️⃣ ORIGINAL — builds entire index for folder
# --------------------------------------------
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


# --------------------------------------------
# Choose which mode to run
# --------------------------------------------
if __name__ == "__main__":
    # OPTION 1: run folder-based embedding
    build_index()

    # OPTION 2: run your single-file embedding
    #embed_single_file()
