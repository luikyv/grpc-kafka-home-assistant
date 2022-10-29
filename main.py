from src import home_assistant, client, servers, sensors

INSTRUCTIONS = """
1. Servers
2. Sensors
3. Home Assistant
4. Client
"""

if __name__=="__main__":
    print(INSTRUCTIONS)
    option = int(input())
    if option == 1:
        servers.servers_main()
    elif option == 2:
        sensors.sensors_main()
    elif option == 3:
        home_assistant.main()
    elif option == 4:
        client.main()
    