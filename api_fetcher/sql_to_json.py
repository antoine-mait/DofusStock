import sqlite3
import json

def sqlite_to_json(db_path):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Dictionary to store all data
    database_data = {}

    # Iterate through each table
    for table_name in tables:
        table_name = table_name[0]
        
        # Fetch all rows from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        # Convert rows to list of dictionaries
        rows = []
        for row in cursor.fetchall():
            # Create a dictionary for each row
            row_dict = dict(zip(column_names, row))
            rows.append(row_dict)
        
        # Add to main dictionary
        database_data[table_name] = rows

    # Close connection
    conn.close()

    # Return JSON string
    return json.dumps(database_data, indent=2, ensure_ascii=False)

# Usage
try:
    # Path to your SQLite database
    db_path = '../dofus_items.sqlite3'
    
    # Convert to JSON
    json_data = sqlite_to_json(db_path)
    
    # Optional: Write to a file
    with open('dofus_items.json', 'w', encoding='utf-8') as f:
        f.write(json_data)


except Exception as e:
    print(f"An error occurred: {e}")