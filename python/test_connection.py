import psycopg2
from config import DB_CONFIG

try:
    conn = psycopg2.connect(**DB_CONFIG)

    print("=" * 60)
    print("Connected successfully!")
    print("=" * 60)

    cursor = conn.cursor()

    cursor.execute("SELECT current_database();")
    print("Database :", cursor.fetchone()[0])

    cursor.execute("SELECT current_schema();")
    print("Schema   :", cursor.fetchone()[0])

    cursor.execute("SELECT version();")
    print("\nPostgreSQL Version:")
    print(cursor.fetchone()[0])

    cursor.close()
    conn.close()

    print("\nConnection closed.")

except Exception as e:
    print("Connection failed!")
    print(e)