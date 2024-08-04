# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.create_message(db=db, message=message, sender='user')

@app.get("/messages/", response_model=List[schemas.Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = crud.get_messages(db, skip=skip, limit=limit)
    return messages

@app.post("/chatbot/respond/", response_model=schemas.Message)
def chatbot_respond(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    bot_response = f"You said: {message.content}"
    return crud.create_message(db=db, message=schemas.MessageCreate(content=bot_response), sender='system')
