# app/services/rag.py
import io
from typing import List
import chromadb
from fastembed import TextEmbedding
from pypdf import PdfReader
from app.config import settings

embedder = TextEmbedding(
    model_name=settings.EMBEDDING_MODEL,
    providers=["CPUExecutionProvider"]
)

chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))
collection = chroma_client.get_or_create_collection(name="intellidocs_master")

def extract_pdf_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extracts text in-memory from PDF bytes."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text)

def chunk_text(text: str, chunk_size: int = 250, overlap: int = 30) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def index_document_from_bytes(pdf_bytes: bytes, doc_id: int, user_id: int) -> int:
    """Chunks, embeds, and indexes document text into ChromaDB directly from memory."""
    text = extract_pdf_text_from_bytes(pdf_bytes)
    chunks = chunk_text(text)
    if not chunks:
        return 0

    embeddings = [emb.tolist() for emb in embedder.embed(chunks)]
    ids = [f"user_{user_id}_doc_{doc_id}_{idx}" for idx in range(len(chunks))]
    metadatas = [{"user_id": user_id, "doc_id": doc_id} for _ in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )
    return len(chunks)

def delete_document_vectors(doc_id: int, user_id: int):
    collection.delete(
        where={
            "$and": [
                {"user_id": {"$eq": user_id}},
                {"doc_id": {"$eq": doc_id}}
            ]
        }
    )

def clear_user_vectors(user_id: int):
    collection.delete(where={"user_id": {"$eq": user_id}})

def retrieve_context(question: str, user_id: int, top_k: int = 4, threshold: float = 1.35) -> str:
    query_emb = list(embedder.embed([question]))[0].tolist()
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        where={"user_id": {"$eq": user_id}}
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents or not distances:
        return ""

    matched_chunks = [
        doc for doc, dist in zip(documents, distances)
        if dist <= threshold
    ]
    return "\n\n---\n\n".join(matched_chunks)