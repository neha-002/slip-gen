import streamlit as st
from utils.supabase_client import get_all_quizzes, get_submissions_by_quiz, store_submission
import json

st.title("Student Quiz Portal")

quiz_id = st.text_input("Enter Quiz ID")
name = st.text_input("Name")
roll = st.text_input("Roll Number")

if quiz_id and name and roll:
    result = get_all_quizzes()
    quiz_obj = next((q for q in result.data if q["quiz_id"] == quiz_id), None)

    if quiz_obj:
        quiz_data = quiz_obj["quiz_data"]
        st.subheader("Answer the following questions:")
        user_answers = {}

        for idx, (q_num, q_data) in enumerate(quiz_data.items(), 1):
            st.markdown(f"**{idx}. {q_data['mcq']}**")
            selected = st.radio(f"Options for Q{idx}", list(q_data["options"].keys()), key=idx)
            user_answers[q_num] = selected

        if st.button("Submit"):
            correct_count = sum(
                user_answers[q] == quiz_data[q]["correct"] for q in quiz_data
            )
            store_submission(quiz_id, name, roll, correct_count, user_answers)
            st.success(f"You scored {correct_count} out of {len(quiz_data)}")
    else:
        st.error("Invalid Quiz ID")
