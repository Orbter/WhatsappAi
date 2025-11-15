from connection import get_connection
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session


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


def is_token_valid(user_id, service_name='google_calendar'):
    """
    Check if stored token is still valid (not expired).
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            SELECT token_expiry > CURRENT_TIMESTAMP as is_valid
            FROM user_credentials
            WHERE user_id = %s AND service_name = %s;
            """,
            (user_id, service_name)
        )
        result = cur.fetchone()
        return result[0] if result else False
        
    except Exception as e:
        print(f"Error checking token validity: {e}")
        return False
    finally:
        cur.close()
        conn.close()
