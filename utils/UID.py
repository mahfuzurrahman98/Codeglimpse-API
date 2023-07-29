from uuid import uuid4
from database import db
from models.Snippet import Snippet


def generate():
    uid = str(uuid4())
    uid = uid.replace('-', '')
    uid = uid[:10]
    snippet = db.query(Snippet).filter(Snippet.uid == uid).first()
    if snippet:
        return generate()
    return uid
