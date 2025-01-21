import pyttsx3
import speech_recognition as sr
import datetime
from ssid_functions import *
from listen_commands import *


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# listening = False  # Global variable to track listening state

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    elif hour >= 12 and hour < 16:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("BDC AP QA! Jarvis here, Please tell me how may I help you")



if __name__ == "__main__":
    # wishMe()
    listen_for_commands()
