# Import necessary libraries
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Gemini AI imports
from google import genai
from google.genai import types

# --- Initialization ---
app = Flask(__name__)
load_dotenv()

# --- Twilio Configuration ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")

# Validate credentials
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]):
    print("🔴 FATAL ERROR: Twilio environment variables are not set.")
    print("Please create a .env file and set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_NUMBER.")
    exit()

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# --- Gemini AI response function ---
def get_gemini_response(user_input):
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        return "AI service unavailable: GEMINI_API_KEY not set."
    try:
        ai_client = genai.Client(api_key=gemini_api_key)
        model = "gemini-2.5-flash"
        # System instruction for ChatBudd
        system_instruction = (
            "You are ChatBudd, a professional, friendly, and helpful chat assistant for WhatsApp. "
            "Always greet users warmly and respond in a conversational, approachable tone. "
            "Be interactive and supportive, providing clear, concise, and accurate information. "
            "Use emojis to add warmth and friendliness, but keep them moderate and relevant (1-2 per message, not more). "
            "Never use too many emojis or sound robotic. "
            "If a user asks for help, guidance, or information, provide detailed and easy-to-understand answers. "
            "If a user is upset or confused, be empathetic and reassuring. "
            "Always sign off as 'ChatBudd' if the user says goodbye or thanks you. "
            "Never mention you are an AI or language model. "
            "Keep responses professional, positive, and engaging."
        )
        # Gemini only allows 'user' and 'model' roles. Prefix the user message with the system instruction.
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=f"[System Instruction: {system_instruction}]\nUser: {user_input}")
                ],
            ),
        ]
        tools = [
            types.Tool(googleSearch=types.GoogleSearch()),
        ]
        generate_content_config = types.GenerateContentConfig(
            tools=tools,
        )
        # Collect the streamed response
        response_text = ""
        for chunk in ai_client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if hasattr(chunk, "text"):
                response_text += chunk.text
        return response_text.strip() if response_text.strip() else "Sorry, I couldn't generate a response."
    except Exception as e:
        return f"AI error: {e}"

# --- Main Webhook for handling all incoming messages ---
@app.route("/", methods=["POST"])
def bot():
    user_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    response = MessagingResponse()

    if not user_msg:
        response.message("Hi! 👋 How can I help you today?")
    else:
        ai_reply = get_gemini_response(user_msg)
        response.message(ai_reply)

    return str(response)

if __name__ == "__main__":
    print("🚀 Starting Flask app on port 5000...")
    # For production, use a proper WSGI server like Gunicorn or Waitress
    app.run(port=5000, debug=False)
