import math
import requests
from urllib.parse import quote
def count_sms(message):
    GSM_7BIT_MAX_CHARS = 160
    UNICODE_MAX_CHARS = 70

    total_length = len(message)
    is_unicode = any(ord(char) > 127 or ord(char) <
                     32 or ord(char) == 127 for char in message)

    if is_unicode:
        return math.ceil(total_length / UNICODE_MAX_CHARS)
    else:
        return math.ceil(total_length / GSM_7BIT_MAX_CHARS)


def send_sms(number_list, message):
 
    username = "SineEnergy"
    password = "3BEawlCe"
    source = "8809617611578"
    
    url = f"https://apibd.rmlconnect.net:8443/bulksms/personalizedbulksms?username={username}&password={password}&source={source}&destination={number_list}&message={message}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("SMS sent successfully!")
            print("Response:", response.text)
        else:
            print("Failed to send SMS. Status code:", response.status_code)
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)