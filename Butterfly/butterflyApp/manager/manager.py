from mongodb.mongo import Mongo
from producers.producer import Producer
from producers.producer import KafkaProducerFactory
from consumers.consumer import KafkaConsumerFactory
from consumers.consumer import Consumer
from kafka import KafkaConsumer
from kafka import KafkaProducer
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from json import load
from kafka.admin import KafkaAdminClient
from kafka.admin import NewTopic

class Processor(ABC):
    @abstractmethod
    def process(self, data: dict):
        pass

    @abstractmethod
    def stop(self):
        pass


class PersonalManager(Processor):
    def __init__(self, mongo: Mongo, producer: Producer):
        self._producer = producer
        self._mongo = mongo

    def process(self, data: dict):
        if "project_url" in data:
            recipients = self._mongo.get_interested_recipients(data)
            if recipients:
                self._add_preferences(data, recipients)
                self._producer.produce(data)

    def stop(self):
        self._producer.close()

    def _add_preferences(self, data: dict, recipients: dict):
        data["recipients"] = recipients


class DispatcherProducer(Producer):
    def __init__(self, producer: KafkaProducer):
        super().__init__(producer)

    def produce(self, data: dict):
        recipients = self.extract_topic_list(data)
        for topic in recipients.keys():
            data["recipients"] = recipients[topic]
            self.send(topic, data)
            data.pop("recipients")

    def extract_topic_list(self, data: dict):
        return data.pop("recipients")


class DispatcherConsumer(Consumer):
    def __init__(self, consumer: KafkaConsumer, processor: Processor):
        super().__init__(consumer)
        self._processor = processor

    def consume(self, data: dict):
        self._processor.process(data)

    def close(self):
        super().close()
        self._processor.stop()


def create_dispatcher_producer(configs: dict) -> DispatcherProducer:
    try:
        kafka_producer = KafkaProducerFactory.create(configs["kafka_producer"])
    except Exception as e:
        print(str(e))
        exit(1)
    return DispatcherProducer(kafka_producer)


def create_personal_manager(configs: dict) -> PersonalManager:
    mongo = Mongo(configs["mongo"]["db_name"], configs["mongo"]["host"], configs["mongo"]["port"])
    return PersonalManager(mongo, create_dispatcher_producer(configs))


def create_dispatcher_consumer(configs: dict):
    try:
        kafka_consumer = KafkaConsumerFactory.create(configs["kafka_consumer"],
                                                     [_ for _ in configs["kafka_topics"]["topic_producer_name_list"].values()])
        return DispatcherConsumer(kafka_consumer, create_personal_manager(configs))
    except Exception as e:
        print(str(e))
        exit(1)


def start_manager(configs: dict):
    print("Creating manager...", flush=True)
    manager = create_dispatcher_consumer(configs)
    print("Manager created!", flush = True)
    try:
        manager.start()
    except KeyboardInterrupt:
        exit(1)
    finally:
        manager.close()

def create_kafka_topic(configs: dict):
    see_topics = KafkaConsumerFactory.create(configs["kafka_consumer"], ["abc"])
    already_created = see_topics.topics()
    topic_producer_list = [NewTopic(name=topic_name, num_partitions=1, replication_factor=1) for topic_name in configs["kafka_topics"]["topic_producer_name_list"] if topic_name not in already_created]
    topic_consumer_list = [NewTopic(name=topic_name, num_partitions=1, replication_factor=1) for topic_name in configs["kafka_topics"]["topic_consumer_name_list"] if topic_name not in already_created]
    if len(topic_producer_list) + len(topic_consumer_list) > 0:
        admin_client = KafkaAdminClient(bootstrap_servers=[configs["kafka_producer"]["bootstrap_servers"]],
                                    client_id='test')
        admin_client.create_topics(new_topics=topic_producer_list, validate_only=False)
        admin_client.create_topics(new_topics=topic_consumer_list, validate_only=False)

if __name__ == '__main__':
    CONFIG_PATH = Path(__file__).parents[0] / 'config' / 'config.json'
    with open(CONFIG_PATH) as file:
        configs = load(file)
    #create_kafka_topic(configs)
    start_manager(configs)
