import requests
import json

API_URL = "http://localhost:8000/devicedata/device/"
USERNAME = "sunilmangawa"
PASSWORD = "#Brahma4coder"
# API_URL = "http://ballmillautomation.com/milldata/device/"
# USERNAME = "testuser1"
# PASSWORD = "Test4work"
DEVICE_ID = "1"

def fetch_device_data(device_id):
    url = f"{API_URL}{device_id}/"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")

    if response.status_code == 200 and response.text:
        try:
            data = json.loads(response.text)
            return data
        except json.JSONDecodeError:
            print("Error parsing JSON response.")
            return None
    else:
        print(f"Error fetching device data: {response.status_code}")
        return None
    
def get_device_data(device_id):
    device_data = fetch_device_data(device_id)
    return device_data

def main():
    device_data = fetch_device_data(DEVICE_ID)
    if device_data:
        print(f"Device data: {device_data}")
    else:
        print("No device data retrieved.")

# def main():
#     device_data = fetch_device_data(DEVICE_ID)
#     if device_data:
#         # print(f"Device data: {device_data}")
        
#         name = device_data.get('name')
#         ip_address = device_data.get('ip_address')
#         mac_address = device_data.get('mac_address')
#         status = device_data.get('status')
#         initial_hold = device_data.get('initial_hold')
#         circle = device_data.get('circle')
#         feed_time = device_data.get('feed_time')
#         circle_hold = device_data.get('circle_hold')
#         galla_clear_time = device_data.get('galla_clear_time')
#         actual_hold = device_data.get('actual_hold')
#         overload_hold = device_data.get('overload_hold')

#         print(f"Name: {name}")
#         print(f"IP Address: {ip_address}")
#         print(f"MAC Address: {mac_address}")
#         print(f"Status: {status}")
#         print(f"Initial Hold: {initial_hold}")
#         print(f"Circle: {circle}")
#         print(f"Feed Time: {feed_time}")
#         print(f"Circle Hold: {circle_hold}")
#         print(f"Galla Clear Time: {galla_clear_time}")
#         print(f"Actual Hold: {actual_hold}")
#         print(f"Overload Hold: {overload_hold}")

#     else:
#         print("No device data retrieved.")

if __name__ == "__main__":
    main()
