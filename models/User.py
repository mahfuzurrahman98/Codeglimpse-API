from sqlalchemy import TIMESTAMP, Column, Integer, SmallInteger, String, text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(15), unique=True, nullable=True)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    google_auth = Column(SmallInteger, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    snippets = relationship('Snippet', back_populates='user')

    def serialize(self):
        # print(self.email)
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email
        }
