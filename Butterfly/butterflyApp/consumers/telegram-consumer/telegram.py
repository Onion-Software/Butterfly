from consumers.consumer import KafkaConsumerFactory
from consumers.consumer import Consumer
from kafka import KafkaConsumer
from pathlib import Path
from json import load
from telebot import TeleBot
from mongodb.mongo import Mongo
from threading import Thread


class TelegramBot:
    """This class handles the bot for sending notifications through Telegram
    """

    def __init__(self, bot: TeleBot, mongo_db: Mongo):
        self._mongo = mongo_db
        self._bot = bot

        @self._bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            try:
                self._mongo.update_telegram_id(message.chat.username, message.chat.id)
                self._bot.reply_to(message, "Howdy, how are you doing?")
            except Exception as e:
                self._bot.reply_to(message, str(e))

    def set_bot(self, bot: TeleBot):
        self.close()
        self._bot = bot

        @self._bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            try:
                self._mongo.update_telegram_id(message.chat.username, message.chat.id)
                self._bot.reply_to(message, "Howdy, how are you doing?")
            except Exception as e:
                self._bot.reply_to(message, str(e))

    def get_bot(self):
        return self._bot

    def close(self):
        self._bot.stop_polling()
        self._bot.stop_bot()

    def start(self):
        self._bot.polling()

    def send_message(self, recipient: int, message: str):
        self._bot.send_message(recipient, message)


class TelegramConsumer(Consumer):
    """This class handles the notifications to be sent through Telegram
    """

    def __init__(self, consumer: KafkaConsumer, bot: TelegramBot):
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


def start_telegram_consumer(configs: dict):
    mongo = Mongo(configs["mongo"]["db_name"], configs["mongo"]["host"], configs["mongo"]["port"])
    telegram_bot = TelegramBot(TeleBot(configs["telegram"]["bot_token"]), mongo)
    try:
        kafka_consumer = KafkaConsumerFactory.create(configs["kafka_consumer"],
                                                     [configs["kafka_topics"]["topic_consumer_name_list"]["telegram"]])

    except Exception as e:
        print(str(e))
        exit(1)
    telegram_consumer = TelegramConsumer(kafka_consumer, telegram_bot)
    try:
        Thread(target=telegram_bot.start).start()
        telegram_consumer.start()
    except KeyboardInterrupt:
        exit(1)
    finally:
        telegram_consumer.close()
        telegram_bot.close()


if __name__ == '__main__':
    CONFIG_PATH = Path(__file__).parents[0] / 'config' / 'config.json'
    with open(CONFIG_PATH) as file:
        configs = load(file)
    start_telegram_consumer(configs)
