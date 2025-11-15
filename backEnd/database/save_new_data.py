from connection import get_connection
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session

def save_user_credentials(user_id, service_name, access_token, refresh_token, token_expiry, scopes):
    """
    Save or update OAuth credentials for a user.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        import json
        scopes_json = json.dumps(scopes) if isinstance(scopes, list) else scopes
        
        cur.execute(
            """
            INSERT INTO user_credentials 
                (user_id, service_name, access_token, refresh_token, token_expiry, scopes, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, service_name) 
            DO UPDATE SET
                access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                token_expiry = EXCLUDED.token_expiry,
                scopes = EXCLUDED.scopes,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (user_id, service_name, access_token, refresh_token, token_expiry, scopes_json)
        )
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error saving credentials: {e}")
        return False
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