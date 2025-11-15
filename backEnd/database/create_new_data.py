from connection import get_connection
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session


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
                name VARCHAR(255) NOT NULL,
                email_address VARCHAR(255) NOT NULL
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
