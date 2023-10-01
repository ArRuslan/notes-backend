from base64 import urlsafe_b64encode
from os import urandom

import bcrypt
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from .config import TORTOISE_ORM
from .models import User, Session, Note
from .schemas import RegisterData, LoginData, CreateNoteData, WriteNoteData, WriteNoteDiffData
from .utils import authUser

app = FastAPI()


@app.post("/api/v1/auth/register")
async def register(data: RegisterData):
    data = data.model_dump()
    data["password"] = bcrypt.hashpw(data["password"].encode().replace(b"\x00", b""), bcrypt.gensalt()).decode()
    user = await User.create(**data)
    await Note.create(user=user, name="First note", text="This is your **first note**!")
    session = await Session.create(user=user, key=urlsafe_b64encode(urandom(32)).decode())
    return {
        "token": f"{user.id}.{session.id}.{session.key}",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    }


@app.post("/api/v1/auth/login")
async def login(data: LoginData):
    user = await User.get_or_none(email=data.email)
    if not bcrypt.checkpw(data.password.encode().replace(b"\x00", b""), user.password.encode()):
        return {"errors": {"email": "Wrong email or password", "password": "Wrong email or password"}}, 400

    session = await Session.create(user=user, key=urlsafe_b64encode(urandom(32)).decode())
    return {
        "token": f"{user.id}.{session.id}.{session.key}",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    }


@app.get("/api/v1/me")
async def get_me(user: User = Depends(authUser)):
    return {"id": user.id, "name": user.name, "email": user.email}


@app.get("/api/v1/notes")
async def get_notes(user: User = Depends(authUser), with_content: bool=False):
    fields = ["id", "name"]
    if with_content:
        fields.append("text")
    return await Note.filter(user=user).all().values(*fields)


@app.post("/api/v1/notes")
async def get_notes(data: CreateNoteData, user: User = Depends(authUser)):
    kw = {"user": user}
    if data.name:
        kw["name"] = data.name
    note = await Note.create(**kw)
    return {
        "id": note.id,
        "name": note.name,
        "text": note.text,
    }


@app.get("/api/v1/notes/{note_id}")
async def get_notes(note_id: int, user: User = Depends(authUser)):
    if (note := await Note.get_or_none(id=note_id, user=user)) is None:
        return {"errors": {"note": "No such note"}}, 404
    return {
        "id": note.id,
        "name": note.name,
        "text": note.text,
    }


@app.patch("/api/v1/notes/{note_id}")
async def get_notes(data: CreateNoteData, note_id: int, user: User = Depends(authUser)):
    if (note := await Note.get_or_none(id=note_id, user=user)) is None:
        return {"errors": {"note": "No such note"}}, 404

    note.name = data.name or "Unnamed"
    await note.save()

    return {
        "id": note.id,
        "name": note.name,
        "text": note.text,
    }


@app.put("/api/v1/notes/{note_id}")
async def get_notes(data: WriteNoteData, note_id: int, user: User = Depends(authUser)):
    if (note := await Note.get_or_none(id=note_id, user=user)) is None:
        return {"errors": {"note": "No such note"}}, 404

    note.text = data.text
    await note.save()

    return {
        "id": note.id,
        "name": note.name,
        "text": note.text,
    }


@app.put("/api/v1/notes/{note_id}/diff")
async def get_notes(data: WriteNoteDiffData, note_id: int, user: User = Depends(authUser)):
    if (note := await Note.get_or_none(id=note_id, user=user)) is None:
        return {"errors": {"note": "No such note"}}, 404

    # TODO: decompress and apply diff
    #note.text = data.text
    #await note.save()

    return {
        "id": note.id,
        "name": note.name,
        "text": note.text,
    }


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
register_tortoise(app, config=TORTOISE_ORM)
