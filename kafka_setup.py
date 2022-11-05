from kafka.admin import KafkaAdminClient, NewTopic
from src.config import Config

admin_client = KafkaAdminClient(
    bootstrap_servers=f"localhost:{Config.KAFKA_PORT}", 
    client_id="main_client"
)

topic_list = []
topic_list.append(NewTopic(name=Config.LUMINOSITY_TOPIC, num_partitions=1, replication_factor=1))
topic_list.append(NewTopic(name=Config.TEMPERATURE_TOPIC, num_partitions=1, replication_factor=1))
topic_list.append(NewTopic(name=Config.AUDIO_INTENSITY_TOPIC, num_partitions=1, replication_factor=1))
admin_client.create_topics(new_topics=topic_list, validate_only=False)