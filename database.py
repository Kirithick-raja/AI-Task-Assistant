import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    """Open a new connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "ai_task_assistant")
        )
        return connection
    except Error as e:
        print(f"Database connection failed: {e}")
        raise
