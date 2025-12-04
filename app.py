import streamlit as st
from query import ask
from ingest import build_index
import os

st.set_page_config(page_title="GraceWise RAG", layout="wide")
st.title("📚 GraceWise Full-Folder RAG Assistant")

if st.button("Build / Rebuild Vector Index"):
    st.warning("This will rebuild embeddings for ALL files. Takes time.")
    with st.spinner("Processing all documents..."):
        build_index()
    st.success("Index created.")

query = st.text_input("Ask something:")

if query:
    with st.spinner("Thinking..."):
        answer = ask(query)
    st.subheader("🧠 Answer")
    st.write(answer)
