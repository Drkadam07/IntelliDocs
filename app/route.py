import io
import time
from pathlib import Path

from fastapi import APIRouter, Request, UploadFile, File
from pydantic import BaseModel
from pypdf import PdfReader

from app.RAG.rag import embedder, index_pdf, clear_collection
from app.LLM.llm import get_ai_reply
from app.db.database import (
    save_message,
    get_all_messages,
    save_document,
    clear_messages,
)

router = APIRouter()

# Project upload directory
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ChatMessage(BaseModel):
    message: str


@router.get("/test-embed")
def test_embed():
    texts = [
        "This is a test sentence about machine learning."
    ] * 8

    start_time = time.time()
    embeddings = list(embedder.embed(texts))
    elapsed = time.time() - start_time

    return {
        "elapsed_seconds": elapsed,
        "embeddings_count": len(embeddings),
    }


@router.get("/")
def read_root(request: Request):
    messages = get_all_messages()

    from fastapi.templating import Jinja2Templates

    templates = Jinja2Templates(
        directory=str(BASE_DIR / "frontend" / "templates")
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"messages": messages},
    )


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    # Use only the filename, not any client-supplied directory path
    filename = Path(file.filename or "document.pdf").name
    save_path = UPLOAD_DIR / filename

    # Save PDF
    with open(save_path, "wb") as f:
        f.write(pdf_bytes)

    # Extract PDF text
    reader = PdfReader(io.BytesIO(pdf_bytes))
    extracted_text = ""

    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    # Save document and index for RAG retrieval
    save_document(filename, extracted_text)
    num_chunks = index_pdf(str(save_path), doc_id=filename)

    return {
        "message": f"'{filename}' uploaded successfully.",
        "chunks": num_chunks,
    }


@router.post("/chat")
def chat(chat_message: ChatMessage):
    bot_reply = get_ai_reply(chat_message.message)

    save_message(chat_message.message, bot_reply)

    return {"reply": bot_reply}


@router.post("/clear")
def clear_chat():
    clear_messages()
    clear_collection()

    return {
        "message": "Chat history and uploaded documents cleared."
    }