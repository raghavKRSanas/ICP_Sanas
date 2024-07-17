import time
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
import json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import virtualJack as vj
import cpuUsage as cu
import logging
import os

def readInputValues(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config


def permissionAccess():
    preferences = {
        "profile.default_content_setting_values.media_stream_mic": 1  # 1 to allow, 2 to block
    }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", preferences)
    return chrome_options


def ringCentralLogin(driver, userEmail, password):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Sign in']"))).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='credential']"))).send_keys(userEmail)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "// input[ @ id = 'password']"))).send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()


def changeMicrophone(driver, audioInput='Sanas'):
    WebDriverWait(driver, 20).until(
     EC.element_to_be_clickable((By.XPATH, "//span[@class='sc-gKAblj PDDfI settings_border icon']"))).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "// li[@aria-label='Audio']"))).click()
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@id='selectBox-microphoneSource']"))
    )
    dropdown.click()
    options = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located(
            (By.XPATH, "//ul[@class='MuiList-root MuiMenu-list MuiList-padding']/li"))
    )
    try:
        for option in options:
            if audioInput in option.text:
                option.click()
                logging.info("Audio Input is selected as : '{}' ".format(option.text))
                break
    except StaleElementReferenceException:
        logging.info("Exception occurred.")


def closePopUp(driver, xpath):
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath))).click()
        logging.info("Closed pop-up")
    except :
        logging.info("No pop-up message were found")


def dialingNumber(driver, phoneNumber):
    retry = 1
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='sc-gKAblj PDDfI phone_border icon']"))).click()
    except:
        logging.info("Going to exception for clicking phone icon")
        driver.find_element(By.XPATH, "//span[@class='sc-gKAblj PDDfI phone icon']").click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='PHONE_DIALER_INPUT_ID']"))).send_keys(
        phoneNumber)
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='MuiListItemText-root sc-jOFreG dgxyXt MuiListItemText-multiline RcListItemText-multiline']"))).click()
        logging.info("Call has been initiated to {} waiting for receiver".format(phoneNumber))
        return True
    except:
        if retry > 0:
            retry -= 1
            logging.info("Call not initiated properly. Retrying again.")
            dialingNumber(driver, phoneNumber)
        else:
            logging.info("Call not initiated after Retry")
            return False


def changeWindows(driver, windowReq=None):
    if windowReq:
        driver.switch_to.window(windowReq)
    else:
        original_window = driver.current_window_handle
        logging.info("Current window : {} ".format(original_window))
        all_windows = driver.window_handles
        for window in all_windows:
            if window != original_window:
                logging.info("Switched to window : {}".format(window))
                driver.switch_to.window(window)
                break
    driver.maximize_window()



def checkForRecieve(driver):
    status = 0
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    changeWindows(driver)
    for i in range(3):
        try:
            WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Record the call']"))).click()
            time.sleep(2)
            try:
                driver.find_element(By.XPATH, "//button[@data-test-automation-id='telephony-stop-record-menu-item']")
                status = 1
                logging.info("Recording started at {} try ".format(i+1))
                return status
            except:
                logging.info("Not able to record the call. Retrying again after 5 seconds")
                time.sleep(5)
        except:
            logging.info("Record Element not found. Retrying again")
    return status


def callStart(driver, phoneNumber, receiverBufferTime=15):
    original_window = driver.current_window_handle
    logging.info("In window : {} ".format(original_window))
    if not dialingNumber(driver, phoneNumber):
        return False
    time.sleep(receiverBufferTime)
    status = checkForRecieve(driver)
    if status:
        logging.info("Call has been received at receivers end")
        return True
    else:
        logging.info("Call was not successfully made.")
        return False



def callEnd(driver):
    original_window = driver.current_window_handle
    logging.info("In window : {} ".format(original_window))
    WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-test-automation-id='telephony-end-btn']"))).click()
    time.sleep(3)


inputData = readInputValues('variable.json')
userEmail = inputData['RingCentral']['userEmail']
password = inputData['RingCentral']['password']
audioInput = inputData['RingCentral']['audioInput']
phoneNumber = inputData['RingCentral']['phoneNumber']
directory_path = inputData['directory_path']
appPath = inputData['appLocation']
overRidingSession = inputData['RingCentral']['newSession']
numberRetryCalls = inputData['RingCentral']['numberRetryCalls']
receiverBufferTime = inputData['RingCentral']['receiverBufferTime']

def main():
    # Configuration setup
    vac_device_id = int(vj.list_sound_devices())
    wav_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.wav')]
    chrome_options = permissionAccess()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://app.ringcentral.com/")
    driver.maximize_window()
    Mainwindow = driver.current_window_handle

    # Ring Central Login
    ringCentralLogin(driver, userEmail, password)
    closePopUp(driver, "//button[contains(@class, 'onetrust-close-btn-handler') and contains(@class, 'banner-close-button') and contains(@class, 'ot-close-link') and text()='Continue without Accepting']")
    # Selecting Input Microphone
    changeMicrophone(driver, audioInput)

    for file in wav_files:
        for i in range(numberRetryCalls):
            if callStart(driver, phoneNumber, receiverBufferTime):
                time.sleep(1)
                vj.play_audio_files_to_vac(file, vac_device_id)
                logging.info(f"audio played in location {file}")
                logging.info("Audio file ended.")
                logging.info("Ending the call.")
                callEnd(driver)
                changeWindows(driver, Mainwindow)
                try:
                    driver.find_element(By.XPATH, "//span[@class='MuiButton-label' and text()='Cancel']").click()
                except:
                    logging.info("Call rating button was not found which is can be ignored")
                break
            else:
                callEnd(driver)
                changeWindows(driver, Mainwindow)
                try:
                    driver.find_element(By.XPATH, "//span[@class='MuiButton-label' and text()='Cancel']").click()
                except:
                    logging.info("Call rating button was not found which is can be ignored")
                continue

    driver.quit()


if __name__ == "__main__":
    main()
