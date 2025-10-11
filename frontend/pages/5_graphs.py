import streamlit as st
import requests
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Dataset Plots", layout="wide")
st.title("📊 Dataset Graphs Dashboard")

# --- Input: Dataset ID
dataset_id = st.number_input("Enter Dataset ID", min_value=1, step=1)

if st.button("Generate Graphs"):
    try:
        # Call backend endpoint that reads dataset directly
        resp = requests.get(f"http://localhost:8000/graphs/{dataset_id}")
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        st.error(f"Failed to fetch dataset: {e}")
        st.stop()

    # --- Plot numeric columns
    st.subheader("Numeric Columns")
    for col in data['numeric']:
        fig_box = px.box(y=col['values'], labels={"y": col['column_name']}, title=f"Boxplot: {col['column_name']}")
        st.plotly_chart(fig_box, use_container_width=True)

        fig_hist = px.histogram(col['values'], nbins=20, labels={"value": col['column_name']}, title=f"Histogram: {col['column_name']}")
        st.plotly_chart(fig_hist, use_container_width=True)

        fig_line = px.line(y=col['values'], labels={"y": col['column_name'], "x": "Row Index"}, title=f"Lineplot: {col['column_name']}")
        st.plotly_chart(fig_line, use_container_width=True)

    # --- Plot categorical columns
    st.subheader("Categorical Columns")
    for col in data['categorical']:
        counts = {v: col['values'].count(v) for v in set(col['values'])}
        fig_bar = px.bar(x=list(counts.keys()), y=list(counts.values()), labels={"x": col['column_name'], "y": "Count"}, title=f"Bar Chart: {col['column_name']}")
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Numeric vs Categorical Example
    if data['numeric'] and data['categorical']:
        numeric_col = data['numeric'][0]
        categorical_col = data['categorical'][0]
        df = pd.DataFrame({
            numeric_col['column_name']: numeric_col['values'][:len(categorical_col['values'])],
            categorical_col['column_name']: categorical_col['values'][:len(numeric_col['values'])]
        })
        fig_box_grouped = px.box(df, x=categorical_col['column_name'], y=numeric_col['column_name'],
                                 title=f"{numeric_col['column_name']} by {categorical_col['column_name']}")
        st.plotly_chart(fig_box_grouped, use_container_width=True)
