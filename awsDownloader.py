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
import talkdeskDownloader as td


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


def main(conversationIDDict, downloadDir, downloadDestination):
    log_filename = datetime.now().strftime('automation_log_%Y%m%d_%H%M%S.log')
    log_filename = 'AWS_Download_' + log_filename
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])

    if not os.path.exists(downloadDir):
        os.makedirs(downloadDir)
    chrome_options = permissionAccess(downloadDir)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://sanas-connect.my.connect.aws/users#/edit")
    awsLogin(driver, userEmail='Raghav', password='Sanas@123')
    time.sleep(10)
    driver.maximize_window()
    for id,fileName in conversationIDDict.items():
        downloadURL = 'https://sanas-connect.my.connect.aws/contact-search/api/contact/' + str(id) + '/recording'
        driver.get(downloadURL)
        time.sleep(5)
        appVersion = td.getAppVersion()
        modelVersion = td.getModelVersion()
        newName = conversationIDDict[id] + "_appVersion_" + appVersion + "_modelVersion_" + modelVersion
        us.rename_and_move_latest_file(downloadDir, downloadDestination, newName, '.mp3')
        logging.info("Downloaded synth file for source file :{} with ID {} stored in {} with name {} ".format(fileName, id, downloadDestination, newName))
