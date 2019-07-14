from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from mongodb.mongo import Mongo
from json import load
from json import dumps
from pathlib import Path


class Application:
    def __init__(self, flask: Flask, mongo: Mongo):
        self._app = flask
        self._mongo = mongo
        self._add_api_routes()
        self._add_website_routes()

    def _shutdown_app(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def close(self):
        Application._shutdown_app()
        self._producer.close()

    def start(self, host: str, port: int):
        self._app.run(host=host, port=port)

    def _add_api_routes(self):

        @self._app.route('/api/v1/contacts', methods=['GET'])
        def api_list_contacts():
            return self._mongo.list_contacts().to_json()

        @self._app.route('/api/v1/contacts', methods=['POST'])
        def api_insert_contact():
            data = request.json
            if 'contact_name' in data.keys():
                name = data['contact_name']
            else:
                return dumps({"errore": "Nome mancante"})
            if 'contact_surname' in data.keys():
                surname = data['contact_surname']
            else:
                return dumps({"errore": "Cognome mancante"})
            if 'contact_email' in data.keys():
                email = data['contact_email']
            else:
                return dumps({"errore": "Email mancante"})
            telegram_username = data['contact_telegram_username'] if 'contact_telegram_username' else None
            slack_email = data['contact_slack_email'] if 'contact_slack_email' in data.keys() else None
            use_email = data['contact_use_email'] if 'contact_use_email' in data.keys() else False
            use_telegram = data['contact_use_telegram'] if 'contact_use_telegram' in data.keys() else False
            use_slack = data['contact_use_slack'] if 'contact_use_slack' in data.keys() else False
            holidays_begin_1 = data['contact_holidays_begin_1'] if 'contact_holidays_begin_1' in data.keys() else None
            holidays_end_1 = data['contact_holidays_end_1'] if 'contact_holidays_end_1' in data.keys() else None
            holidays_begin_2 = data['contact_holidays_begin_2'] if 'contact_holidays_begin_2' in data.keys() else None
            holidays_end_2 = data['contact_holidays_end_2'] if 'contact_holidays_end_2' in data.keys() else None
            holidays_begin_3 = data['contact_holidays_begin_3'] if 'contact_holidays_begin_3' in data.keys() else None
            holidays_end_3 = data['contact_holidays_end_3'] if 'contact_holidays_end_3' in data.keys() else None
            try:
                self._mongo.insert_contact(name, surname, email, telegram_username, slack_email, use_email,
                                           use_telegram, use_slack, holidays_begin_1, holidays_end_1, holidays_begin_2, holidays_end_2, holidays_begin_3, holidays_end_3)
            except Exception as e:
                return dumps({"errore": str(e)})
            return dumps({"ok": "Contatto inserito"})

        @self._app.route('/api/v1/contacts', methods=['PUT'])
        def api_update_contact():
            data = request.json
            if 'contact_email_old' in data.keys():
                contact = self._mongo.find_contact_by_email(data['contact_email_old'])
                if contact is None:
                    return dumps({"errore": "Contatto da modificare inesistente"})
            else:
                return dumps({"errore": "Email del contatto da modificare mancante"})
            name = data['contact_name'] if 'contact_name' in data.keys() else contact.name
            surname = data['contact_surname'] if 'contact_surname' in data.keys() else contact.surname
            email = data['contact_email'] if 'contact_email' in data.keys() else contact.email
            telegram_username = data[
                'contact_telegram_username'] if 'contact_telegram_username' in data.keys() else contact.telegram.username
            slack_email = data['contact_slack_email'] if 'contact_slack_email' in data.keys() else contact.slack.email
            use_email = data[
                'contact_use_email'] if 'contact_use_email' in data.keys() else contact.preferences.use_email
            use_telegram = data[
                'contact_use_telegram'] if 'contact_use_telegram' in data.keys() else contact.preferences.use_telegram
            use_slack = data[
                'contact_use_slack'] if 'contact_use_slack' in data.keys() else contact.preferences.use_slack
            holidays_begin_1 = data[
                'contact_holidays_begin_1'] if 'contact_holidays_begin_1' in data.keys() else contact.holidays.begin_1
            holidays_end_1 = data[
                'contact_holidays_end_1'] if 'contact_holidays_end_1' in data.keys() else contact.holidays.end_1
            holidays_begin_2 = data[
                'contact_holidays_begin_2'] if 'contact_holidays_begin_2' in data.keys() else contact.holidays.begin_2
            holidays_end_2 = data[
                'contact_holidays_end_2'] if 'contact_holidays_end_2' in data.keys() else contact.holidays.end_2
            holidays_begin_3 = data[
                'contact_holidays_begin_3'] if 'contact_holidays_begin_3' in data.keys() else contact.holidays.begin_3
            holidays_end_3 = data[
                'contact_holidays_end_3'] if 'contact_holidays_end_3' in data.keys() else contact.holidays.end_3
            try:
                self._mongo.update_contact(data['contact_email_old'], name, surname, email, telegram_username,
                                           slack_email, use_email, use_telegram, use_slack, holidays_begin_1, holidays_end_1, holidays_begin_2, holidays_end_2, holidays_begin_3, holidays_end_3)
            except Exception as e:
                return dumps({"errore": str(e)})
            return dumps({"ok": "Contatto aggiornato"})

        @self._app.route('/api/v1/contacts', methods=['DELETE'])
        def api_delete_contact():
            data = request.json
            if 'email_to_delete' in data.keys():
                query = data['email_to_delete']
            else:
                return dumps({"errore": "Email del contatto da eliminare mancante"})
            contact_to_delete = self._mongo.find_contact_by_email(query)
            if contact_to_delete is not None:
                self._mongo.delete_contact(contact_to_delete)
                return dumps({"ok": "Contatto eliminato"})
            else:
                return dumps({"errore": "Contatto inesistente"})

        @self._app.route('/api/v1/projects', methods=['GET'])
        def api_list_projects():
            return self._mongo.list_projects().to_json()

        @self._app.route('/api/v1/projects', methods=['POST'])
        def api_insert_project():
            data = request.json
            if 'project_name' in data.keys():
                name = data['project_name']
            else:
                return dumps({"errore": "Nome mancante"})
            if 'project_url' in data.keys():
                url = data['project_url']
            else:
                return dumps({"errore": "Url mancante"})
            try:
                self._mongo.insert_project(name, url)
            except Exception as e:
                return dumps({"errore": str(e)})
            return dumps({"ok": "Progetto inserito"})

        @self._app.route('/api/v1/projects', methods=['PUT'])
        def api_update_project():
            data = request.json
            if 'project_url_old' in data.keys():
                project = self._mongo.find_project_by_url(data['project_url_old'])
            else:
                return dumps({"errore": "Url del progetto da modificare mancante"})
            name = data['project_name'] if 'project_name' in data.keys() else project.name
            url = data['project_url'] if 'project_url' in data.keys() else project.url
            try:
                self._mongo.update_project(data['project_url_old'], name, url)
            except Exception as e:
                return dumps({"errore": str(e)})
            return dumps({"ok": "Progetto aggiornato"})

        @self._app.route('/api/v1/projects', methods=['DELETE'])
        def api_delete_project():
            data = request.json
            if 'url_to_delete' in data.keys():
                query = data['url_to_delete']
            else:
                return dumps({"errore": "Url del progetto da eliminare mancante"})
            project_to_delete = self._mongo.find_project_by_url(query)
            if project_to_delete is not None:
                self._mongo.delete_project(project_to_delete)
                return dumps({"ok": "Progetto eliminato"})
            else:
                return dumps({"errore": "Progetto inesistente"})

        @self._app.route('/api/v1/subscriptions', methods=['GET'])
        def api_list_subscriptions():
            return self._mongo.list_subscriptions().to_json()

        @self._app.route('/api/v1/subscriptions', methods=['POST'])
        def api_insert_subscription():
            data = request.json
            if 'contact_email' in data.keys():
                email = data['contact_email']
            else:
                return dumps({"errore": "Email del contatto mancante"})
            if 'project_url' in data.keys():
                url = data['project_url']
            else:
                return dumps({"errore": "Url del progetto mancante"})
            priority = data['subscription_priority'] if 'subscription_priority' in data.keys() else 1
            keywords = data['subscription_keywords'].replace(' ', '').split(
                ',') if 'subscription_keywords' in data.keys() else []
            try:
                self._mongo.insert_subscription(email, url, priority, keywords)
            except Exception as e:
                return dumps({"errore": str(e)})
            return dumps({"ok": "Iscrizione inserita"})

        @self._app.route('/api/v1/subscriptions', methods=['PUT'])
        def api_update_subscription():
            data = request.json
            if 'project_url_old' and 'contact_email_old' in data.keys():
                subscription = self._mongo.find_subscription_by_email_url(data['contact_email_old'],
                                                                          data['project_url_old'])
            else:
                return dumps({"errore": "Email del contatto o url del progetto dell'iscrizione da modificare mancanti"})
            email = data['contact_email'] if 'contact_email' in data.keys() else subscription.email
            url = data['project_url'] if 'project_url' in data.keys() else subscription.url
            priority = data[
                'subscription_priority'] if 'subscription_priority' in data.keys() else subscription.priority
            keywords = data['subscription_keywords'].replace(' ', '').split(
                ',') if 'subscription_keywords' in data.keys() else []
            try:
                self._mongo.update_subscription(data['contact_email_old'], data['project_url_old'], email, url,
                                                priority, keywords)
            except Exception as e:
                return dumps({"errore": str(e)})
            return dumps({"ok": "Iscrizione aggiornata"})

        @self._app.route('/api/v1/subscriptions', methods=['DELETE'])
        def api_delete_subscription():
            data = request.json
            if 'email_to_delete' in data.keys() and 'url_to_delete' in data.keys():
                email_to_delete = data['email_to_delete']
                url_to_delete = data['url_to_delete']
            else:
                return dumps({"errore": "Email o url dell'iscrizione da eliminare mancanti"})
            subscription_to_delete = self._mongo.find_subscription_by_email_url(email_to_delete, url_to_delete)
            if subscription_to_delete is not None:
                self._mongo.delete_subscription(subscription_to_delete)
                return dumps({"ok": "Iscrizione eliminata"})
            else:
                return dumps({"errore": "Iscrizione inesistente"})

    def _add_website_routes(self):

        @self._app.route('/')
        def index():
            return render_template('index.html')

        @self._app.route('/insert_contact', methods=['POST'])
        def insert_contact():
            if request.method == 'POST':
                name = request.form['contact_name']
                surname = request.form['contact_surname']
                email = request.form['contact_email']
                telegram_username = None
                if request.form['contact_telegram_username']:
                    telegram_username = request.form['contact_telegram_username']
                slack_email = None
                if request.form['contact_slack_email']:
                    slack_email = request.form['contact_slack_email']
                use_email = False
                if request.form.get('contact_use_email'):
                    use_email = True
                use_telegram = False
                if request.form.get('contact_use_telegram'):
                    use_telegram = True
                use_slack = False
                if request.form.get('contact_use_slack'):
                    use_slack = True
                holidays_begin_1 = None
                if request.form['contact_holidays_begin_1']:
                    holidays_begin_1 = request.form['contact_holidays_begin_1']
                holidays_end_1 = None
                if request.form['contact_holidays_end_1']:
                    holidays_end_1 = request.form['contact_holidays_end_1']
                holidays_begin_2 = None
                if request.form['contact_holidays_begin_2']:
                    holidays_begin_2 = request.form['contact_holidays_begin_2']
                holidays_end_2 = None
                if request.form['contact_holidays_end_2']:
                    holidays_end_2 = request.form['contact_holidays_end_2']
                holidays_begin_3 = None
                if request.form['contact_holidays_begin_3']:
                    holidays_begin_3 = request.form['contact_holidays_begin_3']
                holidays_end_3 = None
                if request.form['contact_holidays_end_3']:
                    holidays_end_3 = request.form['contact_holidays_end_3']
            try:
                self._mongo.insert_contact(name, surname, email, telegram_username, slack_email, use_email,
                                           use_telegram, use_slack, holidays_begin_1, holidays_end_1, holidays_begin_2, holidays_end_2, holidays_begin_3, holidays_end_3)
            except Exception as e:
                return render_template('error.html', error_message=str(e))
            return redirect(url_for('contacts'))

        @self._app.route('/insert_project', methods=['POST'])
        def insert_project():
            if request.method == 'POST':
                name = request.form['project_name']
                url = request.form['project_url']
                try:
                    self._mongo.insert_project(name, url)
                except Exception as e:
                    return render_template('error.html', error_message=str(e))
                return redirect(url_for('projects'))

        @self._app.route('/insert_subscription', methods=['POST'])
        def insert_subscription():
            if request.method == 'POST':
                email = request.form['contact_email']
                url = request.form['project_url']
                priority = request.form['subscription_priority']
                keywords = list(filter(None, request.form['subscription_keywords'].replace(' ', '').split(',')))
                try:
                    self._mongo.insert_subscription(email, url, priority, keywords)
                except Exception as e:
                    return render_template('error.html', error_message=str(e))
                return redirect(url_for('subscriptions'))

        @self._app.route('/contacts')
        def contacts():
            return render_template('contacts.html', contacts_array=self._mongo.list_contacts())

        @self._app.route('/find_contacts', methods=['GET', 'POST'])
        def find_contacts():
            if request.form['keyword']:
                keyword = request.form['keyword'].strip()
                return render_template('contacts.html', contacts_array=self._mongo.find_contacts(keyword))
            return redirect(url_for('contacts'))

        @self._app.route('/projects')
        def projects():
            return render_template('projects.html', projects_array=self._mongo.list_projects())

        @self._app.route('/find_projects', methods=['GET', 'POST'])
        def find_projects():
            keyword = request.form['keyword']
            return render_template('projects.html', projects_array=self._mongo.find_projects(keyword))

        @self._app.route('/subscriptions')
        def subscriptions():
            return render_template('subscriptions.html', subscriptions_array=self._mongo.list_subscriptions())

        @self._app.route('/find_subscriptions', methods=['GET', 'POST'])
        def find_subscriptions():
            keyword = request.form['keyword']
            return render_template('subscriptions.html', subscriptions_array=self._mongo.find_subscriptions(keyword))

        @self._app.route('/delete_contact', methods=['POST'])
        def delete_contact():
            if request.method == 'POST':
                query = request.form['email_to_delete']
                contact_to_delete = self._mongo.find_contact_by_email(query)
                self._mongo.delete_contact(contact_to_delete)
                return render_template('contacts.html', contacts_array=self._mongo.list_contacts())

        @self._app.route('/delete_project', methods=['POST'])
        def delete_project():
            if request.method == 'POST':
                query = request.form['url_to_delete']
                project_to_delete = self._mongo.find_project_by_url(query)
                self._mongo.delete_project(project_to_delete)
                return render_template('projects.html', projects_array=self._mongo.list_projects())

        @self._app.route('/delete_subscription', methods=['POST'])
        def delete_subscription():
            if request.method == 'POST':
                contact_email = request.form['email_to_delete']
                project_url = request.form['url_to_delete']
                subscription_to_delete = self._mongo.find_subscription_by_email_url(contact_email, project_url)
                self._mongo.delete_subscription(subscription_to_delete)
                return render_template('subscriptions.html', subscriptions_array=self._mongo.list_subscriptions())

        @self._app.route('/update_contact', methods=['POST'])
        def update_contact():
            if request.method == 'POST':
                email_old = request.form['contact_email_old']
                name = request.form['contact_name']
                surname = request.form['contact_surname']
                email = request.form['contact_email']
                telegram_username = request.form['contact_telegram_username']
                slack_email = None
                if request.form['contact_slack_email']:
                    slack_email = request.form['contact_slack_email']
                use_email = False
                if request.form.get('contact_use_email'):
                    use_email = True
                use_telegram = False
                if request.form.get('contact_use_telegram'):
                    use_telegram = True
                use_slack = False
                if request.form.get('contact_use_slack'):
                    use_slack = True
                holidays_begin_1 = None
                holidays_end_1 = None
                if request.form['contact_holidays_begin_1'] and request.form['contact_holidays_end_1']:
                    holidays_begin_1 = request.form['contact_holidays_begin_1']
                    holidays_end_1 = request.form['contact_holidays_end_1']
                holidays_begin_2 = None
                holidays_end_2 = None
                if request.form['contact_holidays_begin_2'] and request.form['contact_holidays_end_2']:
                    holidays_begin_2 = request.form['contact_holidays_begin_2']
                    holidays_end_2 = request.form['contact_holidays_end_2']
                holidays_begin_3 = None
                holidays_end_3 = None
                if request.form['contact_holidays_begin_3'] and request.form['contact_holidays_end_3']:
                    holidays_begin_3 = request.form['contact_holidays_begin_3']
                    holidays_end_3 = request.form['contact_holidays_end_3']
            try:
                self._mongo.update_contact(email_old, name, surname, email, telegram_username, slack_email, use_email,
                                           use_telegram, use_slack, holidays_begin_1, holidays_end_1, holidays_begin_2, holidays_end_2, holidays_begin_3, holidays_end_3)
            except Exception as e:
                return render_template('error.html', error_message=str(e))
            return redirect(url_for('contacts'))

        @self._app.route('/update_project', methods=['POST'])
        def update_project():
            if request.method == 'POST':
                url_old = request.form['project_url_old']
                name = request.form['project_name']
                url = request.form['project_url']
                try:
                    self._mongo.update_project(url_old, name, url)
                except Exception as e:
                    return render_template('error.html', error_message=str(e))
                return redirect(url_for('projects'))

        @self._app.route('/update_subscription', methods=['POST'])
        def update_subscription():
            if request.method == 'POST':
                email_old = request.form['contact_email_old']
                url_old = request.form['project_url_old']
                email = request.form['contact_email']
                url = request.form['project_url']
                priority = request.form['subscription_priority']
                keywords = list(filter(None, request.form['subscription_keywords'].replace(' ', '').split(',')))
                try:
                    self._mongo.update_subscription(email_old, url_old, email, url, priority, keywords)
                except Exception as e:
                    return render_template('error.html', error_message=str(e))
                return redirect(url_for('subscriptions'))


def start_application(config: dict):
    mongo = Mongo(configs["mongo"]["db_name"], configs["mongo"]["host"], configs["mongo"]["port"])
    flask = Flask(configs["application"]["app_name"])
    server = Application(flask, mongo)
    try:
        server.start(configs["application"]["ip"], configs["application"]["port"])
    except KeyboardInterrupt:
        exit(1)
    finally:
        server.close()


if __name__ == '__main__':
    CONFIG_PATH = Path(__file__).parents[0] / 'config' / 'config.json'
    with open(CONFIG_PATH) as file:
        configs = load(file)
        start_application(configs)
