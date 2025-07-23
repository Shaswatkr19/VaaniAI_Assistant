import speech_recognition as sr
import os
import webbrowser
import musicLibrary
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
from pygame import mixer
import time

# 🔐 Load environment variables
load_dotenv()
newsapi_key = os.environ.get("NEWSAPI_KEY")
gemini_api_key = os.environ.get("GEMINIAI_API_KEY")

# 🧠 Gemini model setup
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-pro")

WAKE_WORDS = ["alexa"]
user_info = {}

# ✅ Speak with improved audio handling
def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        filename = "alexa.mp3"
        tts.save(filename)

        mixer.init()
        mixer.music.load(filename)
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(0.2)

        mixer.music.stop()
        mixer.quit()
        os.remove(filename)
    except Exception as e:
        print("🎙️ TTS fallback (say):", e)
        os.system(f'say "{text}"')

# 👋 Small talk for personalization
def smallTalk():
    r = sr.Recognizer()
    speak("Hi! Before we begin, may I know your name?")
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5)
            name = r.recognize_google(audio)
            user_info['name'] = name
            speak(f"Nice to meet you, {name}!")
    except:
        user_info['name'] = "boss"
        speak("I'll call you boss for now.")

    speak("What do you do?")
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5)
            job = r.recognize_google(audio)
            user_info['job'] = job
            speak(f"Wow! Being a {job} must be exciting.")
    except:
        user_info['job'] = "developer"
        speak("Got it. You sound like a techy person!")

# 🧠 AI response via Gemini
def aiProcess(command):
    try:
        response = model.generate_content(
            f"You are a helpful assistant named Aarya. Respond briefly to: {command}"
        )
        return response.text.strip()
    except Exception as e:
        print("Gemini API error:", e)
        return "I'm sorry, I couldn't process that right now."

# 🎯 Command router
def processCommand(c):
    c = c.lower()
    print("🎯 Command received:", c)

    if "youtube" in c:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "google" in c:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "music" in c:
        speak("Opening Music")
        webbrowser.open("https://music.youtube.com")

    elif "udemy" in c:
        speak("Opening Udemy")
        webbrowser.open("https://www.udemy.com/home/my-courses/learning/")

    elif "hotstar" in c or "jiohotstar" in c:
        speak("Opening Hotstar")
        webbrowser.open("https://www.hotstar.com/in/home")

    elif c.startswith("play"):
        song = c.split("play", 1)[1].strip()
        if musicLibrary:
            link = musicLibrary.music.get(song.lower())
            if link:
                speak(f"Playing {song}")
                webbrowser.open(link)
            else:
                speak("Sorry, I couldn't find that song in your library.")
        else:
            speak("Your music library is not loaded.")

    elif "news" in c:
        try:
            r = requests.get(
                f"https://newsdata.io/api/1/news?apikey={newsapi_key}&country=in&language=en&category=technology"
            )
            if r.status_code == 200:
                data = r.json()
                results = data.get('results', [])
                speak("Here are the latest tech headlines from India:")
                for article in results[:3]:
                    speak(article['title'])
            else:
                speak("Sorry, I couldn't fetch the news.")
        except Exception as e:
            print("News fetch error:", e)
            speak("Error while fetching news.")

    elif "exit" in c or "quit" in c:
        speak("Goodbye boss!")
        exit()

    else:
        output = aiProcess(c)
        speak(output)

# 🏁 Main loop
if __name__ == "__main__":
    speak("Initializing Alexa...")
    smallTalk()

    r = sr.Recognizer()

    while True:
        print("🎧 Listening for wake word...")
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=8, phrase_time_limit=4)

            word = r.recognize_google(audio)
            print("🗣️ You said:", word)

            if any(wake in word.lower() for wake in WAKE_WORDS):
                speak(f"Yes {user_info.get('name', 'boss')}, I'm listening.")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    speak("Go ahead.")
                    audio = r.listen(source, timeout=6, phrase_time_limit=6)

                try:
                    command = r.recognize_google(audio)
                    print("✅ Heard command:", command)
                    processCommand(command)
                except Exception as e:
                    print("🎤 Command recognition error:", e)
                    speak("Sorry, I didn't catch that.")
        except sr.WaitTimeoutError:
            print("⌛ No input detected.")
        except Exception as e:
            print("❗ Wake word error:", e)