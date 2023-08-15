from sqlalchemy import TIMESTAMP, Column, Integer, SmallInteger, String, text, func
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(15), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    google_auth = Column(SmallInteger, nullable=False, server_default='0')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        nullable=True,
        default=None,
        onupdate=func.now(),
        server_onupdate=func.now()
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
