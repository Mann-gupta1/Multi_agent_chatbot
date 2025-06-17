import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

def init_db():
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    user_query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    agent_name VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
    finally:
        connection_pool.putconn(conn)

def save_chat(user_query, response, agent_name):
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_history (user_query, response, agent_name) VALUES (%s, %s, %s)",
                (user_query, response, agent_name)
            )
            conn.commit()
    finally:
        connection_pool.putconn(conn)

def get_chat_history():
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_query, response, agent_name FROM chat_history ORDER BY timestamp DESC LIMIT 10")
            return [{"user_query": row[0], "response": row[1], "agent_name": row[2]} for row in cur.fetchall()]
    finally:
        connection_pool.putconn(conn)