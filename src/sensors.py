from abc import ABC, abstractmethod
from aiokafka import AIOKafkaProducer
from time import sleep
import asyncio
import json
import random
import grpc

from .config import Config
from .protos import home_pb2
from .protos import home_pb2_grpc

class Sensor(ABC):

    def __init__(self, kafka_port: int, topic: str) -> None:
        self.kafka_port: int = kafka_port
        self.topic: str = topic
    
    @abstractmethod
    async def publish_properties(producer: AIOKafkaProducer) -> None:
        pass

    async def observe(self) -> None:

        producer = AIOKafkaProducer(
            bootstrap_servers=f"localhost:{self.kafka_port}"
        )
        await producer.start()
        try:
            while True:
                sleep(5)
                await self.publish_properties(producer)
        finally:
            await producer.stop()

class LuminositySensor(Sensor):

    async def publish_properties(self, producer: AIOKafkaProducer) -> None:
        luminosity = random.uniform(0.85, 1.0) if self.is_the_lamp_on() else random.uniform(0.0, 0.15)
        print(f"Publishing luminosity: {luminosity:.2f}")
        await producer.send_and_wait(
            self.topic,
            json.dumps({"property": luminosity}).encode("utf-8")
        )

    def is_the_lamp_on(self,) -> bool:
        with grpc.insecure_channel(f"localhost:{Config.DEVICE_SERVER_PORT}") as channel:
            stub = home_pb2_grpc.LampServiceStub(channel)
            empty = home_pb2.Empty()
            try:
                lamp = stub.GetLamp(empty)
            except:
                return False
            else:
                return lamp.on

class TemperatureSensor(Sensor):

    async def publish_properties(self, producer: AIOKafkaProducer) -> None:
        temperature = self.get_temperature() + random.uniform(-2.0, 2.0)
        print(f"Publishing temperature: {temperature:.2f} degrees")
        await producer.send_and_wait(
            self.topic,
            json.dumps({"property": temperature}).encode("utf-8")
        )

    def get_temperature(self,) -> float:
        with grpc.insecure_channel(f"localhost:{Config.DEVICE_SERVER_PORT}") as channel:
            stub = home_pb2_grpc.AirConditionerServiceStub(channel)
            empty = home_pb2.Empty()
            try:
                air_conditioner = stub.GetAirConditioner(empty)
            except:
                return 25.0
            else:
                return air_conditioner.temperature

class AudioIntensitySensor(Sensor):

    async def publish_properties(self, producer: AIOKafkaProducer) -> None:
        audio_intensity = random.uniform(0.85, 1.0) if self.is_audio_system_on() else random.uniform(0.0, 0.15)
        print(f"Publishing audio intensity: {audio_intensity:.2f} decibels")
        await producer.send_and_wait(
            self.topic,
            json.dumps({"property": audio_intensity}).encode("utf-8")
        )

    def is_audio_system_on(self,) -> bool:
        with grpc.insecure_channel(f"localhost:{Config.DEVICE_SERVER_PORT}") as channel:
            stub = home_pb2_grpc.AudioSystemServiceStub(channel)
            empty = home_pb2.Empty()
            try:
                audio_system = stub.GetAudioSystem(empty)
            except:
                return False
            else:
                return audio_system.on

#################### Sensor Main Functions ##########

async def _sensors_main():
    luminosity_sensor = LuminositySensor(
        kafka_port=Config.KAFKA_PORT,
        topic=Config.LUMINOSITY_TOPIC
    )
    temperature_sensor = TemperatureSensor(
        kafka_port=Config.KAFKA_PORT,
        topic=Config.TEMPERATURE_TOPIC
    )
    audio_system_sensor = AudioIntensitySensor(
        kafka_port=Config.KAFKA_PORT,
        topic=Config.AUDIO_INTENSITY_TOPIC
    )
    await asyncio.gather(
        *[sensor.observe() for sensor in [luminosity_sensor, temperature_sensor, audio_system_sensor]]
    )

# def sensors_main():
#     asyncio.run(_sensors_main())

def sensors_main(sensor_option: int):
    if sensor_option == 1:
        luminosity_sensor = LuminositySensor(
            kafka_port=Config.KAFKA_PORT,
            topic=Config.LUMINOSITY_TOPIC
        )
        asyncio.run(luminosity_sensor.observe())
    elif sensor_option == 2:
        temperature_sensor = TemperatureSensor(
            kafka_port=Config.KAFKA_PORT,
            topic=Config.TEMPERATURE_TOPIC
        )
        asyncio.run(temperature_sensor.observe())
    elif sensor_option == 3:
        audio_system_sensor = AudioIntensitySensor(
            kafka_port=Config.KAFKA_PORT,
            topic=Config.AUDIO_INTENSITY_TOPIC
        )
        asyncio.run(audio_system_sensor.observe())
    