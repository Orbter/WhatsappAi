from connection import get_connection
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session

def get_or_create_user(google_id, email, name, email_verified):
    """
    Find user by google_id, or create if doesn't exist.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "SELECT id FROM users WHERE google_id = %s;",
            (google_id,)
        )
        result = cur.fetchone()
        
        if result:
            user_id = result[0]
            cur.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s;",
                (user_id,)
            )
            conn.commit()
            return user_id
        else:
            cur.execute(
                """
                INSERT INTO users (google_id, email, name, email_verified, last_login)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id;
                """,
                (google_id, email, name, email_verified)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            return user_id
            
    except Exception as e:
        conn.rollback()
        print(f"Error in get_or_create_user: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def get_user_credentials(user_id, service_name='google_calendar'):
    """
    Retrieve OAuth credentials for a user.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            SELECT access_token, refresh_token, token_expiry, scopes
            FROM user_credentials
            WHERE user_id = %s AND service_name = %s;
            """,
            (user_id, service_name)
        )
        result = cur.fetchone()
        
        if result:
            import json
            return {
                'access_token': result[0],
                'refresh_token': result[1],
                'token_expiry': result[2],
                'scopes': json.loads(result[3]) if result[3] else []
            }
        return None
        
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None
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
