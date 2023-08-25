from os import environ

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_connection = environ.get('DB_CONNECTION')
db_host = environ.get('DB_HOST')
db_port = environ.get('DB_PORT')
db_name = environ.get('DB_NAME')
db_user = environ.get('DB_USERNAME')
db_password = environ.get('DB_PASSWORD')
db_connector = 'mysql+mysqlconnector' if db_connection == 'mysql' else 'postgresql+psycopg2'

# connection_string = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"
# connection_string = "postgresql://default:kwKXiHl51CvQ@ep-black-smoke-56527059.ap-southeast-1.postgres.vercel-storage.com:5432/verceldb"

connection_string = f"{db_connector}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# print(connection_string)
engine = create_engine(connection_string, echo=False)

Session = sessionmaker(bind=engine)
db = Session()

Base = declarative_base()
