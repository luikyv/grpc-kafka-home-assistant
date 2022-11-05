from aiokafka import AIOKafkaConsumer
import asyncio
import threading
import json
import grpc
from fastapi import FastAPI
import uvicorn
from dataclasses import dataclass
from typing import List
from enum import Enum

from .protos import home_pb2_grpc, home_pb2
from .config import Config
from .devices import Device, Lamp, AirConditioner, AudioSystem

class SensorTypes(str, Enum):
    luminosity = "luminosity"
    temperature = "temperature"
    audio_intensity = "audio_intensity"

class DevicesTypes(str, Enum):
    lamp = "lamp"
    air_conditioner = "air_conditioner"
    audio_system = "audio_system"

@dataclass
class Sensor:
    name: str
    topic: str
    last_read: float = -1.0

class HomeAssistant():
    def __init__(self, kafka_port: int, sensors: List[Sensor]) -> None:
        self.kafka_port: int = kafka_port
        self.sensor_mapping = {s.name: s for s in sensors}

    ########## Sensors ##########
    
    async def read_sensor(self, sensor_name: str) -> None:
        
        sensor: Sensor = self.sensor_mapping[sensor_name]
        consumer = AIOKafkaConsumer(
            sensor.topic,
            bootstrap_servers=f"localhost:{self.kafka_port}"
        )
        await consumer.start()
        try:
            async for msg in consumer:
                json_ = json.loads(msg.value.decode("utf-8"))
                sensor.last_read = json_["property"]
                print(f"{sensor.name}: {sensor.last_read:.2f}")
        finally:
            await consumer.stop()
    
    def get_last_read(self, sensor_name: str) -> float:
        return self.sensor_mapping[sensor_name].last_read
    
    async def read_sensors(self) -> None:
        await asyncio.gather(*[
            self.read_sensor(sensor_name)
            for sensor_name in self.sensor_mapping
        ])
    
    ########## Devices ##########

    def set_device(self, device: Device) -> None:
        with grpc.insecure_channel(f"localhost:{Config.DEVICE_SERVER_PORT}") as channel:
            if isinstance(device, Lamp):
                stub = home_pb2_grpc.LampServiceStub(channel)
                stub.SetLamp(home_pb2.Lamp(on=device.on))
            elif isinstance(device, AirConditioner):
                stub = home_pb2_grpc.AirConditionerServiceStub(channel)
                stub.SetAirConditioner(home_pb2.AirConditioner(on=device.on, temperature=device.temperature))
            elif isinstance(device, AudioSystem):
                stub = home_pb2_grpc.AudioSystemServiceStub(channel)
                stub.SetAudioSystem(home_pb2.AudioSystem(on=device.on, current_song=device.current_song))
    
    def get_device(self, device_name: DevicesTypes) -> Device:
        with grpc.insecure_channel(f"localhost:{Config.DEVICE_SERVER_PORT}") as channel:
            if device_name == "lamp":
                stub = home_pb2_grpc.LampServiceStub(channel)
                lamp = stub.GetLamp(home_pb2.Empty())
                return Lamp(on=lamp.on)
            if device_name == "air_conditioner":
                stub = home_pb2_grpc.AirConditionerServiceStub(channel)
                air_conditioner = stub.GetAirConditioner(home_pb2.Empty())
                return AirConditioner(on=air_conditioner.on, temperature=air_conditioner.temperature)
            if device_name == "audio_system":
                stub = home_pb2_grpc.AudioSystemServiceStub(channel)
                audio_system = stub.GetAudioSystem(home_pb2.Empty())
                return AudioSystem(on=audio_system.on, current_song=audio_system.current_song)

#################### API Endpoints ####################
home_assistant = HomeAssistant(
    kafka_port=Config.KAFKA_PORT,
    sensors=[
        Sensor(
            name="luminosity",
            topic=Config.LUMINOSITY_TOPIC
        ),
        Sensor(
            name="temperature",
            topic=Config.TEMPERATURE_TOPIC
        ),
        Sensor(
            name="audio_intensity",
            topic=Config.AUDIO_INTENSITY_TOPIC
        ),
    ]
)
app = FastAPI()

########## Sensors ##########

@app.get("/sensor/{sensor_name}")
async def get_sensor(sensor_name: SensorTypes):
    return {"property": home_assistant.get_last_read(sensor_name)}

@app.get("/sensors")
async def get_sensors():
    return {"sensors": list(home_assistant.sensor_mapping.keys())}

########## Devices ##########

@app.put("/lamp/{on}")
async def set_lamp(on: bool):
    home_assistant.set_device(Lamp(on=on))

@app.get("/lamp")
async def get_lamp():
    return {"on": home_assistant.get_device(device_name="lamp").on}

@app.put("/air_conditioner/{on}/{temperature}")
async def set_air_conditioner(on: bool, temperature: float):
    home_assistant.set_device(AirConditioner(on=on, temperature=temperature))

@app.get("/air_conditioner")
async def get_air_conditioner():
    air_conditioner = home_assistant.get_device(device_name="air_conditioner")
    return {"on": air_conditioner.on, "temperature": air_conditioner.temperature}

@app.put("/audio_system/{on}/{current_song}")
async def set_audio_system(on: bool, current_song: str):
    home_assistant.set_device(AudioSystem(on=on, current_song=current_song))

@app.get("/audio_system")
async def get_audio_system():
    audio_system = home_assistant.get_device(device_name="audio_system")
    return {"on": audio_system.on, "current_song": audio_system.current_song}

@app.get("/devices")
async def get_devices():
    return {"devices": [device.name for device in DevicesTypes]}

#################### Main ####################

def main():
    read_sensors_thread = threading.Thread(
        target=asyncio.run,
        args=(home_assistant.read_sensors(),)
    )
    read_sensors_thread.start()
    ### Start API ###
    uvicorn.run(
        "src.home_assistant:app",
        host="0.0.0.0",
        port=Config.HOME_ASSISTANT_PORT,
        reload=False,
        log_level="debug"
    )



