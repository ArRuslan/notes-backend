from typing import Optional

from pydantic import BaseModel


class RegisterData(BaseModel):
    name: str
    email: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


class CreateNoteData(BaseModel):
    name: Optional[str] = None


class WriteNoteData(BaseModel):
    text: str


class WriteNoteDiffData(BaseModel):
    compressed_diff: str
