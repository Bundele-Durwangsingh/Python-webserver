import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="mysql-204495-0.cloudclusters.net",
        port=10067,
        user="admin",
        password="1cuKzP4Q",
        database="todos_db"
    )
    return connection

def init_db():
    # Create database if not exists
    root_conn = mysql.connector.connect(
        host="mysql-204495-0.cloudclusters.net",
        port=10067,
        user="admin",
        password="1cuKzP4Q"
    )
    root_cursor = root_conn.cursor()
    root_cursor.execute("CREATE DATABASE IF NOT EXISTS todos_db")
    root_cursor.close()
    root_conn.close()

    # Connect to todos_db
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if 'todo' table exists
    cursor.execute("SHOW TABLES LIKE 'todo'")
    table_exists = cursor.fetchone()

    # Create table if it doesn’t exist
    if not table_exists:
        cursor.execute("""
            CREATE TABLE todo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task VARCHAR(255) NOT NULL,
                status BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()

    cursor.close()
    conn.close()

def init_user_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'user'")
    table_exists = cursor.fetchone()

    if not table_exists:
        cursor.execute("""
            CREATE TABLE user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()

    cursor.close()
    conn.close()
