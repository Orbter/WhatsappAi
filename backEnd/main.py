from fastapi import FastAPI



app = FastAPI()

@app.post("/chat")
async def handle_chat(message_data: dict):
    user_id = message_data.get("user_id")
    user_text = message_data.get("text")
    response_text = f"You said: {user_text}" 
    return {"user_id": user_id, "response": response_text}