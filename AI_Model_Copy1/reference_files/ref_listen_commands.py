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
from ssid_functions import *
from utils import *
from youtube_mc import remote_ips, ips
# from shared import *

is_executing_command = False

# def speak(text):
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()


# Lists for mapping words to numbers
words = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
         "eighteen", "nineteen", "twenty"]

numbers = list(range(1, 21))

def word_to_number(word):
    """Convert a number word (e.g., 'two') to its numerical value (e.g., 2)."""
    if word in words:
        index = words.index(word)
        return numbers[index]
    return None

def run_youtube_script():
    """Open Command Prompt in the specified directory and run youtube_mc.py with updated remote_ips."""
    target_directory = r'C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model'

    try:
        # Pass remote_ips as a command-line argument
        remote_ips_str = ','.join(remote_ips)
        print("remote_ips_str",remote_ips_str)
        subprocess.run(
            f'start cmd /k "cd /d {target_directory} && python youtube_mc.py open {remote_ips_str}"',
            shell=True,
            check=True
        )
        speak("Attempting to run the YouTube script on all clients.")
    except subprocess.CalledProcessError as e:
        speak("Failed to run the YouTube script.")
        print(f"Error: {e}")

def close_youtube_script():
    """Open Command Prompt in the specified directory and run youtube_mc.py to close YouTube on specified clients."""
    target_directory = r'C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model'

    try:
        # Pass remote_ips as a command-line argument
        remote_ips_str = ','.join(remote_ips)
        subprocess.run(
            f'start cmd /k "cd /d {target_directory} && python youtube_mc.py close {remote_ips_str}"',
            shell=True,
            check=True
        )
        speak("Attempting to close YouTube on all clients.")
    except subprocess.CalledProcessError as e:
        speak("Failed to close YouTube.")
        print(f"Error: {e}")

def update_remote_ips(command):
    """Update remote_ips based on user command."""
    global remote_ips  # Ensure we're modifying the global variable
    remote_ips.clear()  # Clear any previous entries

    # Extract the word representing the number of clients from the command
    words_in_command = command.split()

    num_clients = None
    for word in words_in_command:
        num_clients = word_to_number(word)
        if num_clients is not None:
            break

    if num_clients is None:
        print("Could not find a valid number in the command.")
        return

    # Ensure we don't exceed the available IPs
    num_clients = min(num_clients, len(ips))

    # Update the remote_ips list
    remote_ips.extend(ips[:num_clients])

    print(f"Updated remote_ips: {remote_ips}")

def disconnect_all_clients():
    target_directory = r'C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model'

    try:
        # Open Command Prompt in the target directory and run the script with the `-disconnect` flag
        process = subprocess.run(
            f'start cmd /c "cd /d {target_directory} && python ssid_script.py -disconnect"',
            shell=True,
            capture_output=True,
            text=True
        )

        if process.returncode == 0:
            speak("Successfully disconnected all clients.")
        else:
            speak("Failed to disconnect all clients.")
            print(f"Script returned error code: {process.returncode}")
            print(f"Standard Output: {process.stdout}")
            print(f"Standard Error: {process.stderr}")

    except subprocess.CalledProcessError as e:
        speak("An error occurred while attempting to disconnect clients.")
        print(f"Exception: {e}")

def execute_command(command):

    global is_executing_command
    is_executing_command = True 
    print("The command is",command)

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
        speak("Opening Gopika SZ")
        open_gopika_sz()

    elif 'open hd sz' in command or 'open hdfc' in command or 'open hdfc z' in command:
        speak("Opening HD SZ")
        open_hd_sz()
    
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
        speak("Originally I was created by Iron Man in a movie, but here I have been created by Harsha and Gophikha. They copied the name...! Don't tell anyone, let it be a secret between us.")

    elif "joke" in command:
        speak(pyjokes.get_joke())

    elif "who am I" in command or "do you know me" in command or "who I am" in command:
        speak("Now you are talking to me, so I guess you are a part of AP Team. The best team hands down.")

    elif "will you be my boyfriend" in command or "will you be my bf" in command:
        speak("I'm not sure about that. If you want to have one, you can ask the person who created me. He is single.")

    elif "i love you" in command:
        speak("It's hard to understand. Ask my creator, he will answer!")

    elif "lock window" in command or "lock device" in command or "lock computer" in command:
        speak("Locking the device")
        ctypes.windll.user32.LockWorkStation()

    elif "write a note" in command or "take a note" in command or 'write note' in command:
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
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        try:
            os.startfile(chrome_path)
        except FileNotFoundError:
            speak("chrome not found")
            print(f"Chrome not found at: {chrome_path}")

    elif "shutdown" in command:
        speak("I am shutting the system down")
        os.system('shutdown /s /t 1')
        
    elif "restart" in command:
        speak("Restarting the system now.")
        os.system('shutdown /r /t 1')  
    
    elif "log off" in command or "sign out" in command:
        speak("Logging off in 10 seconds.")
        subprocess.call(["shutdown", "/l"])
    
    elif "disconnect all clients" in command or "disconnect all claims" in command:
        disconnect_all_clients()

    elif "take screenshot" in command:
        take_screenshot()

    elif "open recent screenshot" in command or "open the screenshot" in command or "open that screenshot" in command or "open screenshot" in command:
        open_recent_screenshot()
    
    elif "run youtube in" in command and ("clients" in command or "claims" in command or "lines" in command):
        connect_to_ssid_from_query("connect all clients to HD MS Teams")
        time.sleep(10)
        update_remote_ips(command)
        speak("Running YouTube in specified clients")
        run_youtube_script()

    # new
    elif "close youtube in" in command and ("clients" in command or "claims" in command or "lines" in command):
        connect_to_ssid_from_query("connect all clients to HD MS Teams")
        update_remote_ips(command)
        speak("Closing YouTube in specified clients")
        close_youtube_script()

    # Open Ruckus Analytics
    elif 'open ra' in command or ('open' in command and 'analytics' in command) or 'open array' in command:
        speak("Opening ruckus analytics")
        open_ruckus_analytics()
        print("opened ruckus analytics")

    # Close Ruckus Analytics
    # elif 'close ra' in command or ('close' in command and 'analytics' in command):
    #     close_ruckus_analytics()

    else:
        print(f"Command did not match any predefined options: {command}")
        speak(f"You said {command}")
        speak("Sorry I'm not yet coded to answer your query")

    is_executing_command = False  


def listen_for_commands():
    global is_executing_command
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        if not is_executing_command:
            with microphone as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                query = recognizer.recognize_google(audio).lower()
                print(f"You said: {query}")

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
