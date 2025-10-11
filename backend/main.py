from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from database import Base, engine
from routers import upload, data, insights, reports, graphs  # include graphs

# ✅ Create DB tables if not existing
Base.metadata.create_all(bind=engine)

# ✅ Initialize FastAPI app
app = FastAPI(title="Smart Data Dashboard")

# ✅ Ensure static folders exist
UPLOAD_DIR = "uploaded_files"
REPORT_DIR = "reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# ✅ Serve static files (for reports & uploaded files)
app.mount("/uploaded_files", StaticFiles(directory=UPLOAD_DIR), name="uploaded_files")
app.mount("/report_files", StaticFiles(directory=REPORT_DIR), name="reports")

# ✅ Include Routers
app.include_router(upload.router)
app.include_router(data.router)
app.include_router(insights.router)
app.include_router(reports.router)
app.include_router(graphs.router)  # ✅ added graphs router

# ✅ Root endpoint
@app.get("/")
def home():
    return {"message": "Welcome to Smart Data Dashboard API!"}
