import sqlite3

conn = sqlite3.connect('data/ai_models.db')
cursor = conn.cursor()

# Get count
cursor.execute('SELECT COUNT(*) FROM models')
count = cursor.fetchone()[0]
print(f'SQL Database: {count} AI models\n')

# Get sample
print('Sample models:')
cursor.execute('SELECT model_name, release_year, parameter_count FROM models LIMIT 5')
for row in cursor.fetchall():
    print(f'  - {row[0]} ({row[1]}): {row[2]} params')

conn.close()
