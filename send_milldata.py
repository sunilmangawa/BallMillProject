import requests
import time
from datetime import datetime
import json

# Replace these with the appropriate values
username = 'sunilmangawa'
password = '#Brahma4coder'
# device_id = 1
# base_url = 'http://localhost:8000'
# device_id, 
# def send_milldata(katta_time, katta_weight, circle, feed_time, circle_hold, actual_hold, feed_status, overload_status):
def send_milldata(katta_time, katta_weight, feed_status, overload_status):
    #url = f"{base_url}/devices/{device_id}/timestamps/"
    # url = 'https://ballmillautomation.com/milldata/devices/1/timestamps/'
    url = 'http://localhost:8000/devicedata/devices/1/timestamps/'
    # Set the headers for the POST request
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "katta_time": katta_time,
        "katta_weight": katta_weight,
        # "circle": circle,
        # "feed_time": feed_time,
        # "circle_hold": circle_hold,
        # "actual_hold": actual_hold,
        "feed_status": feed_status,
        "overload_status": overload_status,
    }
    json_data = json.dumps(data)
    response = requests.post(url, data=json_data, headers=headers, auth=(username, password))
    return response

def main():
    while True:
        katta_time = datetime.now().isoformat()
        katta_weight = 60  # Replace this with the actual value
        # circle = 15  # Replace this with the actual value
        # feed_time = 10  # Replace this with the actual value
        # circle_hold = 15  # Replace this with the actual value
        # actual_hold = 1000  # Replace this with the actual value
        feed_status = True  # Replace this with the actual value
        overload_status = False  # Replace this with the actual value
        # response = send_milldata(katta_time, katta_weight, circle, feed_time, circle_hold, actual_hold, feed_status, overload_status)
        response = send_milldata(katta_time, katta_weight, feed_status, overload_status)
        print(f"Sent data to device 1: {response.status_code}")
        print(f"Response content: {response.content}")  # Add this line to print the response content        time.sleep(96)
        time.sleep(96)
if __name__ == "__main__":
    main()
