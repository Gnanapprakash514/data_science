from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Dataset, DatasetCleaned, DatasetInsights

router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"]
)

@router.get("/")
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).all()
    if not datasets:
        raise HTTPException(status_code=404, detail="No datasets found")

    result = []
    for d in datasets:
        result.append({
            "dataset_id": d.id,
            "name": d.name,
            "filename": d.filename,
            "upload_date": d.upload_date,
            "total_rows": d.total_rows,
            "processed_rows": d.processed_rows,
            "status": d.status,
            "cleaned_rows_count": db.query(DatasetCleaned)
                                    .filter(DatasetCleaned.dataset_id == d.id).count(),
            "insights_count": db.query(DatasetInsights)
                                 .filter(DatasetInsights.dataset_id == d.id).count()
        })
    return {"datasets": result}


@router.get("/{dataset_id}")
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    cleaned_rows = db.query(DatasetCleaned).filter(DatasetCleaned.dataset_id == dataset.id).all()
    insights = db.query(DatasetInsights).filter(DatasetInsights.dataset_id == dataset.id).all()

    return {
        "dataset_id": dataset.id,
        "name": dataset.name,
        "filename": dataset.filename,
        "upload_date": dataset.upload_date,
        "total_rows": dataset.total_rows,
        "processed_rows": dataset.processed_rows,
        "status": dataset.status,
        "cleaned_rows": [row.row_data for row in cleaned_rows],
        "insights": [
            {
                "column_name": i.column_name,
                "metric_name": i.metric_name,
                "metric_value": i.metric_value
            } for i in insights
        ]
    }
