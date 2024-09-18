# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, EmailStr
# from typing import Optional, List, Dict, Union
# from datetime import date

# app = FastAPI()

# # Correctly typed in-memory "database" to store user accounts
# users_db: List[Dict[str, Union[str, int, date, None]]] = []

# # Pydantic model to define account creation request
# class UserCreate(BaseModel):
#     email: EmailStr
#     date_of_birth: date
#     full_name: str
#     country: Optional[str] = None
#     job: Optional[str] = None

# # Pydantic model to define a user response (could include more details in real-world scenarios)
# class UserResponse(BaseModel):
#     id: int
#     email: EmailStr
#     full_name: str
#     country: Optional[str] = None
#     job: Optional[str] = None

# @app.post("/create_account", response_model=UserResponse)
# async def create_account(user: UserCreate):
#     # Simulate checking if the email is already registered
#     for existing_user in users_db:
#         if existing_user['email'] == user.email:
#             raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create a new user (with proper typing)
#     new_user: Dict[str, Union[str, int, date, None]] = {
#         "id": len(users_db) + 1,  # ID is strictly int
#         "email": user.email,  # email is str
#         "date_of_birth": user.date_of_birth,  # date_of_birth is date
#         "full_name": user.full_name,  # full_name is str
#         "country": user.country,  # country is Optional[str]
#         "job": user.job  # job is Optional[str]
#     }
    
#     # Add the new user to our in-memory database
#     users_db.append(new_user)
    
#     # Return a response model with only public details
#     return UserResponse(
        
#         id=new_user["id"],  # id is an int
#         email=new_user["email"],  # email is a string (EmailStr)
#         full_name=new_user["full_name"],  # full_name is a string
#         country=new_user["country"],  # country is Optional[str]
#         job=new_user["job"]  # job is Optional[str]
#     )

# # Example endpoint to list all users (for testing purposes)
# @app.get("/users")
# async def get_users():
#     return users_db
# from fastapi import FastAPI, HTTPException, Depends
# from sqlmodel import SQLModel, create_engine, Field, Session, select
# from pydantic import EmailStr
# from typing import Optional, List
# from datetime import date

# # Create the FastAPI app
# app = FastAPI()

# # Define the SQLite database URL (use a different URL for other databases)
# DATABASE_URL = "postgresql://neondb_owner:8EG0IaWfuTJM@ep-cool-butterfly-a5jzey8j.us-east-2.aws.neon.tech/neondb?sslmode=require"
# engine = create_engine(DATABASE_URL, echo=True)

# # Define the User model with SQLModel
# class User(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     email: EmailStr = Field(index=True, unique=True)
#     full_name: str
#     date_of_birth: date
#     country: Optional[str] = None
#     job: Optional[str] = None

# # Create the database tables
# @app.on_event("startup")
# def on_startup():
#     SQLModel.metadata.create_all(engine)

# # Dependency to get a session with the database
# def get_session():
#     with Session(engine) as session:
#         yield session

# # Pydantic model for creating a user
# class UserCreate(SQLModel):
#     email: EmailStr
#     full_name: str
#     date_of_birth: date
#     country: Optional[str] = None
#     job: Optional[str] = None

# # Endpoint to create a user in the database
# @app.post("/users/", response_model=User)
# def create_user(user: UserCreate, session: Session = Depends(get_session)):
#     # Check if the user already exists
#     statement = select(User).where(User.email == user.email)
#     existing_user = session.exec(statement).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create the new user
#     new_user = User(
#         email=user.email,
#         full_name=user.full_name,
#         date_of_birth=user.date_of_birth,
#         country=user.country,
#         job=user.job
#     )
    
#     # Add the user to the session and commit
#     session.add(new_user)
#     session.commit()
#     session.refresh(new_user)  # To get the auto-generated ID
    
#     return new_user

# # Endpoint to get all users from the database
# @app.get("/users/", response_model=List[User])
# def get_users(session: Session = Depends(get_session)):
#     # Query all users from the database
#     users = session.exec(select(User)).all()
#     return users
import os
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import func

# Create the FastAPI app
app = FastAPI()

# Directory for storing uploaded files
UPLOAD_DIRECTORY = "./uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Database connection
DATABASE_URL = "postgresql://neondb_owner:8EG0IaWfuTJM@ep-cool-butterfly-a5jzey8j.us-east-2.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL, echo=True)

# Content Upload Model
class ContentUpload(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_name: str
    file_type: str
    file_path: str
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    scheduled_time: Optional[datetime] = None
    is_sent: bool = Field(default=False)

# Create database tables
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Dependency to get the session with the database
def get_session():
    with Session(engine) as session:
        yield session

# Upload content API
@app.post("/upload/")
async def upload_content(
    file: UploadFile = File(...),
    schedule_in_days: Optional[int] = Form(None),  # Optional scheduling
    db: Session = Depends(get_session)
):
    # Save the uploaded file to the file system
    file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    
    # Schedule the content (if provided)
    scheduled_time = None
    if schedule_in_days:
        scheduled_time = datetime.utcnow() + timedelta(days=schedule_in_days)
    
    # Create a new content record in the database
    new_content = ContentUpload(
        file_name=file.filename,
        file_type=file.content_type,
        file_path=file_location,
        scheduled_time=scheduled_time
    )
    
    # Add and commit the content record
    db.add(new_content)
    db.commit()
    db.refresh(new_content)

    return {"message": "File uploaded successfully", "content_id": new_content.id}

# Get all uploaded content (for testing purposes)
@app.get("/content/", response_model=List[ContentUpload])
def get_content(db: Session = Depends(get_session)):
    return db.exec(select(ContentUpload)).all()

# Logic to check if any scheduled content should be sent (runs periodically in the background)
@app.on_event("startup")
def schedule_checker():
    import threading
    import time
    
    def check_scheduled_content():
        while True:
            with Session(engine) as db:
                # Get content that is scheduled and not yet sent
                scheduled_contents = db.exec(
                    select(ContentUpload)
                    .where(ContentUpload.scheduled_time <= func.now(), ContentUpload.is_sent == False)
                ).all()
                
                for content in scheduled_contents:
                    # Mark content as sent
                    content.is_sent = True
                    db.add(content)
                    db.commit()
                    # Here, you'd implement logic to send the content (e.g., send an email or notification)
                    print(f"Content {content.file_name} scheduled to be sent")
            
            # Sleep for some time (e.g., check every 60 seconds)
            time.sleep(60)
    
    thread = threading.Thread(target=check_scheduled_content)
    thread.start()

