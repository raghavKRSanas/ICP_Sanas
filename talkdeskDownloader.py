from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import logging
import os
from datetime import datetime
import unzipStore as us
import winapps
import sys


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


def talkdeskLogin(driver, userEmail, password):
    for count in range(3):
        driver.get("https://sanasai.talkdeskid.com/login")
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
        iframeHandler(driver, default=True)
        logging.info("No Session is logged in before")


def permissionAccess(download_dir):
    preferences = {
        "download.default_directory": download_dir,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,  # To bypass safe browsing warnings
        "profile.default_content_setting_values.media_stream_mic": 1  # 1 to allow, 2 to block
    }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", preferences)
    return chrome_options


def getAppVersion():
    for app in winapps.list_installed():
        if "Sanas Accent Translator" in app.name:
            #print(f"Name: {app.name}, Version: {app.version}")
            return app.version


def getModelVersion():
    folder_path = "C:\\Program Files\\Sanas.ai\\Sanas Accent Translator\\Models"
    file_name_without_extension = ''
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        file_names = os.listdir(folder_path)
        file_name_without_extension = os.path.splitext(file_names[0])[0]
    else:
        logging.error("The specified folder does not exist or is not a directory.")
    return file_name_without_extension

def popUpClose(driver):
    try:
        driver.find_element(By.XPATH,
                            "(//i[contains(@class,'react-icon_1-10-2_co-icon react-icon_1-10-2_co-icon--small')])[6]").click()
    except (NoSuchElementException,TimeoutException):
        logging.info("Pop up not found")


def main(conversationIDDict, downloadDir, downloadDestination):
    log_filename = datetime.now().strftime('automation_log_%Y%m%d_%H%M%S.log')
    log_filename = 'Talkdesk_Download_' + log_filename
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])

    if not os.path.exists(downloadDir):
        os.makedirs(downloadDir)
    chrome_options = permissionAccess(downloadDir)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    talkdeskLogin(driver, "namrata@sanas.ai", "Sanas@123")
    # Navigate to the specified URL
    driver.maximize_window()
    time.sleep(10)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Conversations']"))).click()
    createNewSession(driver)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Activities']"))).click()

    try:
        time.sleep(10)
        iframeHandler(driver, "Activities")
        conversationIDList  = list(conversationIDDict.keys())
        boundNum = 2*len(conversationIDList)
        while conversationIDList:
            for i in range(10):
                retry = 3
                while retry > 0:
                    xpath = '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[4]/table[1]/tbody[1]/tr[' + str(
                        i + 1) + ']/td[2]/div[1]/p[1]'
                    elements = driver.find_element(By.XPATH, xpath)
                    elements.click()
                    time.sleep(5)
                    try:
                        conversation = driver.find_element(By.XPATH,
                                                          "/html/body/div/div/div[2]/div/div[3]/div/div/div[3]/div/div[1]/table/tbody/tr[8]/td/div/div[1]/div/div/div/p").text

                        boundNum -= 1
                        retry = 0
                        if conversation in conversationIDList:
                            driver.find_element(By.XPATH, "//i[normalize-space()='download']").click()
                            logging.info("Downloaded file for conversation ID {} for the source {} ".format(conversation,
                                                                                                           conversationIDDict[conversation]))
                            time.sleep(3)
                            appVersion = getAppVersion()
                            modelVersion = getModelVersion()
                            newName = conversationIDDict[conversation] + "_appVersion_" + appVersion + "_modelVersion_" + modelVersion
                            us.unzip_latest_folder(downloadDir, downloadDestination, newName)
                            conversationIDList.remove(conversation)
                    except NoSuchElementException:
                        logging.info("conversation ID was not found")
                        retry -= 1
                    try:
                        driver.find_element(By.XPATH, "//i[normalize-space()='close']").click()
                    except:
                        driver.find_element(By.XPATH, "//i[normalize-space()='close']").click()
                        logging.info("Close is not found ")
                    finally:
                        if boundNum == 0:
                            for ele in conversationIDList:
                                logging.error("{} file with conversation ID {} was not found".format(conversationIDDict[ele], ele))
                            driver.quit()
                            sys.exit()
                        if not conversationIDList:
                            logging.info("Downloaded all files")
                            driver.quit()
                            sys.exit()
                    time.sleep(5)
            # Next page
            driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div[6]/div[1]/nav/a[2]/span[1]").click()
            time.sleep(3)
        driver.quit()
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error("failed due to no element exception")


# if __name__ == "__main__":
#     conversationIDList = {'BNS_429_9_Sneha_128BF_VERYLOW_Female_IN-Hindi_1714467721784.wav': 'effc16b4d9c44be5aa8bd7b8c52c9afd', 'Recognizer_Geetha_VeryNoisy_100db_Normal_Telekonnectors_Female_IN-Tamil_1706687306038.wav': 'eef0321b11ac4ed1b5f138ac4f4b8b6b'}
#     downloadDir = r"C:\Users\RaghavKR\Downloads\recordings"
#     main(conversationIDList, downloadDir)
