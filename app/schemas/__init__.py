from typing import List, Optional
from pydantic import BaseModel, EmailStr


# Auth Schemas
class RegisterRequest(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class ResendOTPRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None


# Chat Schemas
class MessageItem(BaseModel):
    role: str
    content: str

    class Config:
        from_attributes = True


class ChatCreateRequest(BaseModel):
    title: Optional[str] = "New Chat"


class ChatUpdateRequest(BaseModel):
    title: str


class ChatSummary(BaseModel):
    id: int
    title: str
    updated: int

    class Config:
        from_attributes = True


class ChatDetail(BaseModel):
    id: int
    title: str
    messages: List[MessageItem]


class SendMessageRequest(BaseModel):
    message: str


class SendMessageResponse(BaseModel):
    reply: str


# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    name: str
    size: int
    created: int

    class Config:
        from_attributes = True
