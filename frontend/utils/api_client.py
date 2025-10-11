import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000"  # Make sure FastAPI backend runs here


def upload_file(uploaded_file):
    """
    Upload a CSV/XLSX file to FastAPI backend.
    Must match backend endpoint: file: UploadFile = File(...)
    """
    if uploaded_file is None:
        st.warning("⚠️ Please select a file before uploading.")
        return None

    try:
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }

        response = requests.post(f"{BASE_URL}/upload/", files=files)

        if response.status_code == 200:
            return response
        elif response.status_code == 400:
            st.error(f"❌ Upload failed: {response.json().get('detail', 'Bad Request')}")
        elif response.status_code == 422:
            st.error("❌ Validation error: FastAPI did not receive a file field named 'file'.")
        else:
            st.error(f"❌ Unexpected error: {response.status_code} - {response.text}")

        return response

    except requests.exceptions.ConnectionError:
        st.error("🚫 Cannot connect to backend API. Make sure it’s running.")
        return None
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")
        return None


def get_data():
    """Fetch datasets metadata."""
    try:
        return requests.get(f"{BASE_URL}/datasets/")
    except requests.exceptions.ConnectionError:
        st.error("🚫 Backend not running for /datasets.")
        return None


def get_insights(dataset_id: int):
    """Generate insights for a specific dataset."""
    try:
        return requests.get(f"{BASE_URL}/insights/generate/{dataset_id}")
    except requests.exceptions.ConnectionError:
        st.error("🚫 Backend not running for /insights.")
        return None


def get_report(dataset_id: int):
    """Generate report for a specific dataset."""
    try:
        return requests.get(f"{BASE_URL}/reports/generate/{dataset_id}")
    except requests.exceptions.ConnectionError:
        st.error("🚫 Backend not running for /reports.")
        return None
