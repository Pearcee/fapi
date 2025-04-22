from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "*",
]
#   "user": [
#     {
#       "id": 1,
#       "firstName": "Emily",
#       "lastName": "Johnson",


# Define the User model
class Users(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    firstName: str
    lastName: str
    age: Optional[int]


# Create the FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create the SQLite database engine
engine = create_engine("sqlite:///database3.db")
SQLModel.metadata.create_all(engine)


# Dependency: Get the session
def get_session():
    with Session(engine) as session:
        yield session


# Create a User
@app.post("/user", response_model=Users)
def create_user(user: Users, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Read all user
@app.get("/user", response_model=list[Users])
def read_user(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    user = session.exec(select(Users).offset(skip).limit(limit)).all()
    return user


# Read a user by ID
@app.get("/user/{user_id}", response_model=Users)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Update a User
@app.put("/user/{user_id}", response_model=Users)
def update_user(
    user_id: int, user_data: Users, session: Session = Depends(get_session)
):
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's attributes
    for field, value in user_data.model_dump().items():
        setattr(user, field, value)
    session.commit()
    session.refresh(user)
    return user


# Delete a User
@app.delete("/user/{user_id}", response_model=Users)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return user


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
