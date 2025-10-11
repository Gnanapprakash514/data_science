from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Dataset
from pydantic import BaseModel
from typing import List
import pandas as pd
import os

UPLOAD_FOLDER = "uploaded_files"

router = APIRouter(
    prefix="/graphs",
    tags=["Graphs"]
)

# ----------------------
# Pydantic models
# ----------------------
class NumericColumnData(BaseModel):
    column_name: str
    values: List[float]

class CategoricalColumnData(BaseModel):
    column_name: str
    values: List[str]

class GraphDataResponse(BaseModel):
    numeric: List[NumericColumnData]
    categorical: List[CategoricalColumnData]

# ----------------------
# Endpoint: /graphs/{dataset_id}
# ----------------------
@router.get("/{dataset_id}", response_model=GraphDataResponse)
def generate_graph_data(dataset_id: int, db: Session = Depends(get_db)):
    # 1️⃣ Fetch dataset from DB
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    print("Requested Dataset ID:", dataset_id)
    print("Dataset found in DB:", dataset)

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # 2️⃣ Check file existence
    file_path = os.path.join(UPLOAD_FOLDER, dataset.filename)
    print("File path:", file_path)
    print("File exists:", os.path.exists(file_path))

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found on server")

    # 3️⃣ Read dataset
    try:
        if dataset.filename.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # 4️⃣ Separate numeric and categorical columns
    numeric_cols = df.select_dtypes(include='number').columns
    categorical_cols = df.select_dtypes(include='object').columns

    numeric_data = [
        NumericColumnData(column_name=col, values=df[col].dropna().tolist())
        for col in numeric_cols
    ]

    categorical_data = [
        CategoricalColumnData(column_name=col, values=df[col].dropna().astype(str).tolist())
        for col in categorical_cols
    ]

    # 5️⃣ Return data
    return GraphDataResponse(numeric=numeric_data, categorical=categorical_data)
