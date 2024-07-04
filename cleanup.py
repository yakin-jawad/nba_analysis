import sqlite3

"""
cleanup.py

This script was mainly used to delete databases once they're no longer useful or if they have been made
redunant by the existence of newer databases.
"""

# Connects to the database.
conn = sqlite3.connect('nba_database.db')

# Replace table_name with the name of the database table
conn.execute('''DROP TABLE [IF EXISTS] table_name''')