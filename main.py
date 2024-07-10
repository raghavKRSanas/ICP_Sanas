import json
import time
import downloadApp as dapp
import launchApplication as lapp
from datetime import datetime
import logging
import getConversationID


def readInputValues(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config


# Reading required values
inputData = readInputValues('variable.json')
appPath = inputData['appLocation']
dialerTesting = inputData['dialerTesting']
url = inputData['url']
downloadDir = inputData['downloadDir']
downloadDestination = inputData['downloadDestination']
download = inputData['download']
appDownloadDir = inputData["appDownloadDir"]

# Dailer and respective dailer python file to import and run
files = {
    'Talkdesk': 'talkdesk',
    '8X8': '8X8',
    'AWS': 'awsDailer'
}


def main():
    log_filename = datetime.now().strftime('automation_log_%Y%m%d_%H%M%S.log')
    log_filename = dialerTesting + '_' + log_filename
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])
    logger = logging.getLogger(__name__)

    # appVersion = talkdeskDownloader.getAppVersion()
    # if appVersion:
    #     downloadAppversion = url.split('/')[-1]
    #     if appVersion in downloadAppversion:
    #         logging.info("The app is already installed with same version.")
    #     else:
    #         dapp.downloadApp(url, appDownloadDir)
    #         dapp.installApp(url, appDownloadDir)
    # else:
    #     dapp.downloadApp(url, appDownloadDir)
    #     dapp.installApp(url, appDownloadDir)


    #lapp.cmdlauchApp(appPath)
    importModule = files[dialerTesting]
    dailerPy = __import__(importModule)
    dailerPy.main()
    if dialerTesting == 'Talkdesk' and download:
        #Added sleep time since the recording updation takes 30sec in dailer
        time.sleep(30)
        #log_filename = "Talkdesk_automation_log_20240618_193928.log"
        conversationIDDict = getConversationID.getConversationID(log_filename, dialerTesting)
        import talkdeskDownloader as td
        td.main(conversationIDDict, downloadDir, downloadDestination)

    if dialerTesting == 'AWS' and download:
        # Added sleep time since the recording update takes 30sec in dailer
        time.sleep(30)
        log_filename = "AWS_automation_log_20240703_165656.log"
        conversationIDDict = getConversationID.getConversationID(log_filename, dialerTesting)
        import awsDownloader as ad
        ad.main(conversationIDDict, downloadDir, downloadDestination)


if __name__ == "__main__":
    main()
