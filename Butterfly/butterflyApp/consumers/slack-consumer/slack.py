from consumers.consumer import KafkaConsumerFactory
from consumers.consumer import Consumer
from kafka import KafkaConsumer
from pathlib import Path
from json import load
from mongodb.mongo import Mongo
from slackclient import SlackClient
from time import sleep
from threading import Thread


class SlackBot:
    """This class creates a bot to send notifications through Slack
    """

    def __init__(self, client: SlackClient, mongo_db: Mongo):
        self._mongo = mongo_db
        self._client = client
        self._isListening = False

    def send_message(self, recipient: str, message: str):
        self._client.api_call(
            "chat.postMessage",
            channel=recipient,
            text=message
        )

    def start(self):
        self._client.rtm_connect(with_team_state=False)
        user_list = self._client.api_call(method="users.list")
        for user in user_list["members"]:
            if "email" in user["profile"].keys():
                try:
                    self._mongo.update_slack_id(user["profile"]["email"], user["id"])
                except Exception as e:
                    self.send_message(user["id"], str(e))
        self._isListening = True
        self.listen()

    def listen(self):
        while self._isListening:
            for event in self._client.rtm_read():
                self._parse_event(event)
            sleep(1)

    def close(self):
        self._isListening = False

    def _parse_event(self, event: dict):
        if event["type"] == "member_joined_channel":
            user_list = self._client.api_call(method="users.list")
            for user in user_list["members"]:
                if user["id"] == event["user"] and "email" in user["profile"].keys():
                    try:
                        self._mongo.update_slack_id(user["profile"]["email"], event["user"])
                    except Exception as e:
                        self._send_message(event["user"], str(e))


class SlackConsumer(Consumer):
    """This class handles the Slack recipients for the notification
    """

    def __init__(self, consumer: KafkaConsumer, bot: SlackBot):
        super().__init__(consumer)
        self._bot = bot

    def consume(self, data: dict):
        message = self._decorate(data)
        for recipient in self.extract_recipient_list(data):
            self._bot.send_message(recipient, message)

    def _decorate(self, data: dict) -> str:
        text = """Hi there!
We would like to inform you that user """ + data["author"] + """ submitted a new """ \
               + data["object_kind"] + """ on project: \"""" + data["project_name"] + """\" (link: """ \
               + data["project_url"] + """) via """ + data["app"] + """.
Here's what's in the notification:
"""
        if "issue_url" in data.keys():
            text += """Author: """ + data["author"] + """
Title: """ + data["title"] + """
Issue URL: """ + data["issue_url"] + """
"""
            if "status" in data.keys():
                text += """Status: """ + data["status"] + """
Assignee: """ + ( ", ".join(data["assignees"]) if "assignees" in data.keys() else "nobody" ) + """
"""
                # Gitlab modified issue
                if "last_edited_at" in data.keys():
                    text += """Last edited at: """ + data["last_edited_at"] + """
Last edited by: """ + data["last_edited_by_id"] + """
"""
        # GitLab push
        elif "commits_url" in data.keys():
            text += """Commits URL: """ + data["commits_url"] + """
Commits author name: """ + data["commits_author_name"] + """
Commits author email: """ + data["commits_author_email"] + """
"""
        # Redmine Issue
        elif "priority" in data.keys():
            text += ("""New priority: """ if 'prioritychanged' in data.keys() and data['prioritychanged'] else """Priority: """) + data["priority"] + """
Subject: """ + data["subject"] + """
Status: """ + data["state"] + """
"""

        text += """ - Created on: """ + data["created_on"] + """
 - Description: """ + data["description"]
        return text

    def extract_recipient_list(self, data: dict):
        return data.pop("recipients")


def start_slack_consumer(configs: dict):
    mongo = Mongo(configs["mongo"]["db_name"], configs["mongo"]["host"], configs["mongo"]["port"])
    slack_bot = SlackBot(SlackClient(configs["slack"]["bot_token"]), mongo)
    try:
        kafka_consumer = KafkaConsumerFactory.create(configs["kafka_consumer"],
                                                     [configs["kafka_topics"]["topic_consumer_name_list"]["slack"]])

    except Exception as e:
        print(str(e))
        exit(1)
    slack_consumer = SlackConsumer(kafka_consumer, slack_bot)
    try:
        Thread(target=slack_bot.start).start()
        slack_consumer.start()
    except KeyboardInterrupt:
        exit(1)
    finally:
        slack_consumer.close()
        slack_bot.close()


if __name__ == '__main__':
    CONFIG_PATH = Path(__file__).parents[0] / 'config' / 'config.json'
    with open(CONFIG_PATH) as file:
        configs = load(file)
    start_slack_consumer(configs)
