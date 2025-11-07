import json


def load_history(fileName):
    """Loads the history from a json file... lol didn't learned SQL yet"""
    try:
        with open(fileName, 'r') as prev:
            chat_history = json.load(prev)
    except FileNotFoundError:
        chat_history =[]
        with open(fileName, 'w') as current:
            json.dump(chat_history, current, indent=4)
    except json.JSONDecodeError:
        chat_history = []
    return chat_history

def save_history(fileName, history):
    """Saves chat history to a JSON file."""
    try:
        existing_history = load_history(fileName)
        
        existing_history.append(history)
        
        with open(fileName, 'w') as current:
            json.dump(existing_history, current, indent=4)
        print("Chat history saved.")
    except Exception as e:
        print(f"Error saving chat history: {e}")