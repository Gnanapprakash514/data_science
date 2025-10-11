import streamlit as st
from utils.api_client import upload_file

st.title("📤 Upload Data")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    res = upload_file(uploaded_file)

    if res is None:
        st.error("🚫 Cannot connect to backend API. Make sure it’s running.")
    elif res.status_code == 200:
        st.success("✅ File uploaded successfully!")
    else:
        st.error(f"❌ Upload failed (Status: {res.status_code})")
