from producers.producer import Producer
from producers.producer import KafkaProducerFactory
from producers.producer import FlaskServer
from json import load
from pathlib import Path
from kafka import KafkaProducer
from flask import Flask


class GitLabProducer(Producer):
    """
    This class extracts important data from Gitlab notifications
    """

    def __init__(self, producer: KafkaProducer, server: str):
        super().__init__(producer)
        self._server = server

    def produce(self, data: dict):
        try:
            self.send("gitlab", self._parse(data))
        except Exception as e:
            print(str(e))

    
    def _parse(self, data: dict) -> dict:
        result = dict()
        result["app"] = "GitLab"
        result["object_kind"] = data["object_kind"]
        result["project_name"] = data["project"]["name"]
        result["project_url"] = f"http://{self._server}/{data['project']['path_with_namespace']}"
        if data["object_kind"] == "issue":
            if data["object_attributes"]["last_edited_at"] is None:
                return self._find_new_issue_keys(data, result)
            else:
                return self._find_modified_issue_keys(data, result)
        elif data["object_kind"] == "push":
            return self._find_push_keys(data, result)
        elif data["object_kind"] == "note":
            return self._find_note_keys(data, result)
        else:
            raise Exception("This notification is not supported")

    
    def _find_note_keys(self, data: dict, result: dict) -> dict:
        if "commit" in data.keys():
            result["title"] = data["commit"]["message"]
        else:
            result["title"] = data["issue"]["title"]
        result["author"] = data["user"]["name"]
        result["description"] = data["object_attributes"]["description"]
        result["created_on"] = data["object_attributes"]["created_at"]
        result["issue_url"] = f"{result['project_url']}/issues/{data['issue']['id']}"
        return result

    
    def _find_issue_keys(self, data: dict, result: dict) -> dict:
        result["title"] = data["object_attributes"]["title"]
        result["author"] = data["user"]["name"]
        result["description"] = data["object_attributes"]["description"]
        result["status"] = data["object_attributes"]["state"]
        result["created_on"] = data["object_attributes"]["created_at"]
        result["issue_url"] = f"{result['project_url']}/issues/{data['object_attributes']['id']}"
        if "assignees" in data.keys():
            result["assignees"] = [assignee["username"] for assignee in data["assignees"]]
        return result

    
    def _find_new_issue_keys(self, data: dict, result: dict) -> dict:
        return self._find_issue_keys(data, result)

    
    def _find_modified_issue_keys(self, data: dict, result: dict) -> dict:
        result = self._find_issue_keys(data, result)
        result["last_edited_at"] = data["object_attributes"]["last_edited_at"]
        result["last_edited_by_id"] = data["object_attributes"]["last_edited_by_id"]
        return result

    
    def _find_push_keys(self, data: dict, result: dict) -> dict:
        result["author"] = data["user_name"]
        result["description"] = data["commits"][0]["message"]
        result["created_on"] = data["commits"][0]["timestamp"]  # called once: result["commits_timestamp"]
        result["commits_url"] = f"{result['project_url']}/commit/{data['commits'][0]['id']}"
        result["commits_author_name"] = data["commits"][0]["author"]["name"]
        result["commits_author_email"] = data["commits"][0]["author"]["email"]
        return result


def start_gitlab_producer(configs: dict):
    try:
        kafka_producer = KafkaProducerFactory.create(configs["kafka_producer"])
    except Exception as e:
        print(str(e))
        exit(1)
    app = Flask(configs["gitlab"]["app_name"])
    server = FlaskServer(app, GitLabProducer(kafka_producer, configs["gitlab"]["server"]))
    try:
        server.start(configs["gitlab"]["ip"], configs["gitlab"]["port"])
    except KeyboardInterrupt:
        exit(1)
    finally:
        server.close()


if __name__ == '__main__':
    CONFIG_PATH = Path(__file__).parents[0] / 'config' / 'config.json'
    with open(CONFIG_PATH) as file:
        configs = load(file)
    start_gitlab_producer(configs)
