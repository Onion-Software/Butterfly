from mongoengine import *


# *********
# CONTACT *
# *********
# Inner field of Contact: 'telegram'
class Telegram(EmbeddedDocument):
    username = StringField()
    id = IntField()


# Inner field of Contact: 'slack'
class Slack(EmbeddedDocument):
    email = EmailField()
    id = StringField()


# Inner field of Contact: 'preferences'
class Preferences(EmbeddedDocument):
    use_email = BooleanField()
    use_telegram = BooleanField()
    use_slack = BooleanField()


# Inner field of Contact: 'holidays'
class Holidays(EmbeddedDocument):
    begin_1 = DateField()
    end_1 = DateField()
    begin_2 = DateField()
    end_2 = DateField()
    begin_3 = DateField()
    end_3 = DateField()


class Contact(Document):
    meta = {'collection': 'contacts'}
    name = StringField(required=True)
    surname = StringField(required=True)
    email = EmailField(required=True, unique=True)
    telegram = EmbeddedDocumentField(Telegram)
    slack = EmbeddedDocumentField(Slack)
    preferences = EmbeddedDocumentField(Preferences)
    holidays = EmbeddedDocumentField(Holidays)


# *********
# PROJECT *
# *********
class Project(Document):
    meta = {'collection': 'projects'}
    name = StringField(required=True)
    url = URLField(required=True, unique=True)


# **************
# SUBSCRIPTION *
# **************
class Subscription(Document):
    meta = {'collection': 'subscriptions'}
    contact = ReferenceField(Contact, required=True, unique_with='project', reverse_delete_rule=CASCADE)
    project = ReferenceField(Project, required=True, reverse_delete_rule=CASCADE)
    priority = IntField()
    keywords = ListField(StringField(), default=list)
