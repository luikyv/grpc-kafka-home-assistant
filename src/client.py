import requests

from .config import Config

INSTRUCTIONS = """
------------------- CLIENT OPTIONS -------------------
1. Get luminosity
2. Get temperature
3. Get audio intensity
4. List sensors
5. Get lamp
6. Set lamp
7. Get air conditioner
8. Set air conditioner
9. Get audio system
10. Set audio system
11. List devices
"""
HOME_ASSISTANT_URL = f"http://localhost:{Config.HOME_ASSISTANT_PORT}/"

def main():
    print(INSTRUCTIONS)
    while True:
        option = int(input())
        if option == 1:
            resp = requests.get(HOME_ASSISTANT_URL + "sensor/luminosity")
            print(f"Luminosity: {100*resp.json()['property']:.2f}%")
        elif option == 2:
            resp = requests.get(HOME_ASSISTANT_URL + "sensor/temperature")
            print(f"Temperature: {resp.json()['property']:.2f}")
        elif option == 3:
            resp = requests.get(HOME_ASSISTANT_URL + "sensor/audio_intensity")
            print(f"Audio intensity: {resp.json()['property']:.2f}")
        elif option == 4:
            resp = requests.get(HOME_ASSISTANT_URL + "sensors")
            print(f"Sensors: {resp.json()['sensors']}")
        elif option == 5:
            resp = requests.get(HOME_ASSISTANT_URL + "lamp")
            print(f"The lamp is {'on' if resp.json()['on'] else 'off'}")
        elif option == 6:
            on = input("Turn on? Y/N ") == "Y"
            resp = requests.put(HOME_ASSISTANT_URL + f"lamp/{on}")
        elif option == 7:
            resp = requests.get(HOME_ASSISTANT_URL + "air_conditioner")
            resp_json = resp.json()
            print(f"The air conditioner is {'on' if resp_json['on'] else 'off'}. Temperature: {resp_json['temperature']}")
        elif option == 8:
            on = input("Turn on? Y/N ") == "Y"
            if on:
                temperature = float(input("Temperature? "))
                requests.put(HOME_ASSISTANT_URL + f"air_conditioner/{on}/{temperature}")
            else:
                requests.put(HOME_ASSISTANT_URL + f"air_conditioner/{on}/{25.0}")
        elif option == 9:
            resp = requests.get(HOME_ASSISTANT_URL + "audio_system")
            resp_json = resp.json()
            print(f"The audio system is {'on' if resp_json['on'] else 'off'}. Current song: {resp_json['current_song']}")
        elif option == 10:
            on = input("Turn on? Y/N ") == "Y"
            if on:
                current_song = input("Song to play? ")
                requests.put(HOME_ASSISTANT_URL + f"audio_system/{on}/{current_song}")
            else:
                requests.put(HOME_ASSISTANT_URL + f"audio_system/{on}/{'none'}")
        elif option == 11:
            resp = requests.get(HOME_ASSISTANT_URL + "devices")
            print(f"Devices: {resp.json()['devices']}")