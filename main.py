import json
from datetime import datetime
import logging


def readInputValues(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config


#Reading required values
inputData = readInputValues('variable.json')
appPath = inputData['appLocation']
dialerTesting = inputData['dialerTesting']

#Dailer and respective dailer python file to import and run
files = {
    'TalkDesk': 'talkdesk',
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
    importModule = files[dialerTesting]
    dailerPy = __import__(importModule)
    dailerPy.main()


if __name__ == "__main__":
    main()



