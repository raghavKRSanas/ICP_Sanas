import time
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
import json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import virtualJack as vj
import cpuUsage as cu
import functools
import os


def trackCPUUsage(before=True, after=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if before:
                pid, cpu_usage = cu.appCpuUsage()
                print(f"CPU usage before {func.__name__} is {cpu_usage} with pid: {pid}")
            result = func(*args, **kwargs)
            if after:
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
    time.sleep(15)
    if title:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for frame in iframes:
            if frame.get_attribute("title") == title:
                driver.switch_to.frame(frame)
                break
    if default:
        driver.switch_to.default_content()


@trackCPUUsage(before=True, after=True)
def dropDownSelection(driver, cssSelector, selectText):
    elements = driver.find_elements(By.CSS_SELECTOR, cssSelector)
    for ele in elements:
        try:
            if selectText in ele.text:
                ele.click()
                return
        except StaleElementReferenceException:
            time.sleep(1)  # Wait a bit before retrying
            ele.click()
            return


def readInputValues(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config


@trackCPUUsage(before=True, after=True)
def callEnd(driver):
    iframeHandler(driver, title='Conversations')
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//i[normalize-space()='call_end']"))).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//i[normalize-space()='close_outline']"))).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Yes, dismiss')]"))).click()
    except (NoSuchElementException, TimeoutException):
        print("Exception: Submit dialogue box was not visible while ending the call (Differs from User to User)")
    iframeHandler(driver, default=True)


@trackCPUUsage(before=True, after=True)
def callStart(driver, countryCode, phoneNumber):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Conversations']"))).click()
    iframeHandler(driver, title='Conversations')
    driver.find_element(By.XPATH, "//span[@class='co-list__item-content'][normalize-space()='+1']").click()
    driver.find_element(By.XPATH, "//input[@placeholder='Type or paste a number']").send_keys(phoneNumber)
    driver.find_element(By.XPATH, "//button[@class='react-button_1-3-0_co-button react-button_1-3-0_co-button--primary "
                                  "react-button_1-3-0_co-button--medium react-button_1-3-0_co-button--full-width']").click()
    driver.implicitly_wait(5)
    callStart = 0
    while callStart == 0:
        callStatus = driver.find_element(By.XPATH, "//p[@data-testid='call-state-text']").text
        if "Talking" in callStatus:
            callStart = 1
    conversationID = driver.find_element(By.XPATH, "//span[@data-bi='snapshot-tab-conversation-details-card"
                                                   "-interaction_id']").text
    iframeHandler(driver, default=True)
    return conversationID


# Reading all values from json file
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


# Talkdesk Login
WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='email@company.com']"))).send_keys(userEmail)
driver.find_element(By.XPATH, "//input[@placeholder='password']").send_keys(password)
driver.find_element(By.XPATH, "//button[@type='submit']").click()
driver.implicitly_wait(5)

# Microphone configuration setup
driver.find_element(By.XPATH, "//button[@class='react-avatar_1-3-0_co-avatar--clickable']").click()
driver.find_element(By.XPATH, "//p[normalize-space()='Conversations Settings']").click()
iframeHandler(driver, title='conversation-settings')
driver.find_element(By.XPATH, "//span[@class='react-typography_1-4-1_co-text react-typography_1-4-1_co-text--medium "
                              "react-typography_1-4-1_co-text--weight-regular "
                              "react-typography_1-4-1_co-text--truncated']").click()
dropDownSelection(driver, cssSelector="li[class='react-list_1-1-7_co-list__item'] a", selectText=audioInput)
iframeHandler(driver, default=True)
driver.implicitly_wait(15)


# Dialer setup
for file in wav_files:
    conversationID = callStart(driver, countryCode, phoneNumber)
    vj.play_audio_files_to_vac(file, vac_device_id)
    print(f"audio played in location {file} and conversation ID is {conversationID}")
    callEnd(driver)

driver.quit()
