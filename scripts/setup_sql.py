import sqlite3
import os

DB_PATH = "data/ai_models.db"

def create_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            release_year INTEGER,
            parameter_count TEXT,
            organization TEXT,
            sota_benchmark TEXT
        )
    ''')
    
    # Insert sample data
    models_data = [
        ("GPT-3", 2020, "175B", "OpenAI", "Few-shot learning"),
        ("GPT-4", 2023, "Unknown (Est. 1.76T)", "OpenAI", "MMLU"),
        ("Llama 2", 2023, "70B", "Meta", "Open Source Chat"),
        ("Claude 3 Opus", 2024, "Unknown", "Anthropic", "Reasoning"),
        ("Mixtral 8x7B", 2023, "47B", "Mistral AI", "Efficiency"),
        ("Gemini 1.5 Pro", 2024, "Unknown", "Google", "Long Context"),
        ("BERT", 2018, "340M", "Google", "GLUE"),
        ("T5", 2019, "11B", "Google", "Translation"),
        ("Falcon 180B", 2023, "180B", "TII", "Open Source"),
        ("Mistral 7B", 2023, "7B", "Mistral AI", "Small Model Performance")
    ]
    
    cursor.executemany('''
        INSERT INTO models (model_name, release_year, parameter_count, organization, sota_benchmark)
        VALUES (?, ?, ?, ?, ?)
    ''', models_data)
    
    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH} with {len(models_data)} records.")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    create_db()
