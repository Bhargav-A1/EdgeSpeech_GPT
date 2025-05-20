import os
import time
import json
import sounddevice as sd
import pyttsx3
import openai
from vosk import Model, KaldiRecognizer
from apikey import api_key

# Setup
openai.api_key = api_key

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# Load Vosk offline model
model_path = os.path.join(os.getcwd(), "model")
if not os.path.exists(model_path):
    raise FileNotFoundError("'model' folder not found.")

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

def record_audio(duration=5):
    print(f"\n Listening for {duration} seconds...")
    audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype='int16')
    for i in range(duration):
        time.sleep(1)
        print(f" {i+1}", end='', flush=True)
    sd.wait()
    print("\n Recording complete.")
    return audio

def transcribe_audio(audio):
    if recognizer.AcceptWaveform(audio.tobytes()):
        result = json.loads(recognizer.Result())
        return result.get("text", "")
    return ""

def get_chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

#  Main Loop
if __name__ == "__main__":
    speak("Hello! I am your offline assistant powered by ChatGPT. Say 'bye' to exit.")

    while True:
        try:
            audio = record_audio()
            user_input = transcribe_audio(audio)

            if not user_input:
                speak("Sorry, I didn’t catch that.")
                continue

            print("You said:", user_input)

            if "bye" in user_input.lower() or "exit" in user_input.lower():
                speak("Goodbye!")
                break

            reply = get_chatgpt_response(user_input)
            speak(reply)

        except KeyboardInterrupt:
            speak("Goodbye!")
            break
        except Exception as e:
            speak(f"An error occurred: {e}")