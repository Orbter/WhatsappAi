from .connection import get_connection
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session

def get_or_create_app_user(user_identifier):
    """
    Input: user_identifier (str) -> e.g., "+97250..."
    Output: internal_user_id (int) -> e.g., 5
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM app_users WHERE user_identifier = %s;", (user_identifier,))
        result = cur.fetchone()
        if result:
            return result[0] 
        else:
            cur.execute(
                "INSERT INTO app_users (user_identifier) VALUES (%s) RETURNING id;",
                (user_identifier,)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
    except Exception as e:
        conn.rollback()
        print(f"Error in get_or_create_app_user: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

def get_user_google_creds(user_id,service_name='google_calendar'):
    """
    Check if we have tokens for this internal user ID
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT access_token, refresh_token, scopes 
            FROM user_credentials 
            WHERE user_id = %s AND service_name = %s;
            """, (user_id,service_name)
        )
        result = cur.fetchone()
        if result:
             return {
                'access_token': result[0],
                'refresh_token': result[1],
                'scopes': result[2]
            }
        return None
    except Exception as e:
        print(f"Error fetching creds: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def get_or_create_chat(user_id, chat_name="New Chat"):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        
        cur.execute(
            "SELECT id FROM chat_sessions WHERE user_id = %s AND session_name = %s;", 
            (user_id, chat_name)
        )
        result = cur.fetchone()
        
        if result:
            return result[0]  
        else:
            cur.execute(
                "INSERT INTO chat_sessions (user_id, session_name) VALUES (%s, %s) RETURNING id;",
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
            "SELECT id, session_name FROM chat_sessions WHERE user_id = %s ORDER BY id DESC;",
            (user_id,)
        )
        chats = cur.fetchall()
        return chats 
    except Exception as e:
        print(f"Error retrieving chats: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_chat_history_as_text(chat_id, limit=10):
    """
    Fetches DB messages and formats them for Gemini context
    Fixed to return [{"text": "message"}] instead of ["message"]
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT is_from_bot, text 
            FROM messages 
            WHERE chat_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s;
        """, (chat_id, limit))
        
        rows = cur.fetchall()
        rows.reverse() 
        
        history = []
        for is_bot, text in rows:
            role = "model" if is_bot else "user"
            history.append({
                "role": role, 
                "parts": [{"text": text}] 
            })
            
        return history
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
            WHERE user_id = %s AND chat_id = %s
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
