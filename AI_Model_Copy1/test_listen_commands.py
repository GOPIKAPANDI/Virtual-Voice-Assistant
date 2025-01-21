import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import re
import webbrowser
import os
import random
import pyjokes
import ctypes
import time
import threading
import subprocess
from wikipedia.exceptions import DisambiguationError
from ssid_functions import *
from utils import *
from youtube_mc import remote_ips, ips
# from shared import *
import logging
import requests
import whisper
import sounddevice as sd
import numpy as np
import warnings
import sys
import pythoncom

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the logger to capture INFO level and above

# Create file handler for warnings and errors
error_handler = logging.FileHandler('errors.log')
error_handler.setLevel(logging.WARNING)  # Capture WARNING and ERROR logs
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)

# Create file handler for debug logs
debug_handler = logging.FileHandler('debug.log')
debug_handler.setLevel(logging.DEBUG)  # Capture DEBUG logs
debug_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(debug_formatter)

# Add handlers to the logger
logger.addHandler(error_handler)
logger.addHandler(debug_handler)

# Example log messages
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.debug('This is a debug message')


is_executing_command = False


def execute_command(command):
    pythoncom.CoInitialize() 
    global is_executing_command
    is_executing_command = True 
    print("The command is",command)
    
    if 'wikipedia' in command:
            search_term = command.replace("wikipedia", "").strip()  
            try:
                # Fetch summary from Wikipedia
                results = wikipedia.summary(search_term, sentences=3)
                speak(f"According to Wikipedia, {results}")
                print(results)

            except DisambiguationError as e:
                # Handle the disambiguation error
                speak("The term you searched for is ambiguous. Here are some options:")
                print("Disambiguation options:")
                options = e.options[:5]  # Show the first 5 disambiguation options

                for option in options:
                    print(option)
                    speak(option)
                # You can then choose to prompt the user to be more specific if needed
                speak("Please be more specific in your search term.")

    elif 'open google' in command:
        speak("Opening Google...")
        webbrowser.open("google.com")
    
    elif 'open stackoverflow' in command or 'open stack overflow' in command or "open stack over flow" in command or "openstack over flow" in command:
        speak("Opening Stack Overflow...")
        webbrowser.open("stackoverflow.com")

    elif 'open instagram' in command:
        speak("Opening Instagram...")
        webbrowser.open("instagram.com")

    elif 'can you hear me' in command or 'am i audible' in command:
        speak('Yes I can hear you. Tell me how can I assist you')

    elif 'open gopika sz' in command:
        speak("Opening Gopika SZ")
        open_gopika_sz()

    elif 'open hd sz' in command or 'open hdfc' in command or 'open hdfc z' in command:
        speak("Opening HD SZ")
        open_hd_sz()
        # speak("Opened HD SZ")
    
    elif 'open intensity sz' in command or 'open intensity fc' in command:
        speak("Opening Intensity SZ")
        open_intensity_sz()   

    elif 'open density sz' in command or 'open density fc' in command:
        speak("Opening Density SZ")
        open_density_sz()   
    
    elif 'open youtube and search' in command:
        # Extract the search query part by removing "open youtube and search" from the command
        search_query = command.replace('open youtube and search', '').strip()
        if search_query:
            speak(f"Searching YouTube for {search_query}")
            open_youtube_search(search_query)
        else:
            speak("What do you want to search on YouTube?")
            search_query = listen_for_commands()
            if search_query:
                open_youtube_search(search_query)

    elif 'play music' in command or 'play songs' in command:
        music_dir = r'D:\Downloads\Downloads\Music'
        try:
            songs = os.listdir(music_dir)
            if songs:  # Ensure the folder is not empty
                song = random.choice(songs)
                print(songs)
                os.startfile(os.path.join(music_dir, song))
                speak("Playing music.")
                print(f"Playing: {song}")
            else:
                speak("The music folder is empty.")
        except FileNotFoundError:
            speak("Music directory not found. Please check the path.")
    
    elif 'play' in command:
        # Extract the song and artist (if any)
        pattern = re.compile(r"play (.+?)(?: by (.+))?$")
        match = pattern.search(command)
        if match:
            song = match.group(1)
            artist = match.group(2) if match.group(2) else None
            # Run YouTube playback in a separate thread
            play_thread = threading.Thread(target=play_song_on_youtube, args=(song, artist))
            play_thread.start()

    elif 'the time' in command:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {strTime}")

    elif 'open pycharm' in command or 'open python' in command or 'open pie chart' in command:
        codePath = r"C:\Program Files\JetBrains\PyCharm Community Edition 2023.1.4\bin\pycharm64.exe"
        try:
            os.startfile(codePath)
            speak("Opening PyCharm.")
        except FileNotFoundError:
            speak("PyCharm executable not found. Please check the path.")

    elif "who are you" in command:
        speak("I am Jarvis, your personal assistant.")

    elif 'how are you' in command or 'how r u' in command:
        speak("I am fine, thank you. How are you?")

    elif "not good" in command or "I am ok" in command or "not fine" in command:
        speak("Everything will be alright! Don't worry, just smile...")     

    elif "fine" in command:
        speak("It's good to know that you're fine")

    elif "what's your name" in command or "what is your name" in command:
        speak("My name is Jarvis, that's what my creator calls me!")

    elif "who made you" in command or "who created you" in command or "who is your creator" in command:
        speak("I have been created by AP QA Team.")

    elif "joke" in command:
        speak(pyjokes.get_joke())

    elif "who am I" in command or "do you know me" in command or "who I am" in command:
        speak("Now you are talking to me, so I guess you are a part of AP Team. The best team hands down.")

    elif "write a note" in command or "take a note" in command or 'write note' in command:
        speak("Please type in the terminal that What should I write?")
        note = input("Enter note content: ")
        if note:
            with open('jarvis.txt', 'w') as file:
                file.write(note)
            speak("Note has been written!")
        else:
            speak("Sorry, I couldn't capture the note content.")

    elif "show note" in command:
        speak("Here is the note")
        with open("jarvis.txt", "r") as file:
            print(file.read())
        time.sleep(10)

    elif "open chrome" in command:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        try:
            speak("Opening chrome")
            os.startfile(chrome_path)
        except FileNotFoundError:
            speak("chrome not found")
            print(f"Chrome not found at: {chrome_path}")

    else:
        print(f"Command did not match any predefined options: {command}")
        speak(f"You said {command}")
        speak("Sorry I'm not yet coded to answer your query")

    is_executing_command = False  

