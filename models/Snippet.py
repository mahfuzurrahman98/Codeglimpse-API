from sqlalchemy import (TIMESTAMP, Column, Enum, ForeignKey, Integer,
                        SmallInteger, String, Text, text)
from sqlalchemy.orm import relationship

from database import Base, db
from models.User import User


class Snippet(Base):
    __tablename__ = 'snippets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(50), nullable=False)
    title = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(Integer, ForeignKey('programming_languages.id'))
    visibility = Column(SmallInteger, nullable=False)
    share_with = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(
        TIMESTAMP,
        server_default=text(
            'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
        )
    )
    deleted_at = Column(TIMESTAMP, nullable=True)

    programming_language = relationship(
        'ProgrammingLanguage', back_populates='snippets')
    user = relationship('User', back_populates='snippets')

    def serialize(self):

        _snippet = {
            'id': self.id,
            'uid': self.uid,
            'title': self.title,
            'content': self.content,
            'language': self.programming_language.name,
            'visibility': self.visibility,
            'owner': self.user.name,

        }

        if self.visibility == 2:
            shared_with_users = []
            for user_id in self.share_with.split(','):
                shared_with_users.append(
                    db.query(User).get(user_id).serialize())
            _snippet['shared_with'] = shared_with_users

        _snippet['created_at'] = str(self.created_at)
        _snippet['updated_at'] = str(self.updated_at)
        return _snippet
