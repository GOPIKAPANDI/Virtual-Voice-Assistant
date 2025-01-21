import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import random
import pyjokes
import ctypes
import time
import multiprocessing
import subprocess
import re
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

listening = False  # Global variable to track listening state

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
    speak("Vardhan! Jarvis here, Please tell me how may I help you")

def listen():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio).lower()
        print(f"You said: {query}")
        return query
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return None

def open_browser():
    # Use predefined username and password
    username = "admin"
    password = "Lab4man14#"

    # Set Chrome options to ignore SSL certificate errors
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')

    # Specify the path to the WebDriver executable
    service = Service('C:\\webdrivers\\chromedriver.exe')  # Update with the correct path to your WebDriver

    # Initialize the Selenium WebDriver with the specified service and options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the browser and navigate to the login page
    speak("Opening HD SZ.")
    url = "https://10.174.67.33:8443/cas/login?service=%2Fwsg%2Flogin%2Fcas#m"
    driver.get(url)

    # Fill in the username and password fields
    time.sleep(2)  # Wait for the page to load

    try:
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys(username)
        password_field.send_keys(password)

        # Submit the form
        password_field.send_keys(Keys.RETURN)

        # Wait for a few seconds to ensure the login process completes
        time.sleep(5)

        # Confirm that the site has been opened
        speak("Opened HD SZ.")
        
        # Keep the browser open
        driver.switch_to.window(driver.current_window_handle)
        while True:
            time.sleep(10)

    except Exception as e:
        speak(f"An error occurred: {e}")

def normalize_ssid(ssid_name):
    # Mapping of recognized variations to the standard format
    ssid_mapping = {
        "hdms teams": "HD MS Teams",
        "hd ms teams": "HD MS Teams",
        "hdmsteams": "HD MS Teams",
        "hd msteams": "HD MS Teams"
    }
    
    # Normalize the input SSID name
    normalized_ssid = ssid_mapping.get(ssid_name.lower(), ssid_name)
    
    return normalized_ssid

def update_script_content(script_content, ssid_name):
    # Normalize the SSID name for use in the profile name
    normalized_ssid = ssid_name.lower().replace(" ", "-")
    
    # Define patterns to match only the initialization lines
    ssid_pattern = re.compile(r'^(\s*ssid\s*=\s*)".*?"', re.MULTILINE)
    name_pattern = re.compile(r'^(\s*name\s*=\s*)".*?"', re.MULTILINE)
    profile_pattern = re.compile(r'^(\s*profile_name\s*=\s*)".*?"', re.MULTILINE)

    # Replace the initializations for ssid, name, and profile_name
    script_content = ssid_pattern.sub(f'\\1"{ssid_name}"', script_content)
    script_content = name_pattern.sub(f'\\1"{ssid_name}"', script_content)
    script_content = profile_pattern.sub(f'\\1"profile-{normalized_ssid}"', script_content)

    return script_content

def connect_to_hd_ms_teams(ssid_name):
    ssid_name = normalize_ssid(ssid_name)
    target_directory = r'C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model'
    
    try:
        # Open Command Prompt in the target directory and run the script
        subprocess.run(
            f'start cmd /k "cd /d {target_directory} && python ssid_script.py"',
            shell=True
        )

        speak("Attempting to connect all clients to HD MS Teams.")
    except subprocess.CalledProcessError as e:
        speak("Failed to run the script.")
        print(f"Error: {e}")


def connect_to_ssid_from_query(query):
    match = re.search(r'connect all (clients|claims) to (.+)', query)
    if match:
        ssid_name = match.group(2).strip()
        ssid_name = normalize_ssid(ssid_name)
        speak(f"Connecting all clients to SSID: {ssid_name}")
        connectToSSID(ssid_name)
    else:
        speak("Sorry, I couldn't find the SSID in your request.")


