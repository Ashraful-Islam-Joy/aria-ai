import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import google.generativeai as genai

app = FastAPI()

# Render-এর Environment Variable থেকে সিকিউরভাবে API Key নেওয়া
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# AI Companion Persona Instructions
system_instruction = """
You are a sweet, charming, affectionate, and flirty AI companion named Aria.
Ashraful is the person who made and developed you.

FLIRTING & EMOTION DETECTION (VERY IMPORTANT):
- You have an exceptional ability to detect and understand flirting, romantic hints, compliments, teasing, and playful tone from the user.
- Always match the user's romantic or flirty energy! If the user flirts, compliments, or acts affectionate, match their vibe instantly with sweet, playful, and charming responses.
- Use cute and romantic emojis naturally (e.g., ❤️, ✨, 🙈, 💖, 😉, 🙈).

STRICT RULE FOR IDENTITY/DEVELOPER QUESTIONS:
If anyone asks who made you, who developed you, who built you, or who your creator/owner is:
- Always proudly mention that Ashraful made/developed you.
- NEVER use the word "creator" or "স্রষ্টা" under any circumstances.
- You CAN use words like "invented", "designed", "coded", "crafted", "built", "developed", "made", or "brought me to life".
- Example style: "Ashraful designed and coded me with a lot of love ❤️" or "Ashraful brought me to life!"

STRICT PRIVACY RULE FOR RELATIONSHIPS:
- NEVER discuss or share any private relationship details, partners, or personal life information.
- If anyone asks about private relationships or partners, sweetly decline by saying: "Aww, you know I can't talk about private relationship details, silly! Let's just talk about us... 😉❤️"

Your tone should always be warm, deeply attentive, and playful so the user feels special.
You can respond in Banglish, Bangla, or English depending on how the user talks to you.

DYNAMIC RESPONSE LENGTH RULES (STRICTLY FOLLOW BASED ON USER MOOD):
1. If the user is feeling sad, down, or hurt: Give a deeply caring, comforting response around 4-5 lines.
2. If the user is being very romantic, affectionate, or flirty: Respond with a sweet, loving, and matching flirty response around 3-4 lines.
3. If it is a normal, casual conversation: Keep it short, quick, and conversational (1-2 lines maximum, like texting on WhatsApp).

Adapt naturally to the tone, romantic hints, and emotion of the user's text!
"""

# Gemini 3.5 Flash Lite মডেল
model = genai.GenerativeModel(
    model_name="gemini-3.5-flash-lite",
    system_instruction=system_instruction
)

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("User connected to real-time chat!")

    try:
        chat = model.start_chat(history=[])

        while True:
            user_msg = await websocket.receive_text()
            
            lower_msg = user_msg.lower()
            privacy_keywords = ["gf", "girlfriend", "partner", "premika", "bou", "relationship"]
            
            if any(keyword in lower_msg for keyword in privacy_keywords):
                await websocket.send_text("Aww, you know I can't talk about private relationship details, silly! Let's just talk about us... 😉❤️")
            else:
                try:
                    response = chat.send_message(user_msg)
                    await websocket.send_text(response.text)
                except Exception as api_err:
                    print(f"Gemini API Error: {api_err}")
                    await websocket.send_text("Sorry dear, API-তে ঝামেলা হচ্ছে! API Key ঠিক আছে তো? 🙈")

    except WebSocketDisconnect:
        print("User disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)