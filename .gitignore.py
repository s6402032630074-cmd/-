import streamlit as st
import pandas as pd
from extractor import extract_data
from validator import validate_data

st.set_page_config(
    page_title="Concrete Test Validator",
    layout="wide"
)

st.title("Concrete Compressive Strength Validator")

uploaded_file = st.file_uploader(
    "Upload Report",
    type=["jpg","jpeg","png","pdf"]
)

if uploaded_file:

    data = extract_data(uploaded_file)

    st.subheader("OCR Result")

    no = st.text_input(
        "No.",
        value=data.get("No","")
    )

    date = st.text_input(
        "Date",
        value=data.get("Date","")
    )

    project = st.text_input(
        "Project",
        value=data.get("Project","")
    )

    location = st.text_input(
        "Location",
        value=data.get("Location","")
    )

    concrete_class = st.text_input(
        "Concrete Class",
        value=data.get("Concrete Class","")
    )

    slump = st.text_input(
        "Slump",
        value=data.get("Slump","")
    )

    age = st.text_input(
        "Age",
        value=data.get("Age","")
    )

    s1 = st.text_input(
        "Strength 1",
        value=data.get("Strength1","")
    )

    s2 = st.text_input(
        "Strength 2",
        value=data.get("Strength2","")
    )

    s3 = st.text_input(
        "Strength 3",
        value=data.get("Strength3","")
    )

    avg = st.text_input(
        "Average",
        value=data.get("Average","")
    )

    if st.button("Validate"):

        user_data = {
            "No": no,
            "Date": date,
            "Project": project,
            "Location": location,
            "Concrete Class": concrete_class,
            "Slump": slump,
            "Age": age,
            "Strength1": s1,
            "Strength2": s2,
            "Strength3": s3,
            "Average": avg
        }

        result = validate_data(
            data,
            user_data
        )

        st.dataframe(result)

        csv = result.to_csv(index=False)

        st.download_button(
            "Download CSV",
            csv,
            "result.csv",
            "text/csv"
        )
