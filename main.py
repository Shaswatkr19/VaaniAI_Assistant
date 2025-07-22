import speech_recognition as sr
import os
import webbrowser
import musicLibrary
import requests
import google.generativeai as genai


newsapi_key = os.environ.get("NEWSAPI_KEY")
gemini_api_key = os.environ.get("GEMINIAI_API_KEY")


genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-pro")

WAKE_WORDS = ["alexa"]
user_info = {}

def speak(text):
    try:
        from gtts import gTTS
        from playsound import playsound

        tts = gTTS(text=text, lang='en')
        tts.save("alexa.mp3")
        playsound("alexa.mp3")
        os.remove("alexa.mp3")
    except Exception as e:
        print("Fallback (say):", e)
        os.system(f'say "{text}"')


def smallTalk():
    r = sr.Recognizer()

    speak("Hi! Before we begin, may I know your name?")
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=4)
            name = r.recognize_google(audio)
            user_info['name'] = name
            speak(f"Nice to meet you, {name}!")
    except Exception as e:
        user_info['name'] = "boss"
        speak("I'll call you boss for now.")

    speak("What do you do?")
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=4)
            job = r.recognize_google(audio)
            user_info['job'] = job
            speak(f"Wow! Being a {job} must be exciting.")
    except Exception as e:
        user_info['job'] = "developer"
        speak("Got it. You sound like a techy person!")


def aiProcess(command):
    try:
        response = model.generate_content(
            f"You are a helpful voice assistant named Aarya. Respond shortly to this command: {command}"
        )
        return response.text
    except Exception as e:
        print("Gemini API error:", e)
        return "I'm sorry, I couldn't process that with AI."


def processCommand(c):
    c = c.lower()
    print("Command:", c)

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
        speak("Opening JioHotstar")
        webbrowser.open("https://www.hotstar.com/in/home")

    elif c.startswith("play"):
        song = c.split("play", 1)[1].strip()
        link = musicLibrary.music.get(song.lower())
        if link:
            speak(f"Playing {song}")
            webbrowser.open(link)
        else:
            speak("Sorry, I couldn't find that song in your library.")

    elif "news" in c:
        r = requests.get(f"https://newsdata.io/api/1/news?apikey={newsapi_key}&country=in&language=en&category=technology")
        if r.status_code == 200:
            data = r.json()
            results = data.get('results', [])
            speak("Here are the latest technology headlines from India:")
            for article in results[:3]:
                speak(article['title'])
        else:
            speak("Sorry, I couldn't fetch the news.")

    elif "exit" in c:
        speak("Goodbye boss!")
        exit()

    else:
        output = aiProcess(c)
        speak(output)


if __name__ == "__main__":
    speak("Initializing Alexa clone...")
    smallTalk()

    while True:
        r = sr.Recognizer()
        print("🎤 Listening for wake word...")

        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=3, phrase_time_limit=4)

            word = r.recognize_google(audio)
            print("You said:", word)

            if any(wake in word.lower() for wake in WAKE_WORDS):
                speak(f"Yes {user_info.get('name', 'boss')}, I'm listening.")

                with sr.Microphone() as source:
                    print("🎤 Listening for command...")
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source, timeout=3, phrase_time_limit=5)

                try:
                    command = r.recognize_google(audio)
                    print("Heard command:", command)
                    processCommand(command)
                except Exception as e:
                    print("Command recognition error:", e)
                    speak("Sorry, I didn't catch that.")
        except Exception as e:
            print("Wake word error:", e)