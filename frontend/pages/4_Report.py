import streamlit as st
from utils.api_client import get_data, get_report
import base64

st.title("📑 Download Report")

# 1️⃣ Get dataset list
datasets_response = get_data()
if datasets_response is not None and datasets_response.status_code == 200:
    datasets = datasets_response.json().get("datasets", [])

    if datasets:
        # 2️⃣ Let user select dataset
        dataset_options = {d["name"]: d["dataset_id"] for d in datasets}
        selected_name = st.selectbox("Select a dataset", list(dataset_options.keys()))

        if st.button("📄 Generate Report"):
            dataset_id = dataset_options[selected_name]

            # 3️⃣ Call backend to generate report
            res = get_report(dataset_id)

            if res is not None and res.status_code == 200:
                pdf_data = res.content
                pdf_filename = f"report_{dataset_id}.pdf"

                st.success("✅ Report generated successfully!")

                # 🟢 Use Streamlit download button
                st.download_button(
                    label="📥 Click to Download Report",
                    data=pdf_data,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )

                # 🟢 Show PDF inline preview
                base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.error(f"❌ Failed to generate report. Status code: {res.status_code}")
    else:
        st.warning("⚠️ No datasets found. Please upload one first.")
else:
    st.error("🚫 Could not fetch datasets.")
