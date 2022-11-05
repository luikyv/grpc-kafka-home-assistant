from src import home_assistant, client, servers, sensors

INSTRUCTIONS = """
1. Servers
2. Sensors
3. Home assistant
4. Client
"""

SERVER = """
1. Lamp
2. Air conditioner
3. Audio system
"""

SENSORS = """
1. Luminosity
2. Temperature
3. Audio intensity
"""

if __name__=="__main__":
    print(INSTRUCTIONS)
    option = int(input())
    if option == 1:
        print(SERVER)
        server_option = int(input())
        servers.servers_main(server_option=server_option)
    elif option == 2:
        print(SENSORS)
        sensor_option = int(input())
        sensors.sensors_main(sensor_option=sensor_option)
    elif option == 3:
        home_assistant.main()
    elif option == 4:
        client.main()
    