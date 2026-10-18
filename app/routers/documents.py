from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.db.models import User, Document, current_time_ms
from app.schemas import DocumentResponse
from app.core.dependencies import get_current_user
from app.services.rag import index_document, delete_document_vectors, clear_user_vectors

router = APIRouter(tags=["Documents & Maintenance"])


@router.get("/documents", response_model=List[DocumentResponse])
def get_documents(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return db.query(Document).filter(Document.user_id == current_user.id).all()


@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are allowed")

    content = await file.read()
    file_size = len(content)

    # Clean file path storage
    clean_filename = Path(file.filename).name
    save_filename = f"user_{current_user.id}_{int(current_time_ms())}_{clean_filename}"
    file_path = settings.UPLOAD_DIR / save_filename

    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        user_id=current_user.id,
        name=clean_filename,
        size=file_size,
        file_path=str(file_path),
        created=current_time_ms(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Vectorize and index into ChromaDB
    index_document(file_path, doc_id=doc.id, user_id=current_user.id)

    return doc


@router.delete("/documents/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = (
        db.query(Document)
        .filter(Document.id == id, Document.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove vector index and local file
    delete_document_vectors(doc_id=doc.id, user_id=current_user.id)
    file_path = Path(doc.file_path)
    if file_path.exists():
        file_path.unlink()

    db.delete(doc)
    db.commit()
    return None


@router.post("/clear")
def clear_all(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # 1. Clear database documents and chats
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    for doc in docs:
        p = Path(doc.file_path)
        if p.exists():
            p.unlink()

    db.query(Document).filter(Document.user_id == current_user.id).delete()
    db.query(Chat).filter(Chat.user_id == current_user.id).delete()
    db.commit()

    # 2. Clear ChromaDB embeddings for this user
    clear_user_vectors(user_id=current_user.id)

    return {"message": "All user chats and document vectors cleared successfully."}
