from flask import Flask, request, render_template_string
import os
import whisper
from openai import OpenAI

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Create uploads folder
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Load Whisper model
model = whisper.load_model("base")

# 🔑 Replace with your OpenAI API Key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# ================== HTML INSIDE PYTHON ==================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Lecture Voice-to-Notes Generator</title>
    <style>
        body { font-family: Arial; padding: 30px; background: #f4f6f9; }
        h1 { color: #003366; }
        textarea { width: 100%; height: 150px; margin-bottom: 20px; }
        .box { background: white; padding: 20px; margin-top: 20px; border-radius: 10px; }
        button { padding: 10px 20px; background: #003366; color: white; border: none; border-radius: 5px; }
        input { margin-bottom: 15px; }
    </style>
</head>
<body>

<h1>🎤 Lecture Voice-to-Notes Generator</h1>

<form method="POST" enctype="multipart/form-data">
    <input type="file" name="audio" required>
    <br>
    <button type="submit">Generate Notes</button>
</form>

{% if transcript %}
<div class="box">
    <h2>📄 Transcript</h2>
    <textarea readonly>{{ transcript }}</textarea>
</div>

<div class="box">
    <h2>📝 Study Notes</h2>
    <textarea readonly>{{ notes }}</textarea>
</div>

<div class="box">
    <h2>❓ Quiz</h2>
    <textarea readonly>{{ quiz }}</textarea>
</div>

<div class="box">
    <h2>🧠 Flashcards</h2>
    <textarea readonly>{{ flashcards }}</textarea>
</div>
{% endif %}

</body>
</html>
"""

# ================== ROUTE ==================
@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    notes = ""
    quiz = ""
    flashcards = ""

    if request.method == "POST":
        audio = request.files["audio"]
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], audio.filename)
        audio.save(filepath)

        # 🎤 Speech to Text
        result = model.transcribe(filepath)
        transcript = result["text"]

        # 📝 Generate Notes
        notes_prompt = f"Summarize the following lecture into clear study notes:\n{transcript}"
        notes_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": notes_prompt}]
        )
        notes = notes_response.choices[0].message.content

        # ❓ Generate Quiz
        quiz_prompt = f"Create 5 quiz questions from this lecture:\n{transcript}"
        quiz_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": quiz_prompt}]
        )
        quiz = quiz_response.choices[0].message.content

        # 🧠 Generate Flashcards
        flash_prompt = f"Create 5 flashcards (Question-Answer format) from this lecture:\n{transcript}"
        flash_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": flash_prompt}]
        )
        flashcards = flash_response.choices[0].message.content

    return render_template_string(HTML,
                                  transcript=transcript,
                                  notes=notes,
                                  quiz=quiz,
                                  flashcards=flashcards)

# ================== RUN ==================
if __name__ == "__main__":
    app.run(debug=True)