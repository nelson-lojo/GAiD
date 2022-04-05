from selenium.webdriver import Chrome, ChromeOptions
from time import sleep as wait


url = f"google.com"

options = ChromeOptions()
options.add_argument('headless')
with Chrome(options=options) as browser:

    browser.get(url)
    
    wait(secs=2)

    browser.save_screenshot('bruh.png')





