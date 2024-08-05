# crud.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models, schemas
from auth import get_password_hash

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Message).offset(skip).limit(limit).all()

def get_message(db: Session, message_id: int):
    return db.query(models.Message).filter(models.Message.id == message_id).first()

def create_message(db: Session, message: schemas.MessageCreate, sender: str):
    db_message = models.Message(content=message.content, sender=sender)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: int):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
        return db_message
    else:
        raise HTTPException(status_code=404, detail="Message not found")

def update_message(db: Session, message_id: int, updated_message: schemas.MessageCreate):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        db_message.content = updated_message.content
        db.commit()
        db.refresh(db_message)
    return db_message
