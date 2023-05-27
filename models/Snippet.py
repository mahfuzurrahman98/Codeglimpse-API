from sqlalchemy import (TIMESTAMP, Column, Enum, ForeignKey, Integer, String,
                        Text, text)
from sqlalchemy.orm import relationship

from database import Base


class Snippet(Base):
    __tablename__ = 'snippets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(5), nullable=False)
    visibility = Column(Enum(1, 2, 3), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

# def __repr__(self):
#     return f'User(id={self.id}, name={self.name}, email={self.email}, city={self.address.city}, country={self.address.country})'
