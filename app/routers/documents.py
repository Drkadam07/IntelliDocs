# app/routers/documents.py
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, Document, current_time_ms
from app.schemas import DocumentResponse
from app.core.dependencies import get_current_user
from app.services.rag import (
    index_document_from_bytes,
    delete_document_vectors,
    clear_user_vectors,
)
from app.services.storage import (
    upload_file_to_neon,
    delete_file_from_neon,
    generate_neon_download_url,
)

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

    clean_filename = Path(file.filename).name
    neon_storage_key = f"users/{current_user.id}/{current_time_ms()}_{clean_filename}"

    # 1. Upload binary file into Neon Object Storage
    try:
        upload_file_to_neon(
            content, key=neon_storage_key, content_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload to Neon Object Storage: {str(e)}"
        )

    # 2. Save document record in PostgreSQL (stores the Neon storage key)
    doc = Document(
        user_id=current_user.id,
        name=clean_filename,
        size=file_size,
        file_path=neon_storage_key,
        created=current_time_ms(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 3. Vectorize and index chunks in ChromaDB directly from memory
    index_document_from_bytes(content, doc_id=doc.id, user_id=current_user.id)

    return doc


@router.get("/documents/{id}/download")
def get_document_download_url(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns a temporary presigned URL for direct secure download from Neon Object Storage."""
    doc = (
        db.query(Document)
        .filter(Document.id == id, Document.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    download_url = generate_neon_download_url(doc.file_path)
    return {"name": doc.name, "url": download_url}


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

    # 1. Delete object from Neon Object Storage
    try:
        delete_file_from_neon(doc.file_path)
    except Exception:
        pass

    # 2. Remove vector embeddings
    delete_document_vectors(doc_id=doc.id, user_id=current_user.id)

    # 3. Delete database record
    db.delete(doc)
    db.commit()
    return None


@router.post("/clear")
def clear_all(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # 1. Purge all PDF objects in Neon Object Storage for this user
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    for doc in docs:
        try:
            delete_file_from_neon(doc.file_path)
        except Exception:
            pass

    # 2. Clear SQL database entries
    db.query(Document).filter(Document.user_id == current_user.id).delete()
    db.query(Chat).filter(Chat.user_id == current_user.id).delete()
    db.commit()

    # 3. Clear ChromaDB embeddings for this user
    clear_user_vectors(user_id=current_user.id)

    return {
        "message": "All user documents, Neon storage objects, and chat histories cleared successfully."
    }
