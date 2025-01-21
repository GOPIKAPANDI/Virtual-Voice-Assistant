import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def play_video(search_query):
    # Initialize Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')

    # Initialize the Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Search on YouTube
    query = "+".join(search_query.split())
    url = f"https://www.youtube.com/results?search_query={query}"
    driver.get(url)
    print(f"Searching YouTube for {search_query}...")
    time.sleep(3)  # Wait for the page to load

    # Click on the first video in the search results
    first_video = driver.find_element(By.XPATH, '//*[@id="video-title"]')
    first_video.click()
    print(f"Playing the first video for {search_query}...")

    speak("Playing video")
    # Keep the browser open and video playing
    while True:
        time.sleep(10)

if __name__ == "__main__":
    import sys
    search_query = sys.argv[1] if len(sys.argv) > 1 else "default search"
    play_video(search_query)
