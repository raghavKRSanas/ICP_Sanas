import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




def changeMicrophone(driver):
    # Configure Chrome options

    try:
        # Open Chrome microphone settings page
        driver.get('chrome://settings/content/microphone?search=microphone')

        # Wait for the settings page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "settings-ui")))

        shadow_host = driver.find_element(By.TAG_NAME, 'settings-ui')
        shadow_root = shadow_host.shadow_root

        main_page = shadow_root.find_element(By.CSS_SELECTOR, 'settings-main')
        main_shadow_root = main_page.shadow_root

        basic_page = main_shadow_root.find_element(By.CSS_SELECTOR, 'settings-basic-page')
        basic_shadow_root = basic_page.shadow_root

        privacy_page = basic_shadow_root.find_element(By.CSS_SELECTOR, 'settings-privacy-page')
        privacy_shadow_root = privacy_page.shadow_root
        time.sleep(4)

        microphone_settings = privacy_shadow_root.find_element(By.CSS_SELECTOR, "media-picker[type='mic']")
        microphone_shadow_root = microphone_settings.shadow_root

        dropdown_element = microphone_shadow_root.find_elements(By.CSS_SELECTOR, "#mediaPicker")

        for option in dropdown_element:
            if "Sanas" in option.text:
                option.click()
                break


    except:
        logging.info("Due to exception, microphone settings was not set")

