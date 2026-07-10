import os
import shutil
import tempfile
import zipfile

import pandas as pd
import streamlit as st

from test import process_pbip


st.set_page_config(
    page_title="PBIX Metadata Extractor",
    layout="wide"
)

st.title("PBIX Metadata Extractor")

uploaded_file = st.file_uploader(
    "Upload file .pbix",
    type=["pbix"]
)

if uploaded_file is not None:

    with st.spinner("Processing..."):

        temp_dir = tempfile.mkdtemp()

        pbix_path = os.path.join(
            temp_dir,
            uploaded_file.name
        )

        with open(pbix_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # rename pbix -> pbip (zip)
        pbip_path = pbix_path.replace(".pbix", ".pbip")

        os.rename(pbix_path, pbip_path)

        # extract
        extract_folder = os.path.join(
            temp_dir,
            "project"
        )

        os.makedirs(extract_folder, exist_ok=True)

        with zipfile.ZipFile(pbip_path, "r") as zip_ref:
            zip_ref.extractall(extract_folder)

        # jalankan parser
        excel_path = process_pbip(extract_folder)

    st.success("Finished!")

    df = pd.read_excel(excel_path)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    with open(excel_path, "rb") as f:

        st.download_button(
            label="Download Excel",
            data=f,
            file_name="dashcat.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    shutil.rmtree(temp_dir)