from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def open_browser():
    username = "user_name"
    password = "pw"

    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--start-maximized') 
    # chrome_options.add_argument('--start-fullscreen')

    # Automatically download and use the latest version of ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    url = "https://auth-aws-uat.ruckuswireless.com/login?referer=%2Foauth%2Fauthorize%3Fresponse_type%3Dcode%26scope%3Dpublic%26state%3DL2FuYWx5dGljcy9hcGkvYXV0aC92MS91c2VyL2xvZ291dA%3D%3D%26layout%3Dai_login%26client_id%3D1F3B62798F4EDDC38CE022F349FCB659AD4C6B6D2F94D137CAC4A04562263FE7%26redirect_uri%3Dhttps%3A%2F%2Fstaging.mlisa.io%2Fanalytics%2Fapi%2Fauth%2Fv1%2Foauth%2Fcallback%26rd%3Dhttps%3A%2F%2Fstaging.mlisa.io%252Fanalytics%252Fapi%252Fauth%252Fv1%252Fuser%252Flogout"
    driver.get(url)

    try:
        # Wait for the username field to be present
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "user_username")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "user_password")))

        # Fill in the fields
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Click the login button (ensure you have the correct ID for the button)
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))  # Replace with actual button ID
        login_button.click()

        time.sleep(5)  # Wait for login to complete

        # Keep the browser open while other processes continue
        while True:
            time.sleep(10)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_browser()
