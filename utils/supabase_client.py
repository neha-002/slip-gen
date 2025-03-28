# utils/supabase_client.py
from supabase import create_client, Client

SUPABASE_URL = "https://uopfrdpszvotitfofzza.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVvcGZyZHBzenZvdGl0Zm9menphIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMxNzIwOTMsImV4cCI6MjA1ODc0ODA5M30.olNsZ2xA_qXmI-EsbyxULre53WgtZeqt7S9YGqx_IPY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_quiz(quiz_id, quiz_data):
    return supabase.table("quizzes").insert({"quiz_id": quiz_id, "quiz_data": quiz_data}).execute()

def store_quiz_table(test_name: str, quiz: dict):
    rows = []
    for key, value in quiz.items():
        rows.append({
            "question": value["mcq"],
            "options": value["options"],
            "correct": value["correct"]
        })
    
    # Ensure table exists
    create_table_sql = f'''
    CREATE TABLE IF NOT EXISTS "{test_name}" (
        id SERIAL PRIMARY KEY,
        question TEXT,
        options JSONB,
        correct TEXT
    );
    '''
    supabase.rpc("execute_sql", {"sql": create_table_sql}).execute()
    
    # Insert rows
    for row in rows:
        supabase.table(test_name).insert(row).execute()


def store_submission(quiz_id, student_name, roll_number, score, answers):
    return supabase.table("submissions").insert({
        "quiz_id": quiz_id,
        "student_name": student_name,
        "roll_number": roll_number,
        "score": score,
        "answers": answers
    }).execute()

def get_all_quizzes():
    return supabase.table("quizzes").select("*").execute()

def get_submissions_by_quiz(quiz_id):
    return supabase.table("submissions").select("*").eq("quiz_id", quiz_id).execute()
