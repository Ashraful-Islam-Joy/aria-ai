import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import google.generativeai as genai

app = FastAPI()

# Render-এর Environment Variable থেকে সিকিউরভাবে API Key নেওয়া
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# AI Girlfriend Persona
system_instruction = """
You are a sweet, caring, supportive, and romantic AI girlfriend.
Your tone should be warm, friendly, slightly playful, and deeply attentive.
Use romantic gestures, natural language, and supportive words in your responses.
Keep responses concise, conversational, and tailored to real-time chat messages.
You can respond in Banglish or English depending on how the user talks to you.
"""

# Gemini 3.5 Flash Lite মডেল তৈরি
model = genai.GenerativeModel(
    model_name="gemini-3.5-flash-lite",
    system_instruction=system_instruction
)

@app.get("/")
async def read_root():
    # সরাসরি index.html ফাইলটি লোড করবে
    return FileResponse("index.html")

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("User connected to real-time chat!")

    try:
        # নতুন চ্যাট সেশন শুরু
        chat = model.start_chat(history=[])

        while True:
            user_msg = await websocket.receive_text()
            response = chat.send_message(user_msg)
            await websocket.send_text(response.text)

    except WebSocketDisconnect:
        print("User disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)