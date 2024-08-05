import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt
from datetime import timedelta
import models, schemas, crud
from database import SessionLocal, engine
from auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_default_user(db: Session):
    username = "admin"
    password = "admin"
    user = crud.get_user(db, username=username)
    if not user:
        hashed_password = get_password_hash(password)
        db_user = models.User(username=username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()

@app.on_event("startup")
def startup_event():
    with SessionLocal() as db:
        create_default_user(db)

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating user: {user.username}")
    try:
        db_user = crud.get_user(db, username=user.username)
        if db_user:
            logger.warning(f"Username {user.username} already registered")
            raise HTTPException(status_code=400, detail="Username already registered")
        return crud.create_user(db=db, user=user)
    except Exception as exc:
        logger.exception(f"An error occurred while creating user {user.username}: {exc}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Attempting to authenticate user: {form_data.username}")
    try:
        user = crud.get_user(db, username=form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Authentication failed for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        logger.info(f"User {form_data.username} authenticated successfully")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as exc:
        logger.exception(f"An error occurred during authentication for user {form_data.username}: {exc}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        logger.warning("Invalid token")
        raise credentials_exception
    user = crud.get_user(db, username=token_data.username)
    if user is None:
        logger.warning(f"User not found for token subject: {token_data.username}")
        raise credentials_exception
    logger.info(f"User {user.username} authenticated successfully with token")
    return user

@app.get("/messages/", response_model=List[schemas.Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    logger.info(f"User {current_user.username} is fetching messages with skip={skip} and limit={limit}")
    try:
        messages = crud.get_messages(db, skip=skip, limit=limit)
        logger.info(f"Fetched {len(messages)} messages for user {current_user.username}")
        return messages
    except Exception as exc:
        logger.exception(f"An error occurred while fetching messages: {exc}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/messages/", response_model=List[schemas.Message])
def create_user_message(message: schemas.MessageCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    try:
        # Create user message
        user_message = crud.create_message(db=db, message=message, sender='user')
        
        # Create system response
        bot_response_content = f"Your message was recorded as: {message.content}"
        system_message = crud.create_message(db=db, message=schemas.MessageCreate(content=bot_response_content), sender='system')
        
        # Return both messages
        return [user_message, system_message]
    except Exception as exc:
        logger.exception(f"An error occurred while creating messages: {exc}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/messages/{message_id}", response_model=schemas.Message)
def delete_message(message_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    logger.info(f"User {current_user.username} is attempting to delete message with ID: {message_id}")
    try:
        db_message = crud.get_message(db, message_id=message_id)
        if db_message is None:
            logger.warning(f"Message with ID {message_id} not found for user {current_user.username}")
            raise HTTPException(status_code=404, detail="Message not found")
        
        deleted_message = crud.delete_message(db=db, message_id=message_id)
        logger.info(f"Message with ID {message_id} successfully deleted by user {current_user.username}")
        return deleted_message
    
    except HTTPException as http_exc:
        logger.error(f"HTTP exception occurred: {http_exc.detail}")
        raise http_exc

    except Exception as exc:
        logger.exception(f"An unexpected error occurred while deleting message with ID {message_id}: {exc}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/messages/{message_id}", response_model=schemas.Message)
def update_message(message_id: int, updated_message: schemas.MessageCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    logger.info(f"User {current_user.username} is updating message with ID {message_id}")
    try:
        db_message = crud.get_message(db, message_id=message_id)
        if db_message is None:
            logger.warning(f"Message with ID {message_id} not found for user {current_user.username}")
            raise HTTPException(status_code=404, detail="Message not found")
        
        updated_message = crud.update_message(db=db, message_id=message_id, updated_message=updated_message)
        logger.info(f"Message with ID {message_id} updated successfully by user {current_user.username}")
        return updated_message
    
    except HTTPException as http_exc:
        logger.error(f"HTTP exception occurred: {http_exc.detail}")
        raise http_exc

    except Exception as exc:
        logger.exception(f"An unexpected error occurred while updating message with ID {message_id}: {exc}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
