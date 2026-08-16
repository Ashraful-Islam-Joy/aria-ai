import os
import requests
import base64
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import google.generativeai as genai

app = FastAPI()

# আপনার আসল Gemini API Key টি এখানে ইনভার্টেড কমার ভেতরে বসান
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=API_KEY)

# ElevenLabs Credentials
ELEVENLABS_API_KEY = "sk_45333d10598c8e3fb8b74b1feb543c24bfc5b910a45db357"
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel Voice

def generate_voice_audio(text: str):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        print(f"ElevenLabs API Error: {e}")
    return None

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

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
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
                ai_text = "Aww, you know I can't talk about private relationship details, silly! Let's just talk about us... 😉❤️"
            else:
                try:
                    response = chat.send_message(user_msg)
                    ai_text = response.text
                except Exception as api_err:
                    print(f"Gemini API Error: {api_err}")
                    ai_text = "Sorry dear, API-তে ঝামেলা হচ্ছে! API Key ঠিক আছে তো? 🙈"

            audio_base64 = generate_voice_audio(ai_text)

            payload = {
                "text": ai_text,
                "audio": audio_base64
            }
            await websocket.send_text(json.dumps(payload))

    except WebSocketDisconnect:
        print("User disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)