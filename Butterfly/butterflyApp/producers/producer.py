from flask import Flask
from flask import request
from flask import abort
from kafka import KafkaProducer
from kafka import errors
from json import dumps
from abc import abstractmethod
from abc import ABC
from time import sleep


class ProducerFactory(ABC):
    @staticmethod
    @abstractmethod
    def create(config: dict) -> KafkaProducer:
        pass


class KafkaProducerFactory(ProducerFactory):
    @staticmethod
    def create(config: dict) -> KafkaProducer:
        """
        :param config: dizionario per configurare un KafkaProducer
        :return: restituisce un'istanza di KafkaProducer con le opportune configurazioni
        """
        max_iter = 10
        while max_iter > 0:
            try:
                result = KafkaProducer(api_version=(0,10,1), value_serializer=lambda x: dumps(x).encode("utf-8"), **config)
                return result
            except errors.NoBrokersAvailable:
                sleep(1)
                max_iter = max_iter - 1
            except KeyboardInterrupt:
                exit(1)
        raise Exception("Creazione di KafkaProducer fallita")


class Producer(ABC):
    def __init__(self, producer: KafkaProducer):
        self._producer = producer

    @abstractmethod
    def produce(self, data: dict):
        pass

    def send(self, topic_name: str, data: dict):
        self._producer.send(topic_name, data)

    def close(self):
        self._producer.close()


class FlaskServer:
    def __init__(self, flask: Flask, producer: Producer):
        self._app = flask
        self._producer = producer

        @self._app.route('/webhook', methods=['POST'])
        def webhook():
            if request.method == 'POST':
                self._producer.produce(request.get_json(True))
                return '', 200
            else:
                abort(400)

    def start(self, host: str, port: int):
        self._app.run(host=host, port=port)

    @staticmethod
    def _shutdown_app():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def close(self):
        FlaskServer._shutdown_app()
        self._producer.close()
