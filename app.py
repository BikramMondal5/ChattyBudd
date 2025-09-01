# Import necessary libraries
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
from flask import send_from_directory, url_for

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

# --- Gemini Image Generation function ---
import mimetypes
import base64
def generate_gemini_image(prompt, file_prefix="generated_image"):
    # Ensure images directory exists
    images_dir = os.path.join(os.getcwd(), "images")
    os.makedirs(images_dir, exist_ok=True)
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        return None, "AI service unavailable: GEMINI_API_KEY not set."
    try:
        ai_client = genai.Client(api_key=gemini_api_key)
        model = "gemini-2.0-flash-preview-image-generation"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )
        file_index = 0
        image_filenames = []
        text_response = ""
        for chunk in ai_client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue
            part = chunk.candidates[0].content.parts[0]
            if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
                inline_data = part.inline_data
                data_buffer = part.inline_data.data
                file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"
                file_name = f"{file_prefix}_{file_index}{file_extension}"
                file_path = os.path.join(images_dir, file_name)
                with open(file_path, "wb") as f:
                    f.write(data_buffer)
                image_filenames.append(file_name)
                file_index += 1
            elif hasattr(chunk, "text") and chunk.text:
                text_response += chunk.text
        if image_filenames:
            return image_filenames, text_response.strip()
        else:
            return None, text_response.strip() or "Sorry, I couldn't generate an image."
    except Exception as e:
        return None, f"AI error: {e}"


# --- Main Webhook for handling all incoming messages ---
@app.route("/", methods=["POST"])
def bot():
    user_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    response = MessagingResponse()

    if not user_msg:
        response.message("Hi! 👋 How can I help you today?")
    elif user_msg.lower().startswith("/image"):
        # Extract prompt after '/image'
        prompt = user_msg[6:].strip()
        if not prompt:
            response.message("Please provide a description for the image you want me to generate after /image.")
        else:
            filenames, text_response = generate_gemini_image(prompt)
            if filenames:
                # Serve the image via Flask static route and send as WhatsApp media
                image_url = url_for('serve_image', filename=filenames[0], _external=True)
                response.message().media(image_url)
            if text_response:
                response.message(text_response)
            elif not filenames:
                response.message("Sorry, I couldn't generate an image.")
    else:
        ai_reply = get_gemini_response(user_msg)
        response.message(ai_reply)

    return str(response)


# Route to serve generated images
@app.route('/images/<path:filename>')
def serve_image(filename):
    images_dir = os.path.join(os.getcwd(), "images")
    return send_from_directory(images_dir, filename)

if __name__ == "__main__":
    app.run()
