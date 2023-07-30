from sqlalchemy import (TIMESTAMP, Column, Enum, ForeignKey, Integer,
                        SmallInteger, String, Text, text)
from sqlalchemy.orm import relationship

from database import Base, db
from models.User import User
from lib.data.programming_languages import programming_languages


def get_language_name(ext):
    for lang in programming_languages:
        if lang['ext'] == ext:
            return lang['name']
    return None


class Snippet(Base):
    __tablename__ = 'snippets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(50), unique=True, nullable=False)
    title = Column(String(50), nullable=False)
    source_code = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    tags = Column(String(255), nullable=True)
    visibility = Column(SmallInteger, nullable=False)
    pass_code = Column(String(6), nullable=True)
    theme = Column(String(25), nullable=False, server_default='monokai')
    font_size = Column(SmallInteger, nullable=False, server_default='14')
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
            'source_code': self.source_code,
            'language': get_language_name(self.language),
            'visibility': self.visibility,
            'theme': self.theme,
            'font_size': self.font_size,
            'owner': self.user.name,

        }

        if self.tags:
            _snippet['tags'] = self.tags.split(',')

        if self.visibility == 2:
            _snippet['pass_code'] = self.pass_code

        _snippet['created_at'] = str(self.created_at)
        _snippet['updated_at'] = str(self.updated_at)
        return _snippet
