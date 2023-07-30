from os import environ

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_host = environ.get('DB_HOST')
db_port = environ.get('DB_PORT')
db_name = environ.get('DB_NAME')
db_user = environ.get('DB_USERNAME')
db_password = environ.get('DB_PASSWORD')

connection_string = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"
# print(connection_string)
engine = create_engine(connection_string, echo=True)

Session = sessionmaker(bind=engine)
db = Session()

Base = declarative_base()
