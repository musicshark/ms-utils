from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from pydantic import BaseModel
from typing import Optional, List

import os


app = FastAPI(title="MSS-API")

def db_create_filepath(user_id):
    if not os.path.exists("./db/{user_id}"):
        os.system("mkdir -p ./db/{user_id}")

    fp = str(f"./db/{user_id}")
    #print(f"Existing DB Filepath: ./db/{db_file_name}.db")
    return fp









@app.get("/")
def root():
    return {"message":"TEST"}

@app.post("/update/{USER_ID}/day-db/")
def update_db_day_sessions(DB_DAY_NAME, SESSION_NAME, UUID):
    db_filepath = db_create_filepath(USER_ID)

    db_day_engine = create_engine("sqlite:///{db_filepath}/{DB_DAY_NAME}.db")
    db_day_SessionLocal = sessionmaker(autocommit=False, autoFlush=False, bind=db_day_engine)
    db_day_Base = declarative_base()

    class session_note_table(db_day_Base):
        __tablename__ = SESSION_NAME

        name = Column(Integer, nullable=False)
        total_notes_played = Column(Integer, nullable=False)
        total_note_time_played = Column(Float, nullable=False)
        start = Column(Float, nullable=False)
        end = Column(Float, nullable=False)
        runtime = Column(Float, nullable=False)
        note_name = Column(String, nullable=False)
        note_times_played = Column(Integer, nullable=False)
        note_time_total = Column(Float, nullable=False)

    Base.metadata.create_all(db_day_engine)

    class UpdateDayDB(BaseModel):
        name:str
        total_notes_played:int
        total_notes_played:float
        start:float
        end:float
        runtime:float
        note_name:str
        note_times_played:int
        note_time_total:float

    class UpdateDayDBResponse(BaseModel):
        name:str
        total_notes_played:int
        total_notes_played:float
        start:float
        end:float
        runtime:float
        note_name:str
        note_times_played:int
        note_time_total:float

        class Config:
            from_attributes = True

    db = db_day_SessionLocal()
    try:
        yield db
    finally:
        db.close()

update_db_day_sessions()