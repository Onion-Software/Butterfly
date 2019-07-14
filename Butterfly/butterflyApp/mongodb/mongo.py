from mongodb.collections import *
from datetime import date
import re


class Mongo:
    def __init__(self, db_name, db_host, db_port):
        connect(db_name, host=db_host, port=db_port)

    
    def first_element_if_exists(self, query_result):
        if len(query_result):
            return query_result[0]
        else:
            return None

    
    def insert_contact(self, name, surname, email, telegram_username, slack_email,
                       use_email, use_telegram, use_slack, holidays_begin_1, holidays_end_1, holidays_begin_2,
                       holidays_end_2, holidays_begin_3, holidays_end_3):
        if ((holidays_begin_1 is None and holidays_end_1 is None) or (
                holidays_begin_1 is not None and holidays_end_1 is not None and holidays_begin_1 <= holidays_end_1)) and (
                (holidays_begin_2 is None and holidays_end_2 is None) or (
                holidays_begin_2 is not None and holidays_end_2 is not None and holidays_begin_2 <= holidays_end_2)) and (
                (holidays_begin_3 is None and holidays_end_3 is None) or (
                holidays_begin_3 is not None and holidays_end_3 is not None and holidays_begin_3 <= holidays_end_3)):
            telegram = Telegram(username=telegram_username)
            slack = Slack(email=slack_email)
            preferences = Preferences(use_email=use_email, use_telegram=use_telegram, use_slack=use_slack)
            holidays = Holidays(begin_1=holidays_begin_1, end_1=holidays_end_1, begin_2=holidays_begin_2,
                                end_2=holidays_end_2, begin_3=holidays_begin_3, end_3=holidays_end_3)
            contact = Contact(name=name, surname=surname, email=email, telegram=telegram,
                              slack=slack, preferences=preferences, holidays=holidays)
            contact.save()
            return contact
        else:
            raise Exception("Holidays begin must be prior holidays end")

    
    def update_contact(self, email_old, name, surname, email, telegram_username, slack_email, use_email, use_telegram,
                       use_slack, holidays_begin_1, holidays_end_1, holidays_begin_2, holidays_end_2, holidays_begin_3,
                       holidays_end_3):
        if (holidays_begin_1 is None and holidays_end_1 is None) or (
                holidays_begin_1 is not None and holidays_end_1 is not None and holidays_begin_1 <= holidays_end_1):
            contact = self.find_contact_by_email(email_old)
            if contact:
                contact.name = name
                contact.surname = surname
                contact.email = email
                contact.telegram.username = telegram_username
                contact.slack.email = slack_email
                contact.preferences.use_email = use_email
                contact.preferences.use_telegram = use_telegram
                contact.preferences.use_slack = use_slack
                contact.holidays.begin_1 = holidays_begin_1
                contact.holidays.end_1 = holidays_end_1
                contact.holidays.begin_2 = holidays_begin_2
                contact.holidays.end_2 = holidays_end_2
                contact.holidays.begin_3 = holidays_begin_3
                contact.holidays.end_3 = holidays_end_3
                contact.save()
            return contact
        raise Exception("Holidays begin must be prior holidays end")

    
    def find_contact_by_email(self, query):
        query_result = Contact.objects(email=query)
        return self.first_element_if_exists(query_result)

    
    def delete_contact(self, contact: Contact):
        contact.delete()

    
    def find_contacts(self, keyword):
        regex = re.compile(f".*{keyword}.*", re.IGNORECASE)
        query_result = Contact.objects()
        return list(filter(lambda contact: regex.match(contact.name) or regex.match(contact.surname) or regex.match(
            contact.email) or (contact.telegram.username is not None and regex.match(contact.telegram.username)) or (contact.slack.email is not None and regex.match(contact.slack.email)), query_result))

    
    def list_contacts(self, ) -> QuerySet:
        return Contact.objects()

    # PROJECT METHODS
    
    def insert_project(self, name, url):
        project = Project(name=name, url=url)
        project.save()
        return project

    
    def update_project(self, url_old, name, url):
        project = self.find_project_by_url(url_old)
        if project:
            project.name = name
            project.url = url
            project.save()
        return project

    
    def find_project_by_url(self, url):
        query_result = Project.objects(url=url)
        return self.first_element_if_exists(query_result)

    
    def delete_project(self, project: Project):
        project.delete()

    
    def find_projects(self, keyword):
        regex = re.compile(f".*{keyword}.*", re.IGNORECASE)
        query_result = Project.objects()
        return list(filter(lambda project: regex.match(project.name) or regex.match(project.url), query_result))

    
    def list_projects(self) -> QuerySet:
        return Project.objects()

    # SUBSCRIPTION METHODS
    
    def insert_subscription(self, contact_email, project_url, sub_priority, sub_keywords):
        contact_query_result = Contact.objects(email=contact_email)
        project_query_result = Project.objects(url=project_url)
        contact = self.first_element_if_exists(contact_query_result)
        project = self.first_element_if_exists(project_query_result)
        if contact and project:
            subscription = Subscription(contact=contact, project=project, priority=sub_priority,
                                        keywords=sub_keywords)
            subscription.save()
            return subscription
        else:
            raise Exception("Contact or project does not exist in the database")

    
    def update_subscription(self, contact_email_old, project_url_old, contact_email, project_url, sub_priority,
                            sub_keywords):
        subscription = self.find_subscription_by_email_url(contact_email_old, project_url_old)
        if subscription:
            subscription.contact = self.find_contact_by_email(contact_email)
            subscription.project = self.find_project_by_url(project_url)
            subscription.priority = sub_priority
            subscription.keywords = sub_keywords
            subscription.save()
        return subscription

    
    def delete_subscription(self, subscription: Subscription):
        subscription.delete()

    
    def find_subscription_by_email_url(self, email, url):
        contact_query_result = Contact.objects(email=email)
        project_query_result = Project.objects(url=url)
        contact = self.first_element_if_exists(contact_query_result)
        project = self.first_element_if_exists(project_query_result)
        query_result = Subscription.objects(contact=contact, project=project)
        return self.first_element_if_exists(query_result)


    def find_subscriptions(self, keyword):
        regex = re.compile(f".*{keyword}.*", re.IGNORECASE)
        query_result = Subscription.objects()
        return list(filter(lambda subscription: regex.match(subscription.contact.name) or regex.match(
            subscription.contact.surname) or regex.match(
            subscription.contact.email) or (subscription.contact.slack.email is not None and regex.match(
            subscription.contact.slack.email)) or (subscription.contact.telegram.username is not None and regex.match(subscription.contact.telegram.username)) or regex.match(
            subscription.project.name) or regex.match(
            subscription.project.url), query_result))

    
    def list_subscriptions(self) -> QuerySet:
        return Subscription.objects()

    
    def update_telegram_id(self, telegram_username, telegram_id) -> None:
        telegram_query_result = Contact.objects(telegram__username=telegram_username)
        contact = self.first_element_if_exists(telegram_query_result)
        if contact:
            contact.telegram.id = telegram_id
            contact.save()
        else:
            raise Exception("Telegram username does not exist in the database")

    
    def update_slack_id(self, slack_email, slack_id) -> None:
        slack_query_result = Contact.objects(slack__email=slack_email)
        contact = self.first_element_if_exists(slack_query_result)
        if contact:
            contact.slack.id = slack_id
            contact.save()
        else:
            raise Exception("Slack email does not exist in the database")

    
    def get_interested_recipients(self, data: dict) -> dict:
        project_url = data["project_url"]
        description = data["description"]
        project = self.find_project_by_url(project_url)
        subscription_query_result = Subscription.objects(project=project)
        if subscription_query_result:
            recipients = dict(telegram=list(), email=list(), slack=list())
            priority_to_email = {1: [], 2: [], 3: []}
            for record in subscription_query_result:
                if (
                        record.contact.holidays.begin_1 is None or date.today() < record.contact.holidays.begin_1 or date.today() > record.contact.holidays.end_1) and (
                        record.contact.holidays.begin_2 is None or date.today() < record.contact.holidays.begin_2 or date.today() > record.contact.holidays.end_2) and (
                        record.contact.holidays.begin_3 is None or date.today() < record.contact.holidays.begin_3 or date.today() > record.contact.holidays.end_3):
                    matches_keywords = False
                    i = 0
                    while not matches_keywords and i < len(record.keywords):
                        if re.match(f".*{record.keywords[i][1:-1]}.*", description, re.IGNORECASE | re.DOTALL):
                            matches_keywords = True
                        else:
                            i += 1
                    if matches_keywords or len(record.keywords) == 0:
                        priority_to_email[record.priority].append(record.contact.email)
            i = 3
            added = False
            while not added and i > 0:
                if len(priority_to_email[i]):
                    for email in priority_to_email[i]:
                        self.add_recipients_to_dict(recipients, email)
                    added = True
                else:
                    i -= 1
            return recipients
        else:
            return None


    
    def add_recipients_to_dict(self, recipients: dict, contact_email: str) -> None:
        contact_query_result = Contact.objects(email=contact_email)
        contact = self.first_element_if_exists(contact_query_result)
        if contact.preferences.use_telegram and contact.telegram.id:
            recipients["telegram"].append(contact.telegram.id)
        if contact.preferences.use_email:
            recipients["email"].append(contact.email)
        if contact.preferences.use_slack and contact.slack.id:
            recipients["slack"].append(contact.slack.id)
