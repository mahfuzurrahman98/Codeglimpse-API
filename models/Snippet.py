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
    source_code = Column(Text, nullable=False)
    language = Column(SmallInteger, nullable=False)
    visibility = Column(SmallInteger, nullable=False)
    pass_code = Column(SmallInteger, nullable=False, default=24)
    theme = Column(String(10), nullable=False, default='monokai')
    font_size = Column(String(10), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(
        TIMESTAMP,
        server_default=text(
            'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
        )
    )
    deleted_at = Column(TIMESTAMP, nullable=True)

    user = relationship('User', back_populates='snippets')

    def serialize(self):
        _snippet = {
            'id': self.id,
            'uid': self.uid,
            'title': self.title,
            'source_code': self.content,
            'language': self.programming_language.name,
            'visibility': self.visibility,
            'owner': self.user.name,

        }

        if self.visibility == 2:
            _snippet['pass_code'] = self.pass_code
        
        _snippet['created_at'] = str(self.created_at)
        _snippet['updated_at'] = str(self.updated_at)
        return _snippet
