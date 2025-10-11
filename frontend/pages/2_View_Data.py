import streamlit as st
import pandas as pd
from utils.api_client import get_data

st.title("📂 View Datasets")

if st.button("Fetch Data"):
    res = get_data()
    if res.status_code == 200:
        df = pd.DataFrame(res.json())
        st.dataframe(df)
    else:
        st.error("❌ Failed to fetch data")
