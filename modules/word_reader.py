from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys, time

def automate_ipa_reader(ipa_text, voice='Gwyneth', browser=None):
    if(not browser):
        browser = webdriver.Chrome()  # Substitute with your preferred WebDriver, e.g. webdriver.Chrome()
    url = f'http://ipa-reader.xyz/?text={ipa_text}&voice={voice}'
    browser.get(url)

    # You may need to modify the following line to ensure that
    # the play_animate_button is correctly identified.
    play_animate_button = WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.ID, "submit")))

    play_animate_button.click()  
    # give some time for browser to load and play the sound
    
    return browser

def command_line():
    word = sys.argv[1]
    if(word):
        browser = automate_ipa_reader(word)
        time.sleep(6)
        browser.quit()
        
if(__name__ == '__main__'):
    command_line()