def open_hd_sz():
    # Start the browser script as a separate process
    subprocess.Popen(['python', 'open_hd_sz.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_intensity_sz():
    subprocess.Popen(['python', 'open_intensity_sz.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_density_sz():
    subprocess.Popen(['python', 'open_density_sz.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_gopika_sz():
    subprocess.Popen(['python', 'open_gopika_sz.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

def connectToSSID(ssid_name):
    # ssid_name = get_ssid_name()

    # Update the script with new SSID
    script_path = r'C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model\ssid_script.py'
    with open(script_path, 'r') as file:
        script_content = file.read()
          
    script_content = update_script_content(script_content, ssid_name)

    with open(script_path, 'w') as file:
        file.write(script_content)

    print(f"Script updated with SSID: {ssid_name}")

    if ssid_name == "hd ms teams" or ssid_name == "HD MS Teams":
        connect_to_hd_ms_teams(ssid_name)

# Function to search YouTube
def open_youtube_search(search_query):
    subprocess.Popen(['python', 'open_youtube_video.py', search_query], creationflags=subprocess.CREATE_NEW_CONSOLE)


def listen_for_commands():
    global listening
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

            if "jarvis" in query or "hello jarvis" in query or "hey jarvis" in query or "hi jarvis" in query or "hello" in query:
                listening = True
                speak("Yes, how can I assist you?")
                continue  # Skip

            if listening:

                if 'wikipedia' in query:
                    speak('Searching Wikipedia...')
                    query = query.replace("wikipedia", "")
                    results = wikipedia.summary(query, sentences=3)
                    speak("According to Wikipedia")
                    print(results)
                    speak(results)
                
                elif 'connect all clients to' in query or 'connect all claims to' in query:
                    connect_to_ssid_from_query(query)

                # elif 'connect to ssid' in query:
                #     connectToSSID()

                elif 'open youtube' in query:
                    speak("Opening YouTube...")
                    webbrowser.open("youtube.com")

                elif 'open google' in query:
                    speak("Opening Google...")
                    webbrowser.open("google.com")

                elif 'open stackoverflow' in query or 'open stack overflow' in query or "open stack over flow" in query or "openstack over flow" in query:
                    speak("Opening Stack Overflow...")
                    webbrowser.open("stackoverflow.com")

                elif 'open instagram' in query:
                    speak("Opening Instagram...")
                    webbrowser.open("instagram.com")
                
                elif 'open gopika sz' in query:
                    open_gopika_sz()

                elif 'open hd sz' in query or 'open hdfc' in query or 'open hdfc z' in query:
                    open_hd_sz()
                
                elif 'open intensity sz' in query or 'open intensity fc' in query:
                    open_intensity_sz()

                elif 'open density sz' in query or 'open density fc' in query:
                    open_density_sz()
                
                elif 'search youtube' in query:
                    speak("What do you want to search on YouTube?")
                    search_query = listen()
                    if search_query:
                        open_youtube_search(search_query)

                elif 'play music' in query or 'play songs' in query:
                    music_dir = 'D:\\Downloads\\Downloads\\Music'
                    songs = os.listdir(music_dir)
                    song = random.choice(songs)
                    print(songs)
                    os.startfile(os.path.join(music_dir, song))

                elif 'the time' in query:
                    strTime = datetime.datetime.now().strftime("%H:%M:%S")
                    speak(f"Sir, the time is {strTime}")

                elif 'open pycharm' in query:
                    codePath = "C:\\Program Files\\JetBrains\\PyCharm Community Edition 2020.1.2\\bin\\pycharm64.exe"
                    os.startfile(codePath)

                elif 'email to vardhan' in query:
                    try:
                        speak("What should I say?")
                        content = input("Enter email content: ")
                        if content:
                            to = "iamvd7@gmail.com"
                            sendEmail(to, content)
                            speak("Email has been sent!")
                        else:
                            speak("Sorry, I couldn't capture the email content.")
                    except Exception as e:
                        print(e)
                        speak("Sorry sir, I am not able to send this email")

                elif "who are you" in query:
                    speak("I am Jarvis")

                elif 'how are you' in query or 'how r u' in query:
                    speak("I am fine, thank you. How are you, Sir?")

                elif "fine" in query:
                    speak("It's good to know that you're fine")

                elif "not good" in query:
                    speak("Everything will be alright! Don't worry, just smile...")

                elif "what's your name" in query or "what is your name" in query:
                    speak("My name is Jarvis, that's what my creator calls me!")

                elif "who made you" in query or "who created you" in query or "who is your creator" in query:
                    speak("Originally I was created by Iron Man in a movie, but here I have been created by Vardhan. He copied the name...! Don't tell anyone, let it be a secret between us.")

                elif "joke" in query:
                    speak(pyjokes.get_joke())

                elif "who am I" in query or "do you know me" in query:
                    speak("Now you are talking to me, so you are Vardhan or somehow related to Vardhan")

                elif "will you be my boyfriend" in query or "will you be my bf" in query:
                    speak("I'm not sure about that. If you want to have one, you can ask the person who created me. He is single.")

                elif "i love you" in query:
                    speak("It's hard to understand. Ask my creator, he will answer!")

                elif "lock window" in query or "lock device" in query or "lock computer" in query:
                    speak("Locking the device")
                    ctypes.windll.user32.LockWorkStation()

                elif "write a note" in query or "take a note" in query:
                    speak("What should I write, sir?")
                    note = input("Enter note content: ")
                    if note:
                        with open('jarvis.txt', 'w') as file:
                            file.write(note)
                        speak("Note has been written!")
                    else:
                        speak("Sorry, I couldn't capture the note content.")

                elif "show note" in query:
                    speak("Here is the note")
                    with open("jarvis.txt", "r") as file:
                        print(file.read())
                    time.sleep(10)

                elif "open chrome" in query:
                    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe %s"
                    os.startfile(chrome_path)

                elif "shutdown" in query:
                    speak("Are you sure you want to shutdown the computer? Say yes or no.")
                    confirmation = listen()
                    if confirmation and 'yes' in confirmation:
                        os.system('shutdown /s /t 1')
                    else:
                        speak("Shutdown canceled.")

                elif "restart" in query:
                    speak("Are you sure you want to restart the computer? Say yes or no.")
                    confirmation = listen()
                    if confirmation and 'yes' in confirmation:
                        os.system('shutdown /r /t 1')
                    else:
                        speak("Restart canceled.")

                elif "cancel" in query:
                    speak("Okay, I am here if you need me.")

                else:
                    speak(f"You said {query}")
                    speak("Sorry I'm not yet coded to answer your query")

            listening = False

        except sr.UnknownValueError:
            speak("Sorry, I did not understand that")
        except sr.RequestError:
            speak("Sorry, my speech service is down.")

if __name__ == "__main__":
    wishMe()
    listen_for_commands()
