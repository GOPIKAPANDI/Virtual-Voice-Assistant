import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def open_browser():
    # Use predefined username and password
    username = "un"
    password = "pw"

    # Set Chrome options to ignore SSL certificate errors
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')

    # Specify the path to the WebDriver executable
    service = Service('C:\\webdrivers\\chromedriver.exe')  # Update with the correct path to your WebDriver

    # Initialize the Selenium WebDriver with the specified service and options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the browser and navigate to the login page
    url = "https://ip:8443/cas/login?service=%2Fwsg%2Flogin%2Fcas#m"
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
        time.sleep(7)

        driver.get("https://ip:8443/wsg/#m/accessPoint")
        # Keep the browser open
        while True:
            time.sleep(10)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_browser()
