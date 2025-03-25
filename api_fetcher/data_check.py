import sqlite3

db_path = "../dofus_items.sqlite3"  # Adjust path if needed

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT item_id FROM effects LIMIT 10;")  
    results = cursor.fetchall()

    for row in results:
        print(row[0])  # Print item_type column to check encoding

    conn.close()
except Exception as e:
    print(f"Error: {e}")
