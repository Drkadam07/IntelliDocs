from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, Chat, Message, current_time_ms
from app.schemas import (
    ChatSummary,
    ChatDetail,
    ChatCreateRequest,
    ChatUpdateRequest,
    SendMessageRequest,
    SendMessageResponse,
)
from app.core.dependencies import get_current_user
from app.services.rag import retrieve_context
from app.services.llm import generate_rag_answer

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get("", response_model=List[ChatSummary])
def list_chats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id)
        .order_by(Chat.updated.desc())
        .all()
    )


@router.post("", response_model=ChatSummary)
def create_chat(
    payload: ChatCreateRequest = ChatCreateRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_chat = Chat(user_id=current_user.id, title=payload.title or "New Chat")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


@router.get("/{id}", response_model=ChatDetail)
def get_chat(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.patch("/{id}", response_model=ChatSummary)
def update_chat(
    id: int,
    payload: ChatUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    chat.title = payload.title
    chat.updated = current_time_ms()
    db.commit()
    db.refresh(chat)
    return chat


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return None


@router.post("/{id}/messages", response_model=SendMessageResponse)
def post_chat_message(
    id: int,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 1. Retrieve RAG Context scoped to user's documents
    context = retrieve_context(payload.message, user_id=current_user.id)

    # 2. Generate grounded LLM reply
    bot_reply = generate_rag_answer(payload.message, context)

    # 3. Persist messages
    user_msg = Message(chat_id=chat.id, role="user", content=payload.message)
    bot_msg = Message(chat_id=chat.id, role="bot", content=bot_reply)

    chat.updated = current_time_ms()
    db.add(user_msg)
    db.add(bot_msg)
    db.commit()

    return SendMessageResponse(reply=bot_reply)
