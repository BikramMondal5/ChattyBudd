# 🤖🧠 ChattyBudd

ChattyBudd is an interactive WhatsApp bot powered by Google's Gemini AI. It allows you to have natural conversations, generate images, and get coding help right from your WhatsApp. The bot responds to plain English text and provides helpful, context-aware responses.

## 🌟 Features
- 💬 Real-time AI-powered chat via WhatsApp
- 🖼️ Image generation (use /image command)
- 💻 Code generation capabilities
- 🧠 Intelligent and context-aware responses using Gemini AI
- 🌐 Google Search integration
- 💬 Accessible directly through WhatsApp

## 🛠️ Technologies Used
- Python 3
- Flask (for webhook server)
- Twilio (for WhatsApp integration)
- Google Gemini AI (for chat, code, and image generation)
- Gemini 2.5 Flash (for conversations)
- Gemini 2.0 Flash Image Generation

## ⚙️ Installation

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/BikramMondal5/ChattyBudd.git
   cd ChattyBudd
   ```
2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   Create a `.env` file with the following:
   ```
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_WHATSAPP_NUMBER=your_twilio_whatsapp_number
   GEMINI_API_KEY=your_gemini_api_key
   ```

## 🚀 How to Use

1. **Start the application:**
   ```powershell
   python app.py
   ```
2. **Set up Twilio webhook:**
   - Make your server publicly accessible (using ngrok or similar)
   - Configure your Twilio WhatsApp Sandbox to point to your webhook URL
   
3. **Chat via WhatsApp:**
   - Send messages to your configured Twilio WhatsApp number
   - For image generation, send: `/image [your description]`

## 🤝 Contribution

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
