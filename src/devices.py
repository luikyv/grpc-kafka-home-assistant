from abc import ABC, abstractmethod
from dataclasses import dataclass

class Device(ABC):
    pass

@dataclass
class Lamp(Device):
    on: bool = False

@dataclass
class AirConditioner(Device):
    on: bool = False
    temperature: float = 25.0
