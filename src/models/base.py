from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

DATABASE_URL = "sqlite:///./test.db"  # Use the appropriate URL for your SQLite database file

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    print("creating database")
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("creating database")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()