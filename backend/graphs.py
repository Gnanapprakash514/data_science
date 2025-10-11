from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Dataset
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
import os

UPLOAD_FOLDER = "uploaded_files"
router = APIRouter(prefix="/graphs", tags=["Graphs"])

# Pydantic models
class NumericColumnData(BaseModel):
    column_name: str
    values: List[float]  # raw numeric values

class CategoricalColumnData(BaseModel):
    column_name: str
    values: List[str]  # raw categorical values

class GraphDataResponse(BaseModel):
    numeric: List[NumericColumnData]
    categorical: List[CategoricalColumnData]

@router.get("/{dataset_id}", response_model=GraphDataResponse)
def generate_graph_data(dataset_id: int, db: Session = Depends(get_db)):
    # 1️⃣ Fetch dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = os.path.join(UPLOAD_FOLDER, dataset.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # 2️⃣ Read dataset
    try:
        df = pd.read_csv(file_path) if dataset.filename.lower().endswith(".csv") else pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # 3️⃣ Extract numeric and categorical values
    numeric_cols = df.select_dtypes(include='number').columns
    numeric_data = [NumericColumnData(column_name=col, values=df[col].dropna().tolist()) for col in numeric_cols]

    categorical_cols = df.select_dtypes(include='object').columns
    categorical_data = [CategoricalColumnData(column_name=col, values=df[col].dropna().astype(str).tolist()) for col in categorical_cols]

    return GraphDataResponse(numeric=numeric_data, categorical=categorical_data)
