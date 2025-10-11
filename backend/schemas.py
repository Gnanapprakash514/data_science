from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# -------------------------------
# User related schemas
# -------------------------------
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# -------------------------------
# File upload / dataset schemas
# -------------------------------
class FileUpload(BaseModel):
    filename: str
    filetype: str
    uploaded_at: Optional[datetime] = None
    user_id: Optional[int] = None

# -------------------------------
# Cleaned data / insights schemas
# -------------------------------
class DataCleanResponse(BaseModel):
    message: str
    cleaned_file_path: str
    insights: Optional[dict]  # key-value pairs of insights

# -------------------------------
# Generic response schema
# -------------------------------
class ResponseMessage(BaseModel):
    message: str
