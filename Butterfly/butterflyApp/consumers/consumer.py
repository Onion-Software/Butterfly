from kafka import KafkaConsumer
from kafka import errors
from abc import abstractmethod
from abc import ABC
from json import loads
from time import sleep


class ConsumerFactory(ABC):
    @staticmethod
    @abstractmethod
    def create(config: dict, topic_name: str) -> KafkaConsumer:
        pass

class KafkaConsumerFactory(ConsumerFactory):
    """This class creates Kafka Consumers
    """

    @staticmethod
    def create(config: dict, topic_list: list) -> KafkaConsumer:
        """Create a KafkaConsumer

        :param config: dictionary for KafkaConsumer configuration
        :return: restituisce un'istanza di KafkaProducer con le opportune configurazioni
        """
        max_iter = 10
        while max_iter > 0:
            try:
                result = KafkaConsumer(*topic_list, api_version=(0,10,1), value_deserializer=lambda x: loads(x.decode("utf-8")), **config)
                return result
            except errors.NoBrokersAvailable:
                sleep(1)
                max_iter = max_iter - 1
            except KeyboardInterrupt:
                exit(1)
        raise Exception("Creazione di KafkaConsumer fallita")


class Consumer(ABC):
    """This abstract class is the generic Consumer
    """

    def __init__(self, consumer: KafkaConsumer):
        self._consumer = consumer

    def start(self):
        for message in self._consumer:
            self.consume(message.value)

    def get_topic_list(self):
        return self._consumer.topics()

    def get_subscription(self):
        return self._consumer.subscription()

    def close(self):
        self._consumer.close()

    @abstractmethod
    def consume(self, data: dict):
        pass
