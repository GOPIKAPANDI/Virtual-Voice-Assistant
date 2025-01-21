import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import random
import pyjokes
import ctypes
import time
import subprocess
import re
from ssid_functions import *
from utils import *
import threading

# Initialize text-to-speech engine
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


# Function to handle commands
def listen_for_commands():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        with microphone as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            query = recognizer.recognize_google(audio).lower()
            print(f"You said: {query}")

            # Check if the command starts with "hey jarvis", "hi jarvis", "hello jarvis", or "jarvis"
            if query.startswith(("hey jarvis", "hi jarvis", "hello jarvis", "jarvis")):
                # Strip the trigger word from the command
                command = re.sub(r"^(hey|hi|hello)\s+jarvis\s*", "", query).strip()

                if command:
                    if 'wikipedia' in command:
                        speak('Searching Wikipedia...')
                        command = command.replace("wikipedia", "")
                        results = wikipedia.summary(command, sentences=3)
                        speak("According to Wikipedia")
                        print(results)
                        speak(results)

                    elif 'connect all clients to' in command or 'connect all claims to' in command:
                        connect_to_ssid_from_query(command)

                    elif 'open google' in command:
                        speak("Opening Google...")
                        webbrowser.open("google.com")

                    elif 'open stackoverflow' in command or 'open stack overflow' in command or "open stack over flow" in command or "openstack over flow" in command:
                        speak("Opening Stack Overflow...")
                        webbrowser.open("stackoverflow.com")

                    elif 'open instagram' in command:
                        speak("Opening Instagram...")
                        webbrowser.open("instagram.com")

                    elif 'open gopika sz' in command:
                        open_gopika_sz()

                    elif 'open hd sz' in command or 'open hdfc' in command or 'open hdfc z' in command:
                        open_hd_sz()

                    elif 'open intensity sz' in command or 'open intensity fc' in command:
                        open_intensity_sz()

                    elif 'open density sz' in command or 'open density fc' in command:
                        open_density_sz()

                    # elif 'open youtube and search' in command:
                    #     # Extract the search query part by removing "open youtube and search" from the command
                    #     search_query = command.replace('open youtube and search', '').strip()
                    #     if search_query:
                    #         speak(f"Searching YouTube for {search_query}")
                    #         open_youtube_search(search_query)
                    #     else:
                    #         speak("What do you want to search on YouTube?")
                    #         search_query = listen()
                    #         if search_query:
                    #             open_youtube_search(search_query)

                    elif 'play music' in command or 'play songs' in command:
                        music_dir = 'D:\\Downloads\\Downloads\\Music'
                        songs = os.listdir(music_dir)
                        song = random.choice(songs)
                        print(songs)
                        os.startfile(os.path.join(music_dir, song))
                        speak("Playing music.")
                        print(f"Playing: {song}")

                    elif 'play' in command:
                        # Extract the song and artist (if any)
                        pattern = re.compile(r"play (.+?)(?: by (.+))?$")
                        match = pattern.search(command)
                        if match:
                            song = match.group(1)
                            artist = match.group(2) if match.group(2) else None
                            play_song_on_youtube(song, artist)

                    elif 'the time' in command:
                        strTime = datetime.datetime.now().strftime("%H:%M:%S")
                        speak(f"Sir, the time is {strTime}")

                    elif 'open pycharm' in command:
                        codePath = "C:\\Program Files\\JetBrains\\PyCharm Community Edition 2020.1.2\\bin\\pycharm64.exe"
                        os.startfile(codePath)
                        speak("Opening PyCharm.")

                    elif "who are you" in command:
                        speak("I am Jarvis, your personal assistant.")

                    elif 'how are you' in command or 'how r u' in command:
                        speak("I am fine, thank you.")
                        continue

                    elif "fine" in command:
                        speak("It's good to know that you're fine.")

                    elif "not good" in command or 'Not well' in command:
                        speak("Everything will be alright! Don't worry, just smile...")

                    elif "what's your name" in command or "what is your name" in command:
                        speak("My name is Jarvis, that's what my creator calls me!")

                    elif "who made you" in command or "who created you" in command or "who is your creator" in command:
                        speak(
                            "Originally I was created by Iron Man in a movie, but here I have been created by Harsha. He copied the name...! Don't tell anyone, let it be a secret between us.")

                    elif "joke" in command:
                        speak(pyjokes.get_joke())

                    elif "who am I" in command or "do you know me" in command:
                        speak("Now you are talking to me, so I guess you are a part of AP Team. The best team hands down.")

                    elif "i love you" in command:
                        speak("It's hard to understand. Ask my creator, he will answer!")

                    elif "lock window" in command or "lock device" in command or "lock computer" in command:
                        speak("Locking the device.")
                        ctypes.windll.user32.LockWorkStation()

                    elif "write a note" in command or "take a note" in command:
                        speak("What should I write, sir?")
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

                    elif 'volume' in command:
                        # Notify the user and provide instructions
                        speak(
                            "Here you go. Use your thumb and index finger to control the volume. Be close to the webcam so that you can do it accurately.")

                        volume_control_thread = threading.Thread(target=control_volume)
                        volume_control_thread.start()

                    elif "open chrome" in command:
                        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe %s"
                        os.startfile(chrome_path)

                    elif "shutdown" in command:
                        speak("Are you sure you want to shutdown the computer? Say yes or no.")
                        confirmation = listen()
                        if confirmation and 'yes' in confirmation:
                            os.system('shutdown /s /t 1')
                        else:
                            speak("Shutdown canceled.")

                    elif "restart" in command:
                        speak("Are you sure you want to restart the computer? Say yes or no.")
                        confirmation = listen()
                        if confirmation and 'yes' in confirmation:
                            os.system('shutdown /r /t 1')
                        else:
                            speak("Restart canceled.")

                    elif "log off" in command or "sign out" in command:
                        speak("Logging off in 10 seconds.")
                        subprocess.call(["shutdown", "/l"])

                    elif "turn off" in command:
                        speak("Okay, I will sleep now. I am here if you need me.")

                    # elif "run youtube in all clients" in command or "run youtube in all claims":
                    #     speak("Running YouTube in all clients.")
                    #     run_youtube_script()

                    elif "take screenshot" in command:
                        take_screenshot()

                    elif "open recent screenshot" in command or "open the screenshot" in command:
                        open_recent_screenshot()

                    # elif 'volume' in command:
                    #     # Start the volume control in a separate thread
                    #

                    else:
                        speak(f"You said {command}.")
                        speak("Sorry, I'm not yet coded to answer your query.")

                else:
                    speak("Yes, how can I assist you?")

        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
        except sr.RequestError:
            speak("Sorry, my speech service is down.")

if __name__ == "__main__":
    listen_for_commands()
