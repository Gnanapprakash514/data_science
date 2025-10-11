from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import pandas as pd

from database import get_db
from models import Dataset

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

def get_unique_filename(folder: str, filename: str) -> str:
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename

@router.post("/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are allowed")
    
    # Generate unique filename
    unique_filename = get_unique_filename(UPLOAD_FOLDER, file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Read to get total rows
    try:
        df = pd.read_csv(file_path) if unique_filename.endswith(".csv") else pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")

    total_rows = len(df)

    # Save metadata
    dataset = Dataset(
        name=os.path.splitext(unique_filename)[0],
        filename=unique_filename,
        total_rows=total_rows,
        status="uploaded"
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return {
        "message": "File uploaded successfully",
        "filename": unique_filename,
        "total_rows": total_rows,
        "dataset_id": dataset.id
    }
