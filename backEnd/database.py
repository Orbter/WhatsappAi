import os
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import psycopg2

load_dotenv() # Make sure to load your .env file

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

def get_connection():
    """Helper function to create database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def check_history(user_id):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM messages WHERE user_id = %s;", (user_id,))
        count = cur.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error checking history: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def create_history():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "users"(
                id SERIAL PRIMARY KEY,
                user_identifier VARCHAR(255) UNIQUE NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "user"(
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_name(
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                user_id INT NOT NULL,  -- <-- ADDED THIS
                CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES "user"(id) ON DELETE CASCADE
            );
        """) # Removed trailing comma

        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                is_from_bot BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT NOT NULL,  
                chat_id INT NOT NULL,  
                
                CONSTRAINT fk_chat FOREIGN KEY(chat_id) REFERENCES "chat_name"(id) ON DELETE CASCADE,
                CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES "user"(id) ON DELETE CASCADE
            );
        """) 
        
        conn.commit()
        print("Tables created successfully")
    except Exception as e:
        conn.rollback()
        print(f"Error creating tables: {e}")
    finally:
        cur.close()
        conn.close()

def get_or_create_chat(user_id, chat_name="New Chat"):
    """
    Finds a chat by name for a user, or creates a new one.
    Returns the chat_id.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "SELECT id FROM chat_name WHERE user_id = %s AND name = %s;", 
            (user_id, chat_name)
        )
        result = cur.fetchone()
        
        if result:
            return result[0]  
        else:
            cur.execute(
                "INSERT INTO chat_name (user_id, name) VALUES (%s, %s) RETURNING id;",
                (user_id, chat_name)
            )
            chat_id = cur.fetchone()[0]
            conn.commit()
            return chat_id
    except Exception as e:
        conn.rollback()
        print(f"Error getting/creating chat: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def get_user_chats(user_id):
    """Gets all chat sessions for a specific user."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "SELECT id, name FROM chat_name WHERE user_id = %s ORDER BY id DESC;",
            (user_id,)
        )
        chats = cur.fetchall()
        return chats  # Returns a list of (id, name) tuples
    except Exception as e:
        print(f"Error retrieving chats: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def insert_message(text, is_from_bot,created_at, user_id,chat_id):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            INSERT INTO messages (text, is_from_bot, created_at, user_id,chat_id) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id;
            """,
            (text, is_from_bot, created_at, user_id,chat_id)
        )





        message_id = cur.fetchone()[0]
        conn.commit()
        return message_id
    except Exception as e:
        conn.rollback()
        print(f"Error inserting message: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def get_user_messages(user_id,chat_id, limit=50):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            
            """
            SELECT id, text, is_from_bot, created_at 
            FROM messages 
            WHERE user_id = %s  
            WHERE chat_id = %s 
 
            ORDER BY created_at DESC 
            LIMIT %s;
            """,
            (user_id, chat_id, limit)
        )
        messages = cur.fetchall()
        return messages
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return []
    finally:
        cur.close()
        conn.close()


