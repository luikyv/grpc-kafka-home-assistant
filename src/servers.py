from concurrent import futures
import grpc

from .protos import home_pb2
from .protos import home_pb2_grpc

from .config import Config
from .devices import Lamp, AirConditioner, AudioSystem

class LampServer(home_pb2_grpc.LampServiceServicer):

    def __init__(self, lamp: Lamp, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.lamp = lamp

    def SetLamp(self, request, context):
        print(f"Turning {'on' if request.on else 'off'} the lamp")
        self.lamp.on = request.on
        return home_pb2.Status(status=200)
    
    def GetLamp(self, request, context):
        print("Replying with information about the lamp")
        return home_pb2.Lamp(on=self.lamp.on)

class AirConditionerServer(home_pb2_grpc.LampServiceServicer):

    def __init__(self, air_conditioner: AirConditioner, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.air_conditioner = air_conditioner

    def SetAirConditioner(self, request, context):
        if not request.on:
            print(f"Turning off the air conditioner")
        else:
            print(f"Setting temperature to: {request.temperature}")

        self.air_conditioner.on = request.on
        self.air_conditioner.temperature = request.temperature
        return home_pb2.Status(status=200)
    
    def GetAirConditioner(self, request, context):
        print("Replying with information about the air conditioner")
        return home_pb2.AirConditioner(on=self.air_conditioner.on, temperature=self.air_conditioner.temperature)

class AudioSystemServer(home_pb2_grpc.AudioSystemServiceServicer):
    def __init__(self, audio_system: AudioSystem, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.audio_system = audio_system
    
    def SetAudioSystem(self, request, context):
        if not request.on:
            print(f"Turning on the audio system")
        else:
            print(f"Setting song to: {request.current_song}")

        self.audio_system.on = request.on
        self.audio_system.current_song = request.current_song
        return home_pb2.Status(status=200)
    
    def GetAudioSystem(self, request, context):
        print("Replying with information about the audio system")
        return home_pb2.AudioSystem(on=self.audio_system.on, current_song=self.audio_system.current_song)

def servers_main(server_option: int):
    lamp = Lamp()
    air_conditioner = AirConditioner()
    audio_system = AudioSystem()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    if server_option == 1:
        home_pb2_grpc.add_LampServiceServicer_to_server(LampServer(lamp=lamp), server)
    if server_option == 2:
        home_pb2_grpc.add_AirConditionerServiceServicer_to_server(AirConditionerServer(air_conditioner=air_conditioner), server)
    if server_option == 3:
        home_pb2_grpc.add_AudioSystemServiceServicer_to_server(AudioSystemServer(audio_system=audio_system), server)
    
    server.add_insecure_port(f"[::]:{Config.DEVICE_SERVER_PORT}")
    server.start()
    server.wait_for_termination()



