import time
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
import json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import virtualJack as vj
import logging
import os
import changeMicrophone as cm


def readInputValues(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config


def permissionAccess():
    preferences = {
        "profile.default_content_setting_values.media_stream_mic": 1  # 1 to allow, 2 to block
    }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("prefs", preferences)
    return chrome_options


def awsLogin(driver,userEmail,password):
    for count in range(4):
        try:
            if count == 3:
                logging.error("Login Unsuccessful after 3 Retries")
                return
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='wdc_username']"))).send_keys(userEmail)
            driver.find_element(By.XPATH, "//input[@id='wdc_password']").send_keys(password)
            driver.find_element(By.XPATH, "//button[@id='wdc_login_button']").click()
            logging.info("Login Successful")
            return
        except (NoSuchElementException, TimeoutException):
            logging.info("Due to exceptions not able to Login")



def callStart(driver,phoneNumber):
    global numberRetryCalls
    try:
        driver.find_element(By.XPATH, "//input[@type='text']").send_keys(phoneNumber)
        driver.find_element(By.XPATH, "//div[normalize-space()='Call']").click()
        callStatus = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='connectionTab-primary-status']")))
        mode = None
        while True:
            if "Connecting" in callStatus.text:
                if mode != "Connecting":
                    logging.info("Call has been initiated to {} waiting for receiver".format(phoneNumber))
                    mode = "Connecting"
            if "Connected call" in callStatus.text:
                logging.info("Call has been received at receivers end")
                mode = "Connected call"
                return mode
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
        numberRetryCalls -= 1
        if numberRetryCalls <= 0:
            logging.error("Could not proceed after Retries also")
            return None
        else:
            logging.info("Retrying to call due to Time-out or Element not found exception .Retries left {} ".format(
                numberRetryCalls))
            callStart(driver, phoneNumber)


def callEnd(driver):
    logging.info("Ending Call now")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='End call']"))).click()
    time.sleep(5)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Close contact']"))).click()


def createNewSession(driver, newSession=True):
    if newSession:
        try:
            if WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Close contact']"))):
                logging.info("Starting with New session ")
                for i in range(2):
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Close contact']"))).click()
        except (NoSuchElementException, TimeoutException):
            logging.info("No need to start new session")


# Reading all values from json file
inputData = readInputValues('variable2.json')
directory_path = inputData['directory_path']
appPath = inputData['appLocation']
userEmail = inputData['AWS']['userEmail']
password = inputData['AWS']['password']
audioInput = inputData['AWS']['audioInput']
phoneNumber = inputData['AWS']['phoneNumber']
numberRetryCalls = inputData['AWS']['numberRetryCalls']
newSession = inputData['AWS']['newSession']


def main():
    # Configuration setup
    vac_device_id = int(vj.list_sound_devices())
    wav_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.wav')]
    chrome_options = permissionAccess()
    driver = webdriver.Chrome(options=chrome_options)
    cm.changeMicrophone(driver)
    driver.get("https://sanas-connect.my.connect.aws/users#/edit")

    #AWS Login
    awsLogin(driver, userEmail, password)

    #Opening Dailer Window
    shadowObj = driver.find_element(By.CSS_SELECTOR, '[class="lily-icon-logo"]').shadow_root
    obj = shadowObj.find_element(By.CSS_SELECTOR, "a[target='ContactControlPanel']")
    obj.click()
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    original_window = driver.current_window_handle
    all_windows = driver.window_handles
    for window in all_windows:
        if window != original_window:
            driver.switch_to.window(window)
            break
    driver.maximize_window()
    createNewSession(driver, newSession)
    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Number pad']"))).click()

    #Starting and Ending Call
    for file in wav_files:
        mode = callStart(driver, phoneNumber)
        if mode == "Connected call":
            logging.info("Audio file started playing")
            vj.play_audio_files_to_vac(file, vac_device_id)
            logging.info(f"audio played in location {file}")
            logging.info("Audio file ended.")
            callEnd(driver)

    driver.quit()

def convertTable(table_con):
    table_dict = {}
    for tbody in table_con:
        rows = tbody.find_elements(By.CSS_SELECTOR, "tr")
        for row in rows:
            cols = row.find_elements(By.CSS_SELECTOR, "td")
            # Ensure there are at least two columns to use since the second column is the download file name
            if len(cols) >= 2:
                key = cols[1].text  # Column 2 as key
                value = [col.text for i, col in enumerate(cols) if i != 1]  # Rest of the row as value
                table_dict[key] = value
    return table_dict


def downloadAudio(driver):
    driver.get("https://sanas-connect.my.connect.aws/users#/edit")
    awsLogin(driver, userEmail, password)
    time.sleep(5)
    ele1 = driver.find_element(By.CSS_SELECTOR, "lily-navigation").shadow_root
    ele1.find_element(By.CSS_SELECTOR, "li[title='Analytics and optimization']").click()
    ele1.find_element(By.CSS_SELECTOR, "a[title='Contact search']").click()
    time.sleep(5)
    ele1 = driver.find_element(By.CSS_SELECTOR, "contact-search-page").shadow_root
    ele2 = ele1.find_element(By.CSS_SELECTOR, 'div > div:nth-of-type(1)').shadow_root
    ele6 = ele2.find_element(By.CSS_SELECTOR, "contact-search-table-widget[data-testid='search-results__table']").shadow_root
    ele6.find_element(By.CSS_SELECTOR, "button[aria-label='Download recording']").click()
    name = ele6.find_element(By.CSS_SELECTOR, "a").text
    logging.info("Downloaded")
    table_con = ele6.find_elements(By.CSS_SELECTOR, "tbody[role='rowgroup']")
    callDetails = convertTable(table_con)
    print("Call details for the downloaded file {} is  {}  ".format(name, callDetails[name]))
    driver.quit()


if __name__ == "__main__":
    main()
