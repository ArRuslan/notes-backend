from datetime import datetime

from tortoise.models import Model
from tortoise import fields


class User(Model):
    id: int = fields.IntField(pk=True)
    email: str = fields.CharField(max_length=255, unique=True)
    name: str = fields.TextField()
    password: str = fields.TextField()


class Session(Model):
    id: int = fields.IntField(pk=True)
    user: User = fields.ForeignKeyField("models.User")
    key: str = fields.TextField()


class Note(Model):
    id: int = fields.IntField(pk=True)
    user: User = fields.ForeignKeyField("models.User")
    name: str = fields.TextField(default="Unnamed")
    text: str = fields.TextField(default="# New note")
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)
