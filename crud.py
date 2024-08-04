# crud.py
from sqlalchemy.orm import Session
import models, schemas

def get_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Message).offset(skip).limit(limit).all()

def create_message(db: Session, message: schemas.MessageCreate, sender: str):
    db_message = models.Message(content=message.content, sender=sender)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
