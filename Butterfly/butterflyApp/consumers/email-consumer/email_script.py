from consumers.consumer import KafkaConsumerFactory
from consumers.consumer import Consumer
from kafka import KafkaConsumer
from smtplib import SMTP
from pathlib import Path
from json import load
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MailSender:
    """This class sends notifications through email
    """

    def __init__(self, smtp: str, port: str, email: str, password: str):
        self._server = SMTP()
        self._smtp = smtp
        self._port = port
        self._email = email
        self._password = password

    def send(self, recipients: list, message: str):
        try:
            self._server = SMTP(self._smtp, self._port)
            self._server.starttls()
            self._server.login(self._email, self._password)
            self._server.sendmail(self._email, recipients, message)
            self._server.quit()
        except Exception as _:
            print(str(_), flush = True)
            self._server.starttls()
            self._server.login(self._email, self._password)
            self._server.sendmail(self._email, recipient, message)
            self._server.quit()

    def getEmail(self):
        return self._email


class EmailConsumer(Consumer):
    """This class handles the email recipients for the notification
    """

    def __init__(self, consumer: KafkaConsumer, sender: MailSender):
        super().__init__(consumer)
        self._sender = sender

    def consume(self, data: dict):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Notifica Butterfly"
        msg["From"] = self._sender.getEmail()
        recipients = self.extract_recipient_list(data)
        msg["To"] = ", ".join(recipients)

        html, text = self._decorate(data)

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        msg.attach(part1)
        msg.attach(part2)
        if len(recipients):
            self._sender.send(recipients, msg.as_string())

    def extract_recipient_list(self, data: dict):
        return data.pop('recipients')

    def _read_html(self) -> str:
        with open('email.html', 'r') as my_file:
            html = my_file.read()
        return html

    def _decorate(self, data: dict) -> (str, str):
        html = self._read_html() + """Hi there!</span> <br/> We would like to inform you that user """ \
               + data["author"] + """ submitted a new """ + data["object_kind"] + """ on project: \"""" \
               + data["project_name"] + """\" (link: """ + data["project_url"] + """) via """ \
               + data["app"] + """. <br/> Here's what's in the notification:</p>"""
        text = """Hi there!
We would like to inform you that user """ + data["author"] + """ submitted a new """ \
               + data["object_kind"] + """ on project:\"""" + data["project_name"] + """\" (link: """ \
               + data["project_url"] + """) via """ + data["app"] + """.
Here's what's in the notification:
<ul>
"""
        # GitLab notification
        # General information
        if "issue_url" in data.keys():
            html += """<li><b> Author: </b>""" + data["author"] + """</li>""" \
                    + """<li><b> Title: </b>""" + data["title"] + """</li>""" \
                    + """<li><b> Issue URL </b>""" + data["issue_url"] + """</li>"""
            text += """Author: """ + data["author"] + """
Title: """ + data["title"] + """
Issue URL: """ + data["issue_url"] + """
                         """
            # GitLab new issue
            if "status" in data.keys():
                html += """<li><b> Status: </b>""" + data["status"] + """</li>""" \
                        + """<li><b> Assignee: </b>""" + (", ".join(data["assignees"]) if 'assignees' in data.keys() else "nobody") + """</li>"""
                text += """Status: """ + data["status"] + """
Assignee: """ + (", ".join(data["assignees"]) if 'assignees' in data.keys() else "Nobody") + """
"""
                # Gitlab modified issue
                if "last_edited_at" in data.keys():
                    html += """<li><b> Last edited at: </b>""" + data["last_edited_at"] + """</li>""" \
                            + """<li><b> Last edited by: </b>""" + data["last_edited_by"] + """</li>"""
                    text += """Last edited at: """ + data["last_edited_at"] + """
Last edited by: """ + data["last_edited_by_id"] + """
"""
        # GitLab push
        elif "commits_url" in data.keys():
            html += """<li><b> Commits URL: </b>""" + data["commits_url"] + """</li>""" \
                    + """<li><b> Commits author name: </b>""" + data["commits_author_name"] + """</li>""" \
                    + """<li><b> Commits author email: </b>""" + data["commits_author_email"] + """</li>"""
            text += """Commits URL: """ + data["commits_url"] + """
Commits author name: """ + data["commits_author_name"] + """
Commits author email: """ + data["commits_author_email"] + """
"""
        # Redmine Issue
        elif "priority" in data.keys():
            html += ("""<li><b> New priority: </b>""" if 'prioritychanged' in data.keys() and data['prioritychanged'] else """<ul><li><b> Priority: </b>""") + data["priority"] + """</li>""" \
                    + """<li><b> Subject: </b>""" + data["subject"] + """</li>""" \
                    + """<li><b> Status: </b>""" + data["state"] + """</li>"""
            text += ("""New priority: """ if 'prioritychanged' in data.keys() and data['prioritychanged'] else """Priority: """) + data["priority"] + """
Subject: """ + data["subject"] + """
Status: """ + data["state"] + """
"""

        html += """<li><b> Created on: </b>""" + data["created_on"] + """</li>""" \
                + """<li><b> Description: </b>""" + data["description"] + """</li></ul>""" \
                + """<p class="par"> Have a great day! <br/>
<i> Onion Software </i> </p></body></html>"""
        text += """- Created on: """ + data["created_on"] + """
- Description: """ + data["description"]
        return html, text


def start_email_consumer(configs: dict):
    """ Starts email consumer
    """
    email_server = MailSender(configs["email"]["smtp"], configs["email"]["port"], configs["email"]["sender"],
                              configs["email"]["password"])
    try:
        kafka_consumer = KafkaConsumerFactory.create(configs["kafka_consumer"],
                                                     [configs["kafka_topics"]["topic_consumer_name_list"]["email"]])
    except Exception as e:
        print(str(e))
        exit(1)
    email_consumer = EmailConsumer(kafka_consumer, email_server)
    try:
        email_consumer.start()
    except KeyboardInterrupt:
        exit(1)
    finally:
        email_consumer.close()


if __name__ == '__main__':
    CONFIG_PATH = Path(__file__).parents[0] / 'config' / 'config.json'
    with open(CONFIG_PATH) as file:
        configs = load(file)
    start_email_consumer(configs)
