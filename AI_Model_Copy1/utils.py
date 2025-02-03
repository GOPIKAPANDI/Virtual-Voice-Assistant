import subprocess
import pyttsx3
import speech_recognition as sr
import os
import datetime
import glob
import urllib.parse
import time
import math
import numpy as np
import pyautogui
import cv2
import psutil
import webbrowser
import requests
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
# from pycaw.pycaw import CLSCTX_ALL
# from pycaw.callbacks import CLSCTX_ALL  # or similar paths
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from cvzone.HandTrackingModule import HandDetector
# from comtypes import CLSCTX_ALL
from selenium.webdriver.common.action_chains import ActionChains
from ap_functions import *
import threading
import paramiko 

# Global driver variable
driver = None

# def speak(text):
#     engine = pyttsx3.init()
#     engine.say(text)
#     # Only run and wait if the engine is not already running
#     if not engine._inLoop:
#         engine.runAndWait()   

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def open_hd_sz():
    subprocess.Popen(['python', 'open_hd_sz.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_intensity_sz():
    subprocess.Popen(['python', 'open_intensity_sz.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_density_sz():
    subprocess.Popen(['python', 'open_density_sz.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_gopika_sz():
    subprocess.Popen(['python', 'open_gopika_sz.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

# Function to search YouTube
def open_youtube_search(search_query):
    subprocess.Popen(['python', 'open_youtube_video.py', search_query], creationflags=subprocess.CREATE_NEW_CONSOLE)


def open_ruckus_analytics():
    # Open the Ruckus Analytics script in a new console
    with open('subprocess_log.txt', 'w') as log_file:
        subprocess.Popen(
            ['python', 'open_ruckus_analytics.py'],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=log_file,
            stderr=log_file
        )
    print("Opened Ruckus Analytics in a new process")        

def run_zoom_call():
    try:
        # Step 1: Open command prompt and run Zoom_Server.py
        requests.post("http://ip:8000/run_zoom_server/")
        speak("Running Zoom Server.")
        
        # Step 2: Wait for 2 seconds
        time.sleep(2)

        # Step 3: Set up Selenium to open Google Chrome and navigate to Zoom auth URL
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        
        # Add this option to ensure the browser stays open
        chrome_options.add_experimental_option("detach", True)

        chrome_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        zoom_auth_url = "https://zoom.us/oauth/authorize?client_id=LHWCUVSaS0OLfvP6XS24HA&response_type=code&redirect_uri=http://localhost:5000/oauth/callback"
        chrome_driver.get(zoom_auth_url)
        # speak("Opening Zoom Authorization URL in Google Chrome.")
        
        # Step 4: Wait for the page to load and then enter credentials
        time.sleep(5)  # Allow the page to load

        email_field = chrome_driver.find_element(By.ID, "email")
        password_field = chrome_driver.find_element(By.ID, "password")
        
        # Fill in email and password
        email_field.send_keys("email_id")  # Enter your email here
        password_field.send_keys("pw")  # Enter your password here
        # speak("Entering credentials.")
        
        # Step 5: Click the sign-in button
        sign_in_button = chrome_driver.find_element(By.ID, "js_btn_login")
        ActionChains(chrome_driver).move_to_element(sign_in_button).click().perform()
        speak("Signing in.")
        
        # Step 6: Wait 5 seconds after sign-in before starting the Zoom client
        # speak("Waiting 5 seconds before running Zoom Client.")
        time.sleep(12)

        # retry_count = 0
        # max_retries = 5
        # while retry_count < max_retries:
        #     time.sleep(5)  # Wait for a few seconds before checking again
            
        #     # Check for reCAPTCHA error
        #     try:
        #         recaptcha_error = chrome_driver.find_element(By.CSS_SELECTOR, 'div[role="alert"]')
        #         if "reCAPTCHA" in recaptcha_error.text:
        #             # If reCAPTCHA error is found, click sign-in again
        #             print("ReCAPTCHA error occurred. Retrying sign-in.")
        #             sign_in_button = chrome_driver.find_element(By.ID, "js_btn_login")
        #             ActionChains(chrome_driver).move_to_element(sign_in_button).click().perform()
        #             retry_count += 1
        #         else:
        #             break
        #     except Exception:
        #         break

        # if retry_count == max_retries:
        #     speak("Failed to sign in after several attempts due to reCAPTCHA errors.")
        #     return
        
        # Step 7: Locate and click the "Allow" button
        try:
            allow_button = chrome_driver.find_element(By.CSS_SELECTOR, 'button[data-ta="allow-button"]')
            ActionChains(chrome_driver).move_to_element(allow_button).click().perform()
            speak("Clicked Allow button.")
        except Exception as e:
            speak("Could not find the Allow button.")
            print(f"Error locating Allow button: {e}")

        time.sleep(30)
        # Step 7: Call Zoom_Client after 5 seconds
        run_zoom_client()

    except Exception as e:
        speak("An error occurred while running the Zoom call setup.")
        print(f"Error: {e}")

def run_zoom_client():
    try:
        # Send HTTP request to run Zoom_Client.py
        requests.post("http://ip:8000/run_zoom_client/")
        speak("Running Zoom Client.")
        print("Zoom setup complete.")
    except Exception as e:
        speak("An error occurred while running the Zoom client.")
        print(f"Error: {e}")

# Function to take a screenshot
def take_screenshot():
    """Take a screenshot and save it in the 'Screenshots' folder."""
    screenshots_folder = 'Screenshots'

    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(screenshots_folder, f'screenshot_{timestamp}.png')

    pyautogui.screenshot(screenshot_path)
    speak("Screenshot taken and saved.")
    print(f"Screenshot saved at: {screenshot_path}")

# Function to open the most recent screenshot
def open_recent_screenshot():
    """Open the most recent screenshot in the 'Screenshots' folder."""
    screenshots_folder = 'Screenshots'
    list_of_files = glob.glob(f'{screenshots_folder}/*.png')  # Get all PNG files in folder

    if not list_of_files:
        speak("No screenshots found.")
        print("No screenshots found.")
        return

    latest_screenshot = max(list_of_files, key=os.path.getctime)
    os.startfile(latest_screenshot)
    speak("Here you go.")
    print(f"Opening: {latest_screenshot}")

# Function to play a song on YouTube
def play_song_on_youtube(song, artist=None):
    """Search and play a song on YouTube."""
    query = song
    if artist:
        query += f" by {artist}"

    speak(f"Searching for {query} on YouTube.")
    print(f"Searching for: {query}")

    # Use Selenium to get the first result's URL
    options = Options()
    options.headless = False  # Run Chrome with a UI
    options.add_argument("start-maximized")  # Start Chrome maximized

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    search_query = urllib.parse.quote(query)
    youtube_search_url = f"https://www.youtube.com/results?search_query={search_query}"
    driver.get(youtube_search_url)

    # Wait for the results to load and click the first video
    try:
        first_result = driver.find_element(By.XPATH, '//*[@id="video-title"]')
        first_result.click()
        speak(f"Playing {query} on YouTube.")
        
        # Keep the browser open without blocking the AI model from listening
        while True:
            # Keeps the browser window open until manually closed
            pass
    except Exception as e:
        speak("Sorry, I couldn't find the video.")
        print(f"Error: {e}")

# def control_volume():
#     # Camera resolution
#     wCam, hCam = 640, 480

#     # Initialize camera
#     cap = cv2.VideoCapture(0)
#     cap.set(3, wCam)
#     cap.set(4, hCam)

#     # Time variable for FPS calculation
#     pTime = 0

#     # Initialize hand detector for volume control
#     detector = HandDetector(detectionCon=0.7)

#     # Initialize audio control
#     devices = AudioUtilities.GetSpeakers()
#     interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#     volume = cast(interface, POINTER(IAudioEndpointVolume))
#     volRange = volume.GetVolumeRange()
#     minVol = volRange[0]
#     maxVol = volRange[1]

#     start_time = time.time()
#     while time.time() - start_time < 10:  # Run for 10 seconds
#         success, img = cap.read()

#         # Find hand and landmark positions
#         hands, img = detector.findHands(img)

#         if hands:
#             lmList = hands[0]["lmList"]

#             if len(lmList) != 0:
#                 x1, y1 = lmList[4][0], lmList[4][1]  # Thumb tip
#                 x2, y2 = lmList[8][0], lmList[8][1]  # Index finger tip
#                 cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

#                 cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
#                 cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
#                 cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
#                 cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

#                 length = math.hypot(x2 - x1, y2 - y1)

#                 # Convert hand distance to volume range
#                 vol = np.interp(length, [50, 200], [minVol, maxVol])
#                 volBar = np.interp(length, [50, 300], [400, 150])
#                 volPer = np.interp(length, [50, 300], [0, 100])

#                 volume.SetMasterVolumeLevel(vol, None)

#                 if length < 50:
#                     cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

#             cv2.rectangle(img, (50, 150), (85, 400), (128, 0, 128), 3)
#             cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 255, 255), cv2.FILLED)
#             cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (128, 128, 128), 3)

#         # FPS calculation
#         cTime = time.time()
#         fps = 1 / (cTime - pTime)
#         pTime = cTime
#         cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 153, 0), 3)

#         cv2.imshow("Img", img)
#         if cv2.waitKey(1) & 0xFF == ord('x'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
