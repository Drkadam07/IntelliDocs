# app/db/models.py
import time
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.db.session import Base


def current_time_ms() -> int:
    return int(time.time() * 1000)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    otp_code = Column(String(10), nullable=True)
    otp_expiry = Column(BigInteger, nullable=True)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    documents = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    created = Column(BigInteger, default=current_time_ms)

    user = relationship("User", back_populates="documents")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), default="New Chat")
    created = Column(BigInteger, default=current_time_ms)
    updated = Column(BigInteger, default=current_time_ms, onupdate=current_time_ms)

    user = relationship("User", back_populates="chats")
    messages = relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(
        Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(String(10), nullable=False)  # "user" or "bot"
    content = Column(Text, nullable=False)
    created = Column(BigInteger, default=current_time_ms)

    chat = relationship("Chat", back_populates="messages")
