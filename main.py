# main.py
import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from uuid import uuid4
from langchain.globals import set_verbose
from langchain_community.callbacks import get_openai_callback
import io
import re

from src.mcq_generator.utils import read_file, get_table_data
from src.mcq_generator.MCQGenerator import generate_and_evaluate_quiz
from src.mcq_generator.syllabus_data import SYLLABUS_DATA
from utils.supabase_pg import store_quiz_to_postgres

load_dotenv()
set_verbose(True)

# Load schema for formatting response
with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

st_key = "test"
st.title("MCQ Generator")
mode = st.radio("Choose input mode:", ["Upload PDF/TXT", "Choose from Syllabus"])

with st.form("user_inputs"):
    mcq_count = st.number_input("No of Questions", min_value=3, max_value=50)
    tone = st.text_input("Complexity level of Questions", max_chars=20, placeholder="Simple")
    input_key = st.text_input("Enter the secret key", max_chars=50, placeholder="Password")

    text = ""
    subject = ""

    if mode == "Upload PDF/TXT":
        uploaded_file = st.file_uploader("Upload a PDF or TXT file")
        if uploaded_file:
            try:
                text = read_file(uploaded_file)
                subject = st.text_input("Insert the Subject", max_chars=20)
            except Exception as e:
                st.error(f"Error reading file: {e}")
    else:
        year = st.selectbox("Select Year", list(SYLLABUS_DATA.keys()))
        semester = st.selectbox("Select Semester", list(SYLLABUS_DATA[year].keys()))
        course = st.selectbox("Select Subject", list(SYLLABUS_DATA[year][semester].keys()))
        unit = st.selectbox("Select Unit", list(SYLLABUS_DATA[year][semester][course].keys()))
        text = SYLLABUS_DATA[year][semester][course][unit]
        subject = course

    generate_button = st.form_submit_button("Create MCQs")

if generate_button and text and mcq_count and subject and tone:
    if input_key == st_key:
        with st.spinner("Generating MCQs..."):
            try:
                with get_openai_callback() as cb:
                    response = generate_and_evaluate_quiz({
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    })
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error during quiz generation.")
            else:
                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data:
                            # Split options into separate columns and clean labels like "a ->"
                            expanded_data = []
                            for idx, row in enumerate(table_data, 1):
                                options = row["Options"].split("||")
                                options_dict = {}
                                for i, opt in enumerate(options):
                                    opt_clean = re.sub(r"^[a-zA-Z]\s*[-–>→]\s*", "", opt.strip())
                                    options_dict[f"Option {chr(97+i)}"] = opt_clean

                                expanded_row = {
                                    "Serial No": idx,
                                    "Question": row["Question"],
                                    **options_dict,
                                    "Correct": row["Correct"]
                                }
                                expanded_data.append(expanded_row)

                            df = pd.DataFrame(expanded_data)
                            st.table(df)
                            st.text_area("Review", value=response.get("review", ""), height=200)

                            # Excel download
                            excel_buffer = io.BytesIO()
                            df.to_excel(excel_buffer, index=False, engine='openpyxl')
                            excel_buffer.seek(0)

                            st.download_button(
                                label="📥 Download MCQs as Excel",
                                data=excel_buffer,
                                file_name="generated_mcqs.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            # ---- PUBLISH SECTION ----
                            st.subheader("Publish Quiz")
                            test_name = st.text_input("Enter Test Name (used as table name in Supabase)")
                            publish_button = st.button("Publish")

                            if publish_button and test_name:
                                try:
                                    store_quiz_to_postgres(test_name, quiz)
                                    st.success(f"Quiz published to PostgreSQL table: {test_name}")
                                except Exception as e:
                                    st.error(f"Failed to publish quiz: {e}")
                        else:
                            st.error("Error formatting table data.")
                    else:
                        st.write(response)
    else:
        st.error("Wrong Password")




    