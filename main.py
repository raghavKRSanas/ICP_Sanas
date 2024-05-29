import json
import launchApplication as lapp


def readInputValues(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

#Reading required values
inputData = readInputValues('variable2.json')
appPath = inputData['appLocation']
dailerTesting = inputData['dailerTesting']

#Dailer and respective dailer python file to import and run
files = {
    'TalkDesk': 'talkdesk'
}


def main():
    lapp.launchAPP(appPath)
    importModule = files[dailerTesting]
    dailerPy = __import__(importModule)
    dailerPy.main()


if __name__ == "__main__":
    main()



