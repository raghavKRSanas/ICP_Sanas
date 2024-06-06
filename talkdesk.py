import time
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
import json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import virtualJack as vj
import cpuUsage as cu
import functools
import logging
import os
from datetime import datetime

log_filename = datetime.now().strftime('automation_log_%Y%m%d_%H%M%S.log')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])

logger = logging.getLogger(__name__)


def trackCPUUsage(before=True, after=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if before:
                pid, cpu_usage = cu.appCpuUsage()
                print(f"CPU usage before {func.__name__} is {cpu_usage} with pid: {pid}")
            result = func(*args, **kwargs)
            if after:
                time.sleep(2)
                pid, cpu_usage = cu.appCpuUsage()
                print(f"CPU usage after {func.__name__} is {cpu_usage} with pid: {pid}")
            return result
        return wrapper
    return decorator


def permissionAccess():
    preferences = {
        "profile.default_content_setting_values.media_stream_mic": 1  # 1 to allow, 2 to block
    }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", preferences)
    return chrome_options


def iframeHandler(driver, title=None, default=False):
    time.sleep(7)
    if title:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for frame in iframes:
            if frame.get_attribute("title") == title:
                driver.switch_to.frame(frame)
                logging.info("Switching to iframe : {}".format(title))
                break
    if default:
        driver.switch_to.default_content()
        logging.info("Switching to iframe : Default")


@trackCPUUsage(before=True, after=True)
def dropDownSelection(driver, cssSelector, selectText):
    elements = driver.find_elements(By.CSS_SELECTOR, cssSelector)
    for ele in elements:
        try:
            if selectText in ele.text:
                ele.click()
                logging.info("{} is selected as input microphone".format(ele.text))
                return
        except StaleElementReferenceException:
            time.sleep(1)  # Wait a bit before retrying
            ele.click()
            return


def readInputValues(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config


def callEndDismiss(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//i[normalize-space()='close_outline']"))).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Yes, dismiss')]"))).click()
    except (NoSuchElementException, TimeoutException):
        logging.exception("Submit dialogue box was not visible while ending the call (Differs from User to User)")
    iframeHandler(driver, default=True)


@trackCPUUsage(before=False, after=True)
def callEnd(driver):
    iframeHandler(driver, title='Conversations')
    WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//i[normalize-space()='call_end']"))).click()
    callEndDismiss(driver)


def dailingNumber(driver, phoneNumber):
    iframeHandler(driver, title='Conversations')
    global numberRetryCalls
    while True:
        try:
            driver.find_element(By.XPATH, "//input[@placeholder='Type or paste a number']").send_keys(phoneNumber + Keys.RETURN)
            callStatus = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//p[@data-testid='call-state-text']")))
            mode = None
            while True:
                if "Dialing" in callStatus.text:
                    if mode != "Dialing":
                        logging.info("Call has been initiated to {} waiting for receiver".format(phoneNumber))
                        mode = "Dialing"
                if "Talking" in callStatus.text:
                    logging.info("Call has been received at receivers end")
                    numberRetryCalls = 3
                    return
                if "Wrap-up" in callStatus.text:
                    logging.info("Call was not received . Number of Retrys left: {}".format(numberRetryCalls))
                    if numberRetryCalls > 0:
                        numberRetryCalls -= 1
                        callEndDismiss(driver)
                        callStart(driver, phoneNumber, overRidingSession=False)
                    return
        except:
            if numberRetryCalls > 0:
                numberRetryCalls -= 1
                logging.error("Dailing number {} Failed due exception cases. Number of Retrys left {}".format(phoneNumber,numberRetryCalls))
                callEndDismiss(driver)
                callStart(driver, phoneNumber, overRidingSession=True)


def popUpClose(driver):
    try:
        driver.find_element(By.XPATH,
                            "(//i[contains(@class,'react-icon_1-10-2_co-icon react-icon_1-10-2_co-icon--small')])[6]").click()

    except :
        logging.info("Pop up not found")


def createNewSession(driver, overRidingSession=True):
    try:
        if overRidingSession:
            iframeHandler(driver, title='Conversations')
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Start new session']"))).click()
            logging.info("Started new Session since it was used on other system")
            iframeHandler(driver, default=True)
            popUpClose(driver)
    except (NoSuchElementException,TimeoutException):
        logging.info("No Session is logged in before")

def getConversationID(driver):
    #iframeHandler(driver, title='Conversations')
    for count in range(2):
        try:
            conversationID = driver.find_element(By.XPATH, "//span[@data-bi='snapshot-tab-conversation-details-card"
                                                               "-interaction_id']").text
            return conversationID
        except NoSuchElementException:
            logging.error("Caller Recording ID not found.")
    #iframeHandler(driver, default=True)


@trackCPUUsage(before=True, after=False)
def callStart(driver, phoneNumber, overRidingSession=True):
    conversationID = None
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Conversations']"))).click()
    createNewSession(driver, overRidingSession)
    dailingNumber(driver, phoneNumber)
    conversationID = getConversationID(driver)
    return conversationID


def talkdeskLogin(driver, userEmail, password):
    for count in range(3):
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='email@company.com']"))).send_keys(userEmail)
        driver.find_element(By.XPATH, "//input[@placeholder='password']").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        try:
            if driver.find_element(By.XPATH, "//div[@class='co-message__content']"):
                logging.info("Trying to Log in for {} time".format(count + 1))
            if count == 2:
                logging.error("Login Unsuccessful")
                return
        except:
            logging.info("Login Successful")
            return

def downloadRecording(driver, conversationID):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Activities']"))).click()


# Reading all values from json file
inputData = readInputValues('variable.json')
userEmail = inputData['Talkdesk']['userEmail']
password = inputData['Talkdesk']['password']
audioInput = inputData['Talkdesk']['audioInput']
countryCode = inputData['Talkdesk']['countryCode']
phoneNumber = inputData['Talkdesk']['phoneNumber']
directory_path = inputData['directory_path']
appPath = inputData['appLocation']
overRidingSession = inputData['Talkdesk']['newSession']
numberRetryCalls = inputData['Talkdesk']['numberRetryCalls']


def main():
    # Configuration setup
    vac_device_id = int(vj.list_sound_devices())
    wav_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.wav')]
    chrome_options = permissionAccess()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://sanasai.talkdeskid.com/login")

    # Talkdesk Login
    talkdeskLogin(driver, userEmail, password)
    driver.implicitly_wait(5)

    # Microphone configuration setup
    driver.find_element(By.XPATH, "//button[@class='react-avatar_1-3-0_co-avatar--clickable']").click()
    driver.find_element(By.XPATH, "//p[normalize-space()='Conversations Settings']").click()
    iframeHandler(driver, title='conversation-settings')
    driver.find_element(By.XPATH,
                        "//span[@class='react-typography_1-4-1_co-text react-typography_1-4-1_co-text--medium "
                        "react-typography_1-4-1_co-text--weight-regular "
                        "react-typography_1-4-1_co-text--truncated']").click()
    dropDownSelection(driver, cssSelector="li[class='react-list_1-1-7_co-list__item'] a", selectText=audioInput)
    iframeHandler(driver, default=True)
    driver.implicitly_wait(5)

    # Dialer setup
    for file in wav_files:
        conversationID = callStart(driver, phoneNumber)
        if conversationID:
            logging.info("Audio file started playing")
            vj.play_audio_files_to_vac(file, vac_device_id)
            logging.info(f"audio played in location {file} and conversation ID is {conversationID}")
            logging.info("Audio file ended.")
            logging.info("Ending the call.")
            callEnd(driver)
            #downloadRecording()
    driver.quit()


if __name__ == "__main__":
    main()
