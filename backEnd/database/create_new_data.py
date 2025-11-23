from .connection import get_connection

def create_history():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. App Users
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_users(
                id SERIAL PRIMARY KEY,
                user_identifier VARCHAR(255) UNIQUE NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions(
                id SERIAL PRIMARY KEY,
                session_name TEXT NOT NULL,
                user_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES app_users(id) ON DELETE CASCADE
            );
        """) 

        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                is_from_bot BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT NOT NULL,  
                chat_id INT NOT NULL,  
                
                CONSTRAINT fk_chat FOREIGN KEY(chat_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
                CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES app_users(id) ON DELETE CASCADE
            );
        """) 
        
        # 4. User Credentials
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_credentials(
                user_id INT NOT NULL,
                service_name VARCHAR(50) NOT NULL,
                access_token TEXT,
                refresh_token TEXT,
                token_expiry TIMESTAMP,
                scopes TEXT, 
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, service_name),
                CONSTRAINT fk_cred_user FOREIGN KEY(user_id) REFERENCES app_users(id) ON DELETE CASCADE
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