# Function to record audio from the microphone
def record_audio(duration, samplerate=16000):
    print("Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()  # Wait until the recording is finished
    print("Recording complete.")
    return audio.flatten() 

def listen_for_commands():
    global is_executing_command

    while True:
        if not is_executing_command:
            try:
                with open("warnings.log", "w") as f:
                    with warnings.catch_warnings(record=True) as w:
                        # Load the Whisper model
                        model = whisper.load_model("small")

                        # Record audio for a specified duration
                        duration = 10  # seconds
                        audio_data = record_audio(duration)

                        # Transcribe the audio
                        result = model.transcribe(audio_data, language='en')

                        # Print only the transcription
                        # print("The whole query is",result["text"])
                        query1 = result["text"].lower().strip()
                        query = re.sub(r"[.,]", "", query1)
                        print("The whole query is",query)
                        if query.startswith(("hey jarvis", "hi jarvis", "hello jarvis", "jarvis")):
                            # Strip the trigger word from the command
                            command = re.sub(r"^(hey|hi|hello)?\s*jarvis\s*", "", query).strip()
                            print("Command after strip:", command)

                            if command:
                                # Execute the command in a separate thread
                                command_thread = threading.Thread(target=execute_command, args=(command,))
                                command_thread.start()
                            else:
                                speak("Yes, how can I assist you?")   
                        else:
                            print("The command doesn't start with jarvis")        
                        # Log any warnings to the file
                        for warning in w:
                            f.write(str(warning.message) + '\n')

            except sr.UnknownValueError:
                pass
                # speak("Sorry, I did not understand that")
            except sr.RequestError:
                speak("Sorry, my speech service is down.")   
            except Exception as e:
                # Catch all unexpected errors
                print(f"An error occurred: {e}")
                speak(f"An error occurred: {e}")         
                    

if __name__ == "__main__":
    listen_for_commands()

