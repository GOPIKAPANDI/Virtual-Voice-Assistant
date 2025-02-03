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

# def speak(text):
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()

device_mapping = {
    'ip1': 'device1',
    'ip2': 'device2'...
}

# Lists for mapping words to numbers
words = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
         "eighteen", "nineteen", "twenty"]

numbers = list(range(1, 21))

# def word_to_number(word):
#     """Convert a number word (e.g., 'two') to its numerical value (e.g., 2)."""
#     if word in words:
#         index = words.index(word)
#         return numbers[index]
#     return None

def word_to_number(word):
    """Convert a number word (e.g., 'two') to its numerical value (e.g., 2)."""
    if word in words:
        index = words.index(word)
        return numbers[index]
    return None

def run_youtube_script():
    """Open Command Prompt in the specified directory and run youtube_mc.py with updated remote_ips."""
    target_directory = r'C:\AI_Model_Copy1'
    # Pass remote_ips as a command-line argument
    remote_ips_str = ','.join(remote_ips)
    print("remote_ips_str", remote_ips_str)
    try:
        result = subprocess.run(
            [r'python', 'youtube_mc.py', 'open', remote_ips_str],
            cwd=target_directory,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # speak("Attempting to run the YouTube script on all clients.")
        # Check output for any failed IPs
        output = result.stdout.decode().strip()
        print("output===>", output)
        # Split output into lines and check the last line
        lines = output.splitlines()
        last_line = lines[-1] if lines else ""
        if "Failed to execute on the following devices:" in last_line:
            # Extract and speak the failed IPs
            failed_ips = last_line.split(": ", 1)[-1]
            speak(f"Failed to execute on the following devices: {failed_ips.strip()}")
            speak("I am waiting for your next instruction")
        elif "All commands executed successfully." in last_line:
            speak("Successfully ran youtube in all clients")
    except subprocess.CalledProcessError as e:
        # Handle the error from youtube_mc.py execution
        speak("Failed to run the YouTube script.")
        print(f"Error: {e}")
        error_output = e.stderr.decode().strip()
        if error_output:
            print(f"Error Output: {error_output}")

def close_youtube_script():
    """Open Command Prompt in the specified directory and run youtube_mc.py to close YouTube on specified clients."""
    target_directory = r'C:\AI_Model_Copy1'

    remote_ips_str = ','.join(remote_ips)
    print("remote_ips_str", remote_ips_str)
    try:
        result = subprocess.run(
            [r'python', 'youtube_mc.py', 'close', remote_ips_str],
            cwd=target_directory,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output = result.stdout.decode().strip()
        # print("output===>", output)
        # Split output into lines and check the last line
        lines = output.splitlines()
        last_line = lines[-1] if lines else ""
        if "Failed to execute on the following devices:" in last_line:
            # Extract and speak the failed IPs
            failed_ips = last_line.split(": ", 1)[-1]
            speak(f"Failed to close youtube on the following devices: {failed_ips.strip()}")
            speak("I am waiting for your next instruction")
        else:
            speak("Successfully closed youtube in all clients")

    except subprocess.CalledProcessError as e:
        # Handle the error from youtube_mc.py execution
        speak("Failed to run the Close YouTube script.")
        print(f"Error: {e}")
        error_output = e.stderr.decode().strip()
        if error_output:
            print(f"Error Output: {error_output}")

def extract_number_from_command(command):
    """Extracts either the numerical or word-based number from the command."""
    words_in_command = command.split()

    if "all" in words_in_command:
        return 30 

    # Check for a numerical number
    for word in words_in_command:
        if word.isdigit():  # If the word is a digit (e.g., '10')
            return int(word)

    # Check for word-based number
    for word in words_in_command:
        num = word_to_number(word.lower())  # Convert the word to number if possible
        if num is not None:
            return num

    return None

def update_remote_ips(command):
    """Update remote_ips based on user command."""
    global remote_ips  # Ensure we're modifying the global variable
    remote_ips.clear()  # Clear any previous entries

    num_clients = extract_number_from_command(command)

    if num_clients is None:
        print("Could not find a valid number in the command.")
        return

    # Ensure we don't exceed the available IPs
    num_clients = min(num_clients, len(ips))

    # Update the remote_ips list
    remote_ips.extend(ips[:num_clients])

def handle_connection(command, ssid):
    # Call the FastAPI endpoint to connect clients with SSID as a query parameter
    url = "http://ip:8000/connect_clients/"
    params = {"ssid": ssid}

    try:
        response = requests.get(url, params=params)  # Use GET and send parameters
        if response.status_code == 200:
            data = response.json()
            # Check for failed IPs
            failed_ips = data.get("Failed_IPs", [])
            if failed_ips:
                failed_ips_message = ", ".join(failed_ips)
                speak(f"The following clients failed to connect: {failed_ips_message}")
            else:
                speak("All clients connected successfully.")
        else:
            print("Error:", response.status_code, response.text)
            speak("There was an error connecting the clients.")
    except Exception as e:
        print("An error occurred:", str(e))
        speak("An error occurred while connecting the clients.")


def handle_disconnection(command):
    # Call the FastAPI endpoint to disconnect clients
    url = "http://ip:8000/disconnect_clients/"
    
    try:
        response = requests.post(url)  # Use POST method
        if response.status_code == 200:
            data = response.json()
            # Check for failed IPs
            failed_ips = data.get("Failed_IPs", [])
            if failed_ips:
                failed_ips_message = ", ".join(failed_ips)
                speak(f"The following clients failed to disconnect: {failed_ips_message}")
            else:
                speak("All clients disconnected successfully.")
        else:
            print("Error:", response.status_code, response.text)
            speak("There was an error disconnecting the clients.")
    except Exception as e:
        print("An error occurred:", str(e))
        speak("An error occurred while disconnecting the clients.")


def execute_command(command):

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

    elif 'AP is up' in command:
        AP_model1 = get_current_AP_R750()
        AP_model2 = get_current_AP_R770()
        AP_model = AP_model1 if AP_model1 != "" else AP_model2
        speak(f"{AP_model} is up and brodcasting ssid")

    #///t670
    elif 'what is the version of t670' in command or ('version' in command and ('t670' in command or 't 670' in command)):
        # Call function to get the version from the AP
        version = get_t670ap_version()
        speak(f"The version is {version}")

    elif 'what is the country code of t670' in command or ('country' in command and ('t670' in command or 't 670' in command)):
        country_code = get_t670ap_country_code()
        speak(f"The country code is {country_code}")

    elif 'what is the channel of t670' in command or ('channel' in command and ('t670' in command or 't 670' in command)):
        channel_info = get_t670ap_channel_wifi1()
        speak(f"It is operating on {channel_info}")

    elif 'what is the uptime of t670' in command or ('uptime' in command and ('t670' in command or 't 670' in command)):
        uptime = get_t670ap_uptime()
        speak(f"The Uptime of t670 is {uptime}")

    elif 'what is the ip address of t670' in command or ('ip' in command and ('t670' in command or 't 670' in command)):
        ip_address = get_t670ap_ip_address_wan()
        speak(f"The IP address of t670 is {ip_address}")   
    

    #///r760 
    elif 'what is the version of r760' in command or ('version' in command and ('r760' in command or 'r 760' in command or 'are760' in command or 'are 760' in command)):
        # Call function to get the version from the AP
        version = get_r760ap_version()
        speak(f"The version is {version}")

    elif 'what is the country code of r760' in command or ('country' in command and ('r760' in command or 'r 760' in command or 'are760' in command or 'are 760' in command)):
        country_code = get_r760ap_country_code()
        speak(f"The country code is {country_code}")

    elif 'what is the channel of r760' in command or ('channel' in command and ('r760' in command or 'r 760' in command or 'are760' in command or 'are 760' in command)):
        channel_info = get_r760ap_channel_wifi1()
        speak(f"It is operating on {channel_info}")

    elif 'what is the uptime of r760' in command or ('uptime' in command and ('r760' in command or 'r 760' in command or 'are760' in command or 'are 760' in command)):
        uptime = get_r760ap_uptime()
        speak(f"The Uptime of r760 is {uptime}")

    elif 'what is the ip address of r760' in command or ('ip' in command and ('r760' in command or 'r 760' in command or 'are760' in command or 'are 760' in command)):
        ip_address = get_r760ap_ip_address_wan()
        speak(f"The IP address of r760 is {ip_address}")   

    #///r770
    elif 'what is the version of r770' in command or ('version' in command and ('r770' in command or 'r 770' in command or 'are770' in command or 'are 770' in command)):
        # Call function to get the version from the AP
        version = get_r770ap_version()
        speak(f"The version is {version}")

    elif 'what is the country code of r770' in command or ('country' in command and ('r770' in command or 'r 770' in command or 'are770' in command or 'are 770' in command or 'art770' in command or 'art 770' in command or 'rs 770' in command or 'rs770' in command)):                                                  
        country_code = get_r770ap_country_code()
        speak(f"The country code is {country_code}")

    elif 'what is the channel of r770' in command or ('channel' in command and ('r770' in command or 'r 770' in command or 'are770' in command or 'are 770' in command  or'art770' in command or 'art 770' in command or 'art 770' in command or 'rs 770' in command or 'rs770' in command)):
        channel_info = get_r770ap_channel_wifi1()
        speak(f"It is operating on {channel_info}")

    elif 'what is the uptime of r770' in command or ('uptime' in command and ('r770' in command or 'r 770' in command or 'are770' in command or 'are 770' in command or 'art770' in command or 'art 770' in command or 'art 770' in command or 'rs 770' in command or 'rs770' in command)):
        uptime = get_r770ap_uptime()
        speak(f"The Uptime of r770 is {uptime}")

    elif 'what is the ip address of r770' in command or ('ip' in command and ('r770' in command or 'r 770' in command or 'are770' in command or 'are 770' in command or 'art770' in command or 'art 770' in command or 'art 770' in command or 'rs 770' in command or 'rs770' in command)):
        ip_address = get_r770ap_ip_address_wan()
        speak(f"The IP address of r770 is {ip_address}")   

    elif re.search(r'\b(how many (clients|claims|lines) are connected)\b', command):
        speak("Checking for number of connected clients")
        clients = get_r770ap_client_info()    
        speak(f"{clients} clients are connected")

    elif ('ssid' in command or 'society' in command or 'broadcasted' in command) and ('r770' in command or 'r 770' in command or 'are770' in command or 'are 770' in command or 'art770' in command or 'art 770' in command or 'art 770' in command or 'rs 770' in command or 'rs770' in command):
        speak("Checking for ssid")
        ssid = get_r770ap_ssid_info()  
        speak(f"{ssid} is been broadcasted")

    elif 'run zoom call' in command or ('run' in command and 'call' in command):
        # Run zoom server and client in separate threads
        zoom_call_thread = threading.Thread(target=run_zoom_call)
        zoom_call_thread.start()        
                    
    # elif 'connect all clients to' in command or 'connect all claims to' in command or 'connect all trains to' in command:
    #     # Create a separate thread for the connection attempt
    #     connection_thread = threading.Thread(target=handle_connection, args=(command,))
    #     connection_thread.start()
    #     connection_thread.join() 
    #     speak("I'm waiting for your next Instruction")

    if 'connect all clients to' in command or 'connect all claims to' in command or 'connect all trains to' in command:
    # Create a separate thread for the connection attempt
        ssid = get_r770ap_ssid_info()
        speak(f"Connecting all clients to ssid {ssid} please wait for a minute")
        connection_thread = threading.Thread(target=handle_connection, args=(command, ssid))
        connection_thread.start()
        connection_thread.join()
        speak("I'm waiting for your next instruction.")

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

    # elif "lock window" in command or "lock device" in command or "lock computer" in command:
    #     speak("Locking the device")
    #     ctypes.windll.user32.LockWorkStation()

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

    # elif 'volume' in command:
    #     # Notify the user and provide instructions
    #     speak("Here you go. Use your thumb and index finger to control the volume. Be close to the webcam so that you can do it accurately.")

    #     # Start volume control in a new thread
    #     volume_control_thread = threading.Thread(target=control_volume)
    #     volume_control_thread.start()

    elif "open chrome" in command:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        try:
            speak("Opening chrome")
            os.startfile(chrome_path)
        except FileNotFoundError:
            speak("chrome not found")
            print(f"Chrome not found at: {chrome_path}")

    # elif "shutdown" in command:
    #     speak("I am shutting the system down")
    #     os.system('shutdown /s /t 1')
        
    # elif "restart" in command:
    #     speak("Restarting the system now.")
    #     os.system('shutdown /r /t 1')  
    
    # elif "log off" in command or "sign out" in command:
    #     speak("Logging off in 10 seconds.")
    #     subprocess.call(["shutdown", "/l"])
   
    elif "disconnect all clients" in command or "disconnect all claims" in command or "disconnect all planes" in command:
        speak("Attempting to disconnect all clients")
        connection_thread = threading.Thread(target=handle_disconnection, args=(command,))
        connection_thread.start()
        connection_thread.join() 

    elif "take screenshot" in command:
        take_screenshot()

    elif "open recent screenshot" in command or "open the screenshot" in command or "open that screenshot" in command or "open screenshot" in command:
        open_recent_screenshot()
    
    elif "run youtube in" in command and ("clients" in command or "claims" in command or "lines" in command):
        speak("Attempting to run YouTube in specified clients, please wait for a minute.")

        # Send the command in the request body
        url = "http://ip:8000/update_remote_ips/"
        data = {
            "command": command  # Sending the command directly
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # Raise an error for bad responses

            # Handle the response here
            result = response.json()
            print(result)  # Print the result for debugging

            # Check for failed IPs and respond accordingly
            failed_ips = result.get("Failed_IPs", [])
            if failed_ips:
                failed_ips_message = ", ".join(failed_ips)
                speak(f"Running YouTube failed in the following clients: {failed_ips_message}")
            else:
                speak("Successfully ran YouTube in all clients.")
        
        except requests.RequestException as e:
            print(f"An error occurred while processing the request: {str(e)}")
            speak("An error occurred while processing your request.")

    # new
    elif "close youtube in" in command and ("clients" in command or "claims" in command or "lines" in command):
        speak("Attempting to close YouTube in specified clients, please wait for a minute.")

        # Send the command in the request body
        url = "http://ip:8000/update_remote_ips/"
        data = {
            "command": command  # Sending the command directly
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # Raise an error for bad responses

            # Handle the response here
            result = response.json()
            print(result)  # Print the result for debugging

            # Check for failed IPs and respond accordingly
            failed_ips = result.get("Failed_IPs", [])
            if failed_ips:
                failed_ips_message = ", ".join(failed_ips)
                speak(f"Closing YouTube failed in the following clients: {failed_ips_message}")
            else:
                speak("Successfully closed YouTube in all clients.")
        
        except requests.RequestException as e:
            print(f"An error occurred while processing the request: {str(e)}")
            speak("An error occurred while processing your request.")


    # Open Ruckus Analytics
    elif 'open ra' in command or ('open' in command and 'analytics' in command) or 'open array' in command or 'open aare' in command or 'open r a' in command:
        speak("Opening ruckus analytics")
        open_ruckus_analytics()
        print("opened ruckus analytics")

    # Close Ruckus Analytics
    # elif 'close ra' in command or ('close' in command and 'analytics' in command):
    #     close_ruckus_analytics()

    # else:
    #     print(f"Command did not match any predefined options: {command}")
    #     speak(f"You said {command}")
    #     speak("Sorry I'm not yet coded to answer your query")

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
