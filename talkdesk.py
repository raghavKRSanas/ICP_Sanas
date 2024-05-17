import time
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import json
import virtualJack as vj
import os


def permissionAccess():
    preferences = {
        "profile.default_content_setting_values.media_stream_mic": 1  # 1 to allow, 2 to block
    }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", preferences)
    return chrome_options


def iframeHandler(driver, title=None, default=None):
    if title != None:
        iframe = driver.find_elements(By.TAG_NAME, "iframe")
        for frame in iframe:
            if frame.get_attribute("title") == title:
                iframe = frame
                break
        driver.switch_to.frame(iframe)
    if default:
        driver.switch_to.default_content()


def dropDownSelection(driver, cssSelector, selectText):
    elements = driver.find_elements(By.CSS_SELECTOR, cssSelector)
    for ele in elements:
        if selectText in ele.text:
            ele.click()


def readInputValues(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config


def callEnd(driver):
    iframeHandler(driver, title='Conversations')
    time.sleep(5)
    driver.find_element(By.XPATH, "//i[normalize-space()='call_end']").click()
    time.sleep(5)
    try:
        driver.find_element(By.XPATH, "//i[normalize-space()='close_outline']").click()
        time.sleep(5)
        driver.find_element(By.XPATH, "//span[contains(text(),'Yes, dismiss')]").click()
    except NoSuchElementException:
        print("Sumbmit dailogue box was not visible")
    iframeHandler(driver, default=True)
    time.sleep(5)


def callStart(driver, countryCode, phoneNumber):
    driver.find_element(By.XPATH, "//button[@aria-label='Conversations']").click()
    time.sleep(15)
    iframeHandler(driver, title='Conversations')
    driver.find_element(By.XPATH, "//span[@class='co-list__item-content'][normalize-space()='+1']").click()
    time.sleep(2)
    countryCodeXpath = "//span[normalize-space()='" + countryCode + "']"
    driver.find_element(By.XPATH, countryCodeXpath).click()
    driver.find_element(By.XPATH, "//input[@placeholder='Type or paste a number']").send_keys(phoneNumber)
    driver.find_element(By.XPATH, "//button[@class='react-button_1-3-0_co-button react-button_1-3-0_co-button--primary "
                                  "react-button_1-3-0_co-button--medium react-button_1-3-0_co-button--full-width']").click()
    time.sleep(10)
    conversationID = driver.find_element(By.XPATH, "//span[@data-bi='snapshot-tab-conversation-details-card"
                                                   "-interaction_id']").text
    print(conversationID)
    iframeHandler(driver, default=True)
    return conversationID


#Reading all values from json file
inputData = readInputValues('variable.json')
userEmail = inputData['userEmail']
password = inputData['password']
audioInput = inputData['audioInput']
countryCode = inputData['countryCode']
phoneNumber = inputData['phoneNumber']
directory_path = inputData['directory_path']

# Configuration setup
vac_device_id = int(vj.list_sound_devices())
wav_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.wav')]
chrome_options = permissionAccess()
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://sanasai.talkdeskid.com/login")
time.sleep(5)

#Talkdesk Login
driver.find_element(By.XPATH, "//input[@placeholder='email@company.com']").send_keys(userEmail)
driver.find_element(By.XPATH, "//input[@placeholder='password']").send_keys(password)
driver.find_element(By.XPATH, "//button[@type='submit']").click()
time.sleep(20)

#Microphone configuration setup
driver.find_element(By.XPATH, "//button[@class='react-avatar_1-3-0_co-avatar--clickable']").click()
driver.find_element(By.XPATH, "//p[normalize-space()='Conversations Settings']").click()
time.sleep(10)
iframeHandler(driver, title='conversation-settings')
driver.find_element(By.XPATH, "//span[@class='react-typography_1-4-1_co-text react-typography_1-4-1_co-text--medium "
                              "react-typography_1-4-1_co-text--weight-regular "
                              "react-typography_1-4-1_co-text--truncated']").click()
dropDownSelection(driver, cssSelector="li[class='react-list_1-1-7_co-list__item'] a", selectText=audioInput)
iframeHandler(driver, default=True)
time.sleep(15)

#Dailer setup

for file in wav_files:
    conversationID = callStart(driver, countryCode, phoneNumber)
    vj.play_audio_files_to_vac(file, vac_device_id)
    print("audio played in location {} and conversation ID is {} ".format(file, conversationID))
    callEnd(driver)

driver.quit()
