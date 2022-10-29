import requests

from .config import Config

INSTRUCTIONS = """
------------------- CLIENT OPTIONS -------------------
1. Get luminosity
2. Get temperature
3. Get lamp
4. Set lamp
5. Get air conditioner
6. Set air conditioner
"""
HOME_ASSISTANT_URL = f"http://localhost:{Config.HOME_ASSISTANT_PORT}/"

def main():
    print(INSTRUCTIONS)
    while True:
        option = int(input())
        if option == 1:
            resp = requests.get(HOME_ASSISTANT_URL + "sensor/luminosity")
            print(f"Luminosity: {100*resp.json()['property']:.2f}%")
        if option == 2:
            resp = requests.get(HOME_ASSISTANT_URL + "sensor/temperature")
            print(f"Temperature: {resp.json()['property']:.2f}")
        elif option == 3:
            resp = requests.get(HOME_ASSISTANT_URL + "lamp")
            print(f"The lamp is {'on' if resp.json()['on'] else 'off'}")
        elif option == 4:
            on = input("Turn on? Y/N ") == "Y"
            resp = requests.put(HOME_ASSISTANT_URL + f"lamp/{on}")
        elif option == 5:
            resp = requests.get(HOME_ASSISTANT_URL + "air_conditioner")
            resp_json = resp.json()
            print(f"The air conditioner is {'on' if resp_json['on'] else 'off'}. Temperature: {resp_json['temperature']}")
        elif option == 6:
            on = input("Turn on? Y/N ") == "Y"
            if on:
                temperature = float(input("Temperature? "))
                requests.put(HOME_ASSISTANT_URL + f"air_conditioner/{on}/{temperature}")
            else:
                requests.put(HOME_ASSISTANT_URL + f"air_conditioner/{on}/{25.0}")