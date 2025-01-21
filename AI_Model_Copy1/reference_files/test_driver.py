from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def test_driver():
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')

    service = Service('C:\\webdrivers\\chromedriver.exe')  # Update with the correct path to your WebDriver

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("http://www.google.com")
    
    print("Google page opened successfully.")
    driver.quit()

if __name__ == "__main__":
    test_driver()
