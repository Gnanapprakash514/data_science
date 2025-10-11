import streamlit as st

st.set_page_config(page_title="Smart Data Dashboard", layout="wide")

st.sidebar.title("📊 Navigation")
st.sidebar.markdown("Use the sidebar to navigate between pages")

st.title("Welcome to Data Dashboard")
st.markdown("""
This is the **frontend** built with Streamlit.  
Use the sidebar to:
1. Upload Data  
2. View Data  
3. Generate Insights  
4. Download Reports  
""")
