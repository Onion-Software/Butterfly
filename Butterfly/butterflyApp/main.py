from kafka.admin import KafkaAdminClient
from kafka.admin import NewTopic
from json import load
from pathlib import Path
from consumers.consumer import KafkaConsumerFactory
def see_topics(configs: dict):
    a= KafkaConsumerFactory.create(configs["kafka_consumer"], "abc")
    print(a.topics())

def create_kafka_topic(configs: dict):
    topic_producer_list = [NewTopic(name=topic_name, num_partitions=1, replication_factor=1) for topic_name in
                           configs["kafka_topics"]["topic_producer_name_list"]]
    topic_consumer_list = [NewTopic(name=topic_name, num_partitions=1, replication_factor=1) for topic_name in
                           configs["kafka_topics"]["topic_consumer_name_list"]]
    admin_client = KafkaAdminClient(bootstrap_servers=[configs["kafka_producer"]["bootstrap_servers"]],
                                    client_id='test')
    admin_client.create_topics(new_topics=topic_producer_list, validate_only=False)
    admin_client.create_topics(new_topics=topic_consumer_list, validate_only=False)


if __name__ == '__main__':
    CONFIG_PATH = Path(__file__).parents[0] / 'config' / 'config.json'
    with open(CONFIG_PATH) as file:
        configs = load(file)
    #see_topics(configs)
    create_kafka_topic(configs)
