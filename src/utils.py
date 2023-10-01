from fastapi import HTTPException, Request

from .models import User, Session


async def authUser(request: Request) -> User:
    if not (auth := request.headers.get("authorization")):
        raise HTTPException(status_code=401, detail="No such session!")

    try:
        user_id, sess_id, key = auth.split(".")
        user_id = int(user_id)
        sess_id = int(sess_id)

        if ((session := await Session.get_or_none(id=sess_id, user_id=user_id, key=key).prefetch_related("user"))
                is None):
            raise Exception
    except Exception:
        raise HTTPException(status_code=401, detail="No such session!")

    return session.user
