from concurrent import futures
import grpc

from .protos import home_pb2
from .protos import home_pb2_grpc

from .config import Config
from .devices import Lamp, AirConditioner

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

def servers_main():
    lamp = Lamp()
    air_conditioner = AirConditioner()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    home_pb2_grpc.add_LampServiceServicer_to_server(LampServer(lamp=lamp), server)
    home_pb2_grpc.add_AirConditionerServiceServicer_to_server(AirConditionerServer(air_conditioner=air_conditioner), server)
    server.add_insecure_port(f"[::]:{Config.DEVICE_SERVER_PORT}")
    server.start()
    server.wait_for_termination()



