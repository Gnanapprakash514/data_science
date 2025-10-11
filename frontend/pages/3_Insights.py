import streamlit as st
from utils.api_client import get_insights, get_data # adjust import if needed

st.title("📊 Generate Insights")

# 1️⃣ Get dataset list
datasets_response = get_data()
if datasets_response is not None and datasets_response.status_code == 200:
    datasets = datasets_response.json().get("datasets", [])
    
    if datasets:
        # 2️⃣ Let user select dataset
        dataset_options = {d["name"]: d["dataset_id"] for d in datasets}
        selected_name = st.selectbox("Select a dataset", list(dataset_options.keys()))
        selected_id = dataset_options[selected_name]
        
        # 3️⃣ Generate Insights button
        if st.button("Generate Insights"):
            res = get_insights(selected_id)
            if res and res.status_code == 200:
                data = res.json()
                st.success(f"✅ {data['insights_count']} insights generated successfully!")
                st.json(data)
            else:
                st.error("Failed to generate insights.")
    else:
        st.warning("No datasets available.")
else:
    st.error("Failed to fetch datasets.")
