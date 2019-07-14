from producers.producer import Producer
from producers.producer import KafkaProducerFactory
from producers.producer import FlaskServer
from json import load
from pathlib import Path
from kafka import KafkaProducer
from flask import Flask


class RedmineProducer(Producer):
    """
    This class extracts important data from Redmine notifications
    """

    def __init__(self, producer: KafkaProducer, server: str):
        super().__init__(producer)
        self._server = server

    def produce(self, data: dict):
        try:
            self.send("redmine", self._parse(data))
        except Exception as e:
            print(str(e), flush=True)

    def _parse(self, data: dict) -> dict:
        result = dict()
        result["app"] = "Redmine"
        result["author"] = data["author"]["login"]
        result["project_name"] = data["project"]["name"]
        result["project_url"] = f"http://{self._server}/projects/{data['project']['identifier']}"
        result["priority"] = data["priority"]["name"]
        result["created_on"] = data["updated_on"]
        result["subject"] = data["subject"]
        result["description"] = data["description"]
        result["state"] = data["status_id"]["name"]
        if data["created_on"] != data["updated_on"]:
            result["object_kind"] = "issue change"
            result["prioritychanged"] = data["prioritychanged"]
        else:
            result["object_kind"] = "issue creation"
        return result


def start_redmine_producer(configs: dict):
    try:
        kafka_producer = KafkaProducerFactory.create(configs["kafka_producer"])
    except Exception as e:
        print(str(e))
        exit(1)
    app = Flask(configs["redmine"]["app_name"])
    server = FlaskServer(app, RedmineProducer(kafka_producer, configs["redmine"]["server"]))
    try:
        server.start(configs["redmine"]["ip"], configs["redmine"]["port"])
    except KeyboardInterrupt:
        exit(1)
    finally:
        server.close()


if __name__ == '__main__':
    CONFIG_PATH = Path(__file__).parents[0] / 'config' / 'config.json'
    with open(CONFIG_PATH) as file:
        configs = load(file)
    start_redmine_producer(configs)
