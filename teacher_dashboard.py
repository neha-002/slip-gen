import streamlit as st
from utils.supabase_client import get_all_quizzes, get_submissions_by_quiz
import pandas as pd

st.title("Teacher Dashboard")

quizzes = get_all_quizzes().data
quiz_ids = [q["quiz_id"] for q in quizzes]

if quiz_ids:
    selected_quiz = st.selectbox("Select a Quiz ID", quiz_ids)
    submissions = get_submissions_by_quiz(selected_quiz).data

    if submissions:
        df = pd.DataFrame(submissions)
        df = df[["roll_number", "student_name", "score"]]
        df.columns = ["Roll Number", "Name", "Score"]
        st.dataframe(df)
    else:
        st.warning("No submissions yet.")
else:
    st.info("No quizzes published yet.")
