import os
from app import init_db, process_all_csv_files

def initialize():
    print("Initializing database...")
    init_db()
    print("Processing CSV files...")
    process_all_csv_files()
    with open('db_initialized.flag', 'w') as flag_file:
        flag_file.write('Database initialized')
    print("Database initialized and CSV files processed.")

if __name__ == '__main__':
    initialize()