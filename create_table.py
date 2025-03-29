import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dofustock_project.settings')  
django.setup()

from django.db import connections

def create_craft_lists_table():
    with connections['dofus_items'].cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS craft_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (id) DEFERRABLE INITIALLY DEFERRED,
            FOREIGN KEY (user_id) REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED
        );
        ''')
        print("craft_lists table created successfully")

if __name__ == "__main__":
    create_craft_lists_table()