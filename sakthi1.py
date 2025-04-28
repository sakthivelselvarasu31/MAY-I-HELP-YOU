from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
import os
from werkzeug.utils import secure_filename

# Initialize Google GenAI
genai.configure(api_key="AIzaSyA8yDBn0Tnfihe-Xehoxq3qv8d1XOGtQwA")
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
chat = model.start_chat()

# Flask app
app = Flask(__name__)

# Only allow uploads inside the current directory
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Check if file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Medicine chatbot function
def chat_about_medicines(user_input):
    instruction = (
        "You are a medical assistant specialized in medicines and healthcare. "
        "Follow these rules strictly:\n"
        "1. Only answer questions related to medicines, healthcare, and medical conditions\n"
        "2. If the question is not medical-related, politely reply: 'I apologize, but I can only answer questions about medicines and healthcare.'\n"
        "3. Always provide accurate, evidence-based information\n"
        "4. Include relevant warnings about side effects when discussing medicines\n"
        "5. Recommend consulting a healthcare professional for specific medical advice\n"
        "6. Keep responses clear and concise\n"
        "User's question: " + user_input
    )
    try:
        response = chat.send_message(instruction)
        return response.text
    except Exception as e:
        return "I apologize, but I encountered an error. Please try again or rephrase your question."

# Dummy table image processing
def process_table_image(image_path, table_name):
    # Just simulating table processing
    return f"Processed table image: {table_name}"

# Serve the HTML directly
@app.route("/")
def index():
    return send_file("index1.html")

# API endpoint for chat
@app.route("/chat", methods=["POST"])
def chat_api():
    try:
        data = request.json
        user_input = data.get("message", "")
        if not user_input:
            return jsonify({"reply": "Please provide a question about medicines."})
        
        reply = chat_about_medicines(user_input)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "I apologize, but I encountered an error. Please try again."})

# API endpoint for uploading table images (stored temporarily in memory)
@app.route("/upload_table", methods=["POST"])
def upload_table():
    if 'table_image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['table_image']
    table_name = request.form.get('table_name', 'Unnamed Table')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(".", filename)  # Save to current directory
        file.save(filepath)

        result = process_table_image(filepath, table_name)

        # Optionally, delete the file after processing if you don't want to keep it
        os.remove(filepath)

        return jsonify({
            "message": "Table image uploaded and processed successfully",
            "table_name": table_name,
            "filename": filename,
            "result": result
        })

    return jsonify({"error": "Invalid file type"}), 400

if __name__ == "__main__":
    app.run(debug=True)
