class Config:
    KAFKA_PORT: int = 9092
    LAMP_SERVER_PORT: int = 50051
    AIR_CONDITIONER_SERVER_PORT: int = 50052
    AUDIO_SYSTEM_SERVER_PORT: int = 50053

    HOME_ASSISTANT_PORT: int = 8000

    LUMINOSITY_TOPIC: str = "luminosity"
    TEMPERATURE_TOPIC: str = "temperature"
    AUDIO_INTENSITY_TOPIC: str = "audio_intensity"
