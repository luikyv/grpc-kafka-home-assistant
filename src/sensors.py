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
            lamp = stub.GetLamp(empty)
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
            air_conditioner = stub.GetAirConditioner(empty)
            return air_conditioner.temperature

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
    await asyncio.gather(
        *[sensor.observe() for sensor in [luminosity_sensor, temperature_sensor]]
    )

def sensors_main():
    asyncio.run(_sensors_main())
    