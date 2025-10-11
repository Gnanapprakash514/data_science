from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import os

from database import get_db
from models import Dataset, DatasetInsights

UPLOAD_FOLDER = "uploaded_files"

router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)

@router.get("/generate/{dataset_id}")
def generate_insights(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = os.path.join(UPLOAD_FOLDER, dataset.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    try:
        df = pd.read_csv(file_path) if dataset.filename.lower().endswith(".csv") else pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # Clear previous insights for this dataset
    db.query(DatasetInsights).filter(DatasetInsights.dataset_id == dataset.id).delete()
    db.commit()

    insights_to_add = []
    for col in df.columns:
        col_data = df[col]

        # Missing values count
        insights_to_add.append(
            DatasetInsights(
                dataset_id=dataset.id,
                column_name=col,
                metric_name="missing_count",
                metric_value=str(col_data.isnull().sum())
            )
        )

        # Only numeric columns
        if pd.api.types.is_numeric_dtype(col_data):
            # Mean
            insights_to_add.append(
                DatasetInsights(
                    dataset_id=dataset.id,
                    column_name=col,
                    metric_name="mean",
                    metric_value=str(col_data.mean())
                )
            )

            # Standard deviation
            insights_to_add.append(
                DatasetInsights(
                    dataset_id=dataset.id,
                    column_name=col,
                    metric_name="std_dev",
                    metric_value=str(col_data.std())
                )
            )

            # Quartiles (Q1, Q2, Q3, Q4)
            quantiles = col_data.quantile([0.25, 0.5, 0.75, 1.0])
            q_names = ["Q1", "Q2 (Median)", "Q3", "Q4 (Max)"]
            for q_name, q_val in zip(q_names, quantiles):
                insights_to_add.append(
                    DatasetInsights(
                        dataset_id=dataset.id,
                        column_name=col,
                        metric_name=q_name,
                        metric_value=str(q_val)
                    )
                )

            # Mode (first mode)
            mode_val = col_data.mode().iloc[0] if not col_data.mode().empty else None
            insights_to_add.append(
                DatasetInsights(
                    dataset_id=dataset.id,
                    column_name=col,
                    metric_name="mode",
                    metric_value=str(mode_val)
                )
            )

    db.add_all(insights_to_add)
    db.commit()

    return {
        "dataset_id": dataset.id,
        "filename": dataset.filename,
        "insights_count": len(insights_to_add),
        "message": "Insights generated successfully with quartiles, mode, and std deviation"
    }
