from .connection import get_connection
import json

def save_user_google_creds(user_id, service_name, access_token, refresh_token, token_expiry, scopes):
    """
    Saves or updates Google OAuth credentials in the database.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO user_credentials (user_id, service_name, access_token, refresh_token, token_expiry, scopes)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, service_name) 
            DO UPDATE SET 
            access_token = EXCLUDED.access_token,
            refresh_token = EXCLUDED.refresh_token,
            token_expiry = EXCLUDED.token_expiry,
            scopes = EXCLUDED.scopes;
            """,
            (user_id, service_name, access_token, refresh_token, token_expiry, scopes)
        )

        conn.commit()
        print(f"✅ Saved credentials for {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving creds: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def insert_message(text, is_from_bot, user_id, chat_id):
    """
    Saves a message to the 'messages' table.
    Links to both the user (app_users) and the specific session (chat_sessions).
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            INSERT INTO messages (text, is_from_bot, user_id, chat_id, created_at) 
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) 
            RETURNING id;
            """,
            (text, is_from_bot, user_id, chat_id)
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