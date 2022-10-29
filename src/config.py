class Config:
    KAFKA_PORT: int = 9092
    DEVICE_SERVER_PORT: int = 50051
    HOME_ASSISTANT_PORT: int = 8000

    LUMINOSITY_TOPIC: str = "luminosity"
    TEMPERATURE_TOPIC: str = "temperature"
    AUDIO_INTENSITY_TOPIC: str = "audio_intensity"
