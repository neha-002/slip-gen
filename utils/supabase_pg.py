# utils/supabase_pg.py

import psycopg2
import os
from psycopg2.extras import Json

DATABASE_URL = "postgresql://postgres:Project@123@db.uopfrdpszvotitfofzza.supabase.co:5432/postgres"

def store_quiz_to_postgres(test_name, quiz_data):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{test_name}" (
            id SERIAL PRIMARY KEY,
            question TEXT,
            options JSONB,
            correct TEXT
        );
    """)

    # Insert each MCQ
    for qid, entry in quiz_data.items():
        question = entry["mcq"]
        options = entry["options"]
        correct = entry["correct"]
        cursor.execute(
            f'INSERT INTO "{test_name}" (question, options, correct) VALUES (%s, %s, %s);',
            (question, Json(options), correct)
        )

    conn.commit()
    cursor.close()
    conn.close()
