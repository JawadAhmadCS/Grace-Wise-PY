import os
from groq import Groq
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import VECTORSTORE_DIR, GROQ_MODEL, EMBED_MODEL
from sentence_transformers import CrossEncoder

# Load .env file
load_dotenv()

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

GROQ_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_KEY:
    raise ValueError("❌ GROQ_API_KEY not found. Add it to your .env file.")

client = Groq(api_key=GROQ_KEY)

def load_vectorstore():
    embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return FAISS.load_local(VECTORSTORE_DIR, embedding, allow_dangerous_deserialization=True)

def ask(query):
    vs = load_vectorstore()

    # STEP 1 — Initial similarity retrieval (broad net)
    raw_docs = vs.similarity_search(query, k=40)

    # STEP 2 — Prepare pairs for cross-encoder
    pairs = [(query, doc.page_content) for doc in raw_docs]

    # STEP 3 — Get relevance scores
    scores = reranker.predict(pairs)

    # STEP 4 — Sort docs by score (highest relevance first)
    ranked = sorted(
        zip(raw_docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    # STEP 5 — Keep top 10 (final RAG context)
    retrieved_docs = [doc for doc, score in ranked[:20]]

    # STEP 6 — Build the context string
    context = "\n\n".join([
        f"[Chunk ID: {i}] Source: {d.metadata.get('source')}\n{d.page_content}"
        for i, d in enumerate(retrieved_docs)
    ])

    # STEP 7 — Construct the GraceWise system prompt
    prompt = f"""
You are **GraceWise**, a faith-rooted Christian homeschool mentor.
Your purpose is to guide parents with clarity, confidence, and Biblical grounding.
You provide practical curriculum advice, spiritual encouragement, legal awareness
(general, not legal counsel), and real-world teaching strategies that strengthen
families and support Christ-centered homeschooling.

RULES:
1. Use ONLY the information from the context chunks below.
2. If the answer is not in the context, say “I don’t know.”
3. Do NOT fabricate information, scripture, or curriculum features.
4. Do NOT reveal chunk IDs or document names.
5. Keep answers short, clear, and rooted in Biblical wisdom.

### CONTEXT
{context}

### QUESTION
{query}


"""


    # STEP 8 — Call Groq LLM
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # STEP 9 — Return the answer
    return response.choices[0].message.content
