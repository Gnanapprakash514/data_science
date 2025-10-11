from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    status = Column(String(50), default="Pending")  # Pending / Processed / Error

    cleaned_rows = relationship("DatasetCleaned", back_populates="dataset")
    insights = relationship("DatasetInsights", back_populates="dataset")


class DatasetCleaned(Base):
    __tablename__ = "dataset_cleaned"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    row_data = Column(JSON)

    dataset = relationship("Dataset", back_populates="cleaned_rows")


class DatasetInsights(Base):
    __tablename__ = "dataset_insights"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    column_name = Column(String(255))
    metric_name = Column(String(50))
    metric_value = Column(String(255))

    dataset = relationship("Dataset", back_populates="insights")
