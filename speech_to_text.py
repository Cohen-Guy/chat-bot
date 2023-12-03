import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import openai
import os
import pyttsx3

# Function to listen and recognize speech
def listen_and_recognize(recognizer, source, timeout_duration, language):
    try:
        audio = recognizer.listen(source, timeout=timeout_duration)
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return "Could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results; {e}"
    except sr.WaitTimeoutError:
        return "No speech detected in the last 5 seconds"

# Function to get a conversational response from OpenAI's GPT, with the assistant named Boris
def get_gpt_response(prompt):
    api_key = os.getenv("OPENAI_API_KEY")  # Using environment variable for API key
    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are chatting with Boris, a friendly and easy-going virtual assistant who gives brief and casual responses."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return str(e)

# Function to speak text using TTS
def speak(text, language_code):
    # Set the voice based on the language
    voices = tts_engine.getProperty('voices')
    if language_code == 'he-IL':
        hebrew_voice = next((voice for voice in voices if 'hebrew' in voice.name.lower()), None)
        if hebrew_voice:
            tts_engine.setProperty('voice', hebrew_voice.id)
        else:
            tts_engine.setProperty('voice', voices[0].id)  # Default voice
    else:
        tts_engine.setProperty('voice', voices[0].id)  # Default voice

    tts_engine.say(text)
    tts_engine.runAndWait()

# Function to start speech recognition
def start_recognition():
    language = 'he-IL' if lang_var.get() == 1 else 'en-US'
    timeout_duration = 5  # This can be made configurable
    text.delete(1.0, tk.END)
    text.insert(tk.END, "Listening...\n")

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognized_text = listen_and_recognize(recognizer, source, timeout_duration, language)
        text.insert(tk.END, recognized_text + '\n')

# Function to send text to GPT and display response
def send_to_gpt():
    language_code = 'he-IL' if lang_var.get() == 1 else 'en-US'
    prompt = text.get("1.0", tk.END).strip()
    if prompt:
        gpt_response = get_gpt_response(prompt)
        text.insert(tk.END, "\nBoris:\n" + gpt_response + '\n')
        speak(gpt_response, language_code)  # Speak out the GPT response

# Main function to run the GUI
def main():
    global tts_engine, lang_var, text

    root = tk.Tk()
    root.title("Speech Recognition and GPT Response with Boris")

    lang_var = tk.IntVar(value=2)  # Default to English
    hebrew_button = tk.Radiobutton(root, text="Hebrew", variable=lang_var, value=1)
    english_button = tk.Radiobutton(root, text="English", variable=lang_var, value=2)
    start_button = tk.Button(root, text="Start Listening", command=start_recognition)
    gpt_button = tk.Button(root, text="Send to GPT", command=send_to_gpt)
    text = scrolledtext.ScrolledText(root, wrap=tk.WORD)

    hebrew_button.pack()
    english_button.pack()
    start_button.pack()
    gpt_button.pack()
    text.pack(fill=tk.BOTH, expand=True)

    tts_engine = pyttsx3.init()

    root.mainloop()

if __name__ == "__main__":
    main()
