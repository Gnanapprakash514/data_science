from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from database import get_db
from models import Dataset, DatasetInsights

# PDF generation imports
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

import os
from collections import defaultdict

# ----------------------------------------------------------
# Router configuration
# ----------------------------------------------------------
router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# Create reports folder if not present
REPORTS_DIR = os.path.abspath("reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


# ----------------------------------------------------------
# Generate and download PDF report
# ----------------------------------------------------------
@router.get("/generate/{dataset_id}")
def generate_pdf_report(dataset_id: int, db: Session = Depends(get_db)):
    """
    Generate a detailed PDF report for a given dataset_id.
    The report includes dataset details and insights grouped by columns.
    """

    # 1️⃣ Fetch dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # 2️⃣ Fetch insights for the dataset
    insights = db.query(DatasetInsights).filter(DatasetInsights.dataset_id == dataset_id).all()
    if not insights:
        raise HTTPException(status_code=404, detail="No insights found for this dataset")

    # 3️⃣ Setup PDF file path
    file_path = os.path.join(REPORTS_DIR, f"report_{dataset_id}.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # ----------------------------------------------------------
    # Report Header
    # ----------------------------------------------------------
    story.append(Paragraph(f"Dataset Report: <b>{dataset.name}</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Filename:</b> {dataset.filename or 'N/A'}", styles["Normal"]))
    story.append(Paragraph(f"<b>Dataset ID:</b> {dataset.id}", styles["Normal"]))

    upload_date = dataset.upload_date.strftime('%Y-%m-%d %H:%M:%S') if dataset.upload_date else "N/A"
    story.append(Paragraph(f"<b>Upload Date:</b> {upload_date}", styles["Normal"]))
    story.append(Spacer(1, 20))

    # ----------------------------------------------------------
    # Insights Section (Sorted and Clean)
    # ----------------------------------------------------------
    grouped_insights = defaultdict(list)
    for ins in insights:
        grouped_insights[ins.column_name].append((ins.metric_name, ins.metric_value))

    story.append(Paragraph("<b>Insights Summary</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    # Define display order for better readability
    metric_order = ["missing_count", "mean", "std_dev", "Q1", "Q2 (Median)", "Q3", "Q4 (Max)", "mode"]

    for column, metrics in grouped_insights.items():
        # Sort metrics based on the predefined order
        metrics_sorted = sorted(
            metrics,
            key=lambda x: metric_order.index(x[0]) if x[0] in metric_order else len(metric_order)
        )

        story.append(Paragraph(f"<b>{column}</b>", styles["Heading3"]))
        data = [["Metric", "Value"]]
        for metric_name, metric_value in metrics_sorted:
            data.append([str(metric_name), str(metric_value)])

        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ]))
        story.append(table)
        story.append(Spacer(1, 15))

    # ----------------------------------------------------------
    # Build PDF
    # ----------------------------------------------------------
    try:
        doc.build(story)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

    # ----------------------------------------------------------
    # Verify PDF existence
    # ----------------------------------------------------------
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail=f"PDF file not found at {file_path}")

    # ----------------------------------------------------------
    # Return the file as downloadable response
    # ----------------------------------------------------------
    safe_name = dataset.name.replace(" ", "_").replace("/", "_")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{safe_name}_report.pdf"
    )
