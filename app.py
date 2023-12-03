from flask import Flask, render_template, request, jsonify
import os
import speech_recognition as sr
import openai
import pyttsx3

app = Flask(__name__)

def listen_and_recognize(recognizer, source, timeout_duration, language):
    try:
        audio = recognizer.listen(source, timeout=timeout_duration)
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results; {e}."
    except sr.WaitTimeoutError:
        return "No speech detected in the last 5 seconds."

def get_gpt_response(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are chatting with Boris, a friendly and easy-going virtual assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return str(e)

def speak(text, language_code):
    voices = tts_engine.getProperty('voices')
    selected_voice = next((voice for voice in voices if language_code in voice.name.lower()), voices[0])
    tts_engine.setProperty('voice', selected_voice.id)
    tts_engine.say(text)
    tts_engine.runAndWait()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize_speech', methods=['POST'])
def recognize_speech():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"})

    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "No selected audio file"})

    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file)
    with audio_file as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return jsonify({"recognized_text": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"})
    except sr.RequestError as e:
        return jsonify({"error": f"Could not request results; {e}"})

@app.route('/get_gpt_response', methods=['POST'])
def get_gpt_response_endpoint():
    prompt = request.form.get('prompt', '')

    if not prompt:
        return jsonify({"error": "No prompt provided"})

    language_code = request.form.get('language_code', 'en-US')

    gpt_response = get_gpt_response(prompt)
    speak(gpt_response, language_code)

    return render_template('index.html', gpt_response=gpt_response)

if __name__ == '__main__':
    tts_engine = pyttsx3.init()
    app.run(debug=True)
