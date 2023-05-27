from sqlalchemy import (TIMESTAMP, Column, Enum, ForeignKey, Integer,
                        SmallInteger, String, text)
from sqlalchemy.orm import relationship

from database import Base
from models.Snippet import Snippet


class ProgrammingLanguage(Base):
    __tablename__ = 'programming_languages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    alt_name = Column(String(50), nullable=True)
    active = Column(SmallInteger, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    snippets = relationship('Snippet', back_populates='programming_language')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'alt_name': self.alt_name
        }
