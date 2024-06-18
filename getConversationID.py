import re


def getConversationID(file_path):
    file_location_pattern = r'location\s+(.*?)\s+and\s+conversation\s+ID\s+is\s+(.*?)$'
    file_location_conversation_id = {}
    with open(file_path) as file:
        log_text = file.read()
        matches = re.findall(file_location_pattern, log_text, re.MULTILINE)

        for match in matches:
            file_name = (match[0].split('\\')[-1]).split('.')[0]
            file_location_conversation_id[match[1]] = file_name
    return file_location_conversation_id


# log_file_path = r'C:\\Users\\RaghavKR\\PycharmProjects\\testProject\\Talkdesk_Download_automation_log_20240612_180813.log'
# conversationID = getConversationID(log_file_path)

