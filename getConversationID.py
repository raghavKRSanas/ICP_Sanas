import re


def getConversationID(file_path, dailer):
    file_location_conversation_id = {}
    if dailer == 'Talkdesk':
        file_location_pattern = r'location\s+(.*?)\s+and\s+conversation\s+ID\s+is\s+(.*?)$'
        with open(file_path) as file:
            log_text = file.read()
            matches = re.findall(file_location_pattern, log_text, re.MULTILINE)
            for match in matches:
                file_name = (match[0].split('\\')[-1]).split('.')[0]
                file_location_conversation_id[match[1]] = file_name

    if dailer == 'AWS':
        file_location_pattern = r"current url = '.*#(?P<conversation_id>[a-f0-9\-]+)'.*playing audio file (?P<audio_file>.+\.wav)"
        with open(file_path) as file:
            log_text = file.read()
            matches = re.findall(file_location_pattern, log_text, re.MULTILINE)
            for match in matches:
                file_location_conversation_id[match[0]] = match[1]

    return file_location_conversation_id




