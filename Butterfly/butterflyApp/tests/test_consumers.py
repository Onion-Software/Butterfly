import consumers
import importlib
emaillib= importlib.import_module("consumers.email-consumer.email_script")
slacklib= importlib.import_module("consumers.slack-consumer.slack")
telegramlib= importlib.import_module("consumers.telegram-consumer.telegram")
import pytest


class TestConsumer(object):
    def test_KafkaConsumerFactorySuccess(self, mocker):
        mockkafka = mocker.patch('consumers.consumer.KafkaConsumer')
        mockkafka.return_value = True
        assert consumers.consumer.KafkaConsumerFactory.create({}, "example") == True

    
    def test_KafkaConsumerFactoryFailureNoBrokers(self, mocker):
        mockkafka = mocker.patch('consumers.consumer.KafkaConsumer')
        mockkafka.side_effect = consumers.consumer.errors.NoBrokersAvailable
        with pytest.raises(Exception):
            consumers.consumer.KafkaConsumerFactory.create({}, "")
    

    def test_KafkaConsumerFactoryFailureKeybardInterrupt(self,mocker):
        mockkafka = mocker.patch('consumers.consumer.KafkaConsumer')
        mockkafka.side_effect = KeyboardInterrupt
        with pytest.raises(SystemExit) as keyerror:
            consumers.consumer.KafkaConsumerFactory.create({}, "")
            assert keyerror.type == SystemExit
            assert keyerror.value.code == 42


class TestBaseConsumer(object):

    class tester(consumers.consumer.Consumer):
        def consume(self,str):
            return str

    def test_create_BaseConsumer(self,mocker):
        mockkafka = mocker.patch('consumers.consumer.KafkaConsumer')
        obj=TestBaseConsumer.tester(mockkafka)
        assert mockkafka==obj._consumer

    def test_BaseConsumer_start(self,mocker):
        mockkafka = mocker.patch('consumers.consumer.KafkaConsumer')
        mockkafka.message.value="x"
        obj=TestBaseConsumer.tester(mockkafka.return_value)
        obj.start()
        # assert_called_with(mockkafka.message.value)

    def test_BaseConsumer_get_topic_list(self,mocker):
        mockkafka = mocker.patch('consumers.consumer.KafkaConsumer')
        kaf=mockkafka.return_value
        obj=TestBaseConsumer.tester(kaf)
        assert obj.get_topic_list()==kaf.topics()

    def test_BaseConsumer_get_subscription(self,mocker):
        mockkafka = mocker.patch('consumers.consumer.KafkaConsumer')
        kaf=mockkafka.return_value
        obj=TestBaseConsumer.tester(kaf)
        assert obj.get_subscription()==kaf.subscription()

    def test_BaseConsumer_close(self,mocker):
        mockkafka = mocker.patch('consumers.consumer.KafkaConsumer')
        obj=TestBaseConsumer.tester(mockkafka)
        obj.close()
        obj._consumer.close.assert_called_with()


class TestEmail(object):



    def test_create_MailSender(self,mocker):
        mockSMTP=mocker.patch('consumers.email-consumer.email_script.SMTP')
        SMTPfortest=mockSMTP.returnvalue
        obj=emaillib.MailSender(SMTPfortest, 22, "email@test.it", "password")
        assert obj._smtp == SMTPfortest
        assert obj._port == 22
        assert obj._email == "email@test.it"
        assert obj._password == "password"
        mockSMTP.assert_called_once_with()

    def test_MailSender_send(self,mocker):
        mockSMTP=mocker.patch('consumers.email-consumer.email_script.SMTP')
        SMTPfortest=mockSMTP.returnvalue
        obj=emaillib.MailSender(SMTPfortest, 22, "email@test.it", "password")
        obj.send('Recipient','Message')

        obj._server.sendmail.assert_called_with(obj._email, 'Recipient', 'Message')
        obj._server.quit.assert_called_with()

    def test_MailSender_getEmail(self,mocker):
        mockSMTP=mocker.patch('consumers.email-consumer.email_script.SMTP')
        SMTPfortest=mockSMTP.returnvalue
        obj=emaillib.MailSender(SMTPfortest, 22, "email@test.it", "password")
        assert obj.getEmail()== "email@test.it"

    def test_create_EmailConsumer(self,mocker):
        mockMailSender=mocker.patch('consumers.email-consumer.email_script.MailSender')
        mockKafkaConsumer=mocker.patch('consumers.email-consumer.email_script.KafkaConsumer')
        mockConsumer=mocker.patch('consumers.consumer.Consumer')
        obj=emaillib.EmailConsumer(mockKafkaConsumer, mockMailSender)
        assert obj._sender == mockMailSender        

    def test_EmailConsumer_consume(self,mocker):
        mockMailSender=mocker.patch('consumers.email-consumer.email_script.MailSender')
        mockKafkaConsumer=mocker.patch('consumers.email-consumer.email_script.KafkaConsumer')
        mockk=mockKafkaConsumer.return_value
        mockConsumer=mocker.patch('consumers.consumer.Consumer')
        mockf=mocker.patch('consumers.email-consumer.email_script.EmailConsumer.extract_recipient_list')
        mockf.return_value="a@fmail.com"
        mockMailSender.return_value.getEmail.return_value="getEmail"
        mockf2=mocker.patch('consumers.email-consumer.email_script.EmailConsumer._decorate')
        mockf2.return_value="xx","yy"
        obj=emaillib.EmailConsumer(mockk, mockMailSender.return_value)
        obj.consume({})

    def test_EmailConsumer_extract_recipient_list(self,mocker):
        mockMailSender=mocker.patch('consumers.email-consumer.email_script.MailSender')
        mockKafkaConsumer=mocker.patch('consumers.email-consumer.email_script.KafkaConsumer')
        mockConsumer=mocker.patch('consumers.consumer.Consumer')
        obj=emaillib.EmailConsumer(mockKafkaConsumer, mockMailSender)
        assert obj.extract_recipient_list({'recipients': 'egg', 'b': 'spam'})
    
    def test_EmailConsumer_decorate_newissue(self,mocker):
        mockMailSender=mocker.patch('consumers.email-consumer.email_script.MailSender')
        mockKafkaConsumer=mocker.patch('consumers.email-consumer.email_script.KafkaConsumer')
        mockConsumer=mocker.patch('consumers.consumer.Consumer')
        mockf=mocker.patch('consumers.email-consumer.email_script.EmailConsumer._read_html')
        obj=emaillib.EmailConsumer(mockKafkaConsumer, mockMailSender)
        obj._decorate({"author":"", "object_kind":"", "project_name":"", "project_url":"", "app":"", "issue_url":"", "title":"", "status":"", "last_edited_at":"", "last_edited_by":"", "last_edited_by_id":"", "created_on":"22", "description":"bad"})
        
    def test_EmailConsumer_decorate_push(self,mocker):
        mockMailSender=mocker.patch('consumers.email-consumer.email_script.MailSender')
        mockKafkaConsumer=mocker.patch('consumers.email-consumer.email_script.KafkaConsumer')
        mockConsumer=mocker.patch('consumers.consumer.Consumer')
        mockf=mocker.patch('consumers.email-consumer.email_script.EmailConsumer._read_html')
        obj=emaillib.EmailConsumer(mockKafkaConsumer, mockMailSender)
        obj._decorate({"author":"", "object_kind":"", "project_name":"", "project_url":"", "app":"", "commits_url":"", "commits_author_name":"","commits_author_email":"", "title":"", "status":"", "last_edited_at":"", "last_edited_by":"", "last_edited_by_id":"", "created_on":"22", "description":"bad"})
        
    def test_EmailConsumer_decorate_redmineissue(self,mocker):
        mockMailSender=mocker.patch('consumers.email-consumer.email_script.MailSender')
        mockKafkaConsumer=mocker.patch('consumers.email-consumer.email_script.KafkaConsumer')
        mockConsumer=mocker.patch('consumers.consumer.Consumer')
        mockf=mocker.patch('consumers.email-consumer.email_script.EmailConsumer._read_html')
        obj=emaillib.EmailConsumer(mockKafkaConsumer, mockMailSender)
        obj._decorate({"priority":"","author":"", "object_kind":"", "project_name":"", "project_url":"", "app":"", "subject":"", "title":"", "status":"", "last_edited_at":"", "last_edited_by":"", "state":"","last_edited_by_id":"", "created_on":"22", "description":"bad"})
    
    def test_start_email_consumer(self,mocker):
        mockSMTP=mocker.patch('consumers.email-consumer.email_script.SMTP')
        mockMailSender=mocker.patch('consumers.email-consumer.email_script.MailSender')
        mockKafkaConsumerFactory=mocker.patch('consumers.email-consumer.email_script.KafkaConsumerFactory')
        mockEmailConsumer=mocker.patch('consumers.email-consumer.email_script.EmailConsumer')
        emaillib.start_email_consumer({"email": { "smtp": "s", "port": "p", "password": "", "sender": ""}, "kafka_consumer": "", "kafka_topics":{"topic_consumer_name_list": {"email": ""}}})
        mockMailSender.assert_called_with("s", "p", "", "")
        mockKafkaConsumerFactory.create.assert_called_with("", [""])
        mockEmailConsumer.assert_called_with(mockKafkaConsumerFactory.create.return_value, mockMailSender.return_value)
        mockEmailConsumer.return_value.start.assert_called_with()
        mockEmailConsumer.return_value.close.assert_called_with()

    def test_start_email_consumer_EmailConsumer_error(self,mocker):
        mockSMTP=mocker.patch('consumers.email-consumer.email_script.SMTP')
        mockMailSender=mocker.patch('consumers.email-consumer.email_script.MailSender')
        mockKafkaConsumerFactory=mocker.patch('consumers.email-consumer.email_script.KafkaConsumerFactory')
        mockEmailConsumer=mocker.patch('consumers.email-consumer.email_script.EmailConsumer')
        mockEmailConsumer.return_value.start.side_effect= KeyboardInterrupt
        with pytest.raises(SystemExit) as keyerror:
            emaillib.start_email_consumer({"email": { "smtp": "", "port": "", "password": "", "sender": ""}, "kafka_consumer": "", "kafka_topics":{"topic_consumer_name_list": {"email": ""}}})
            assert keyerror.type == SystemExit
            assert keyerror.value.code == 42

        
    def test_start_email_consumer_Kafka_error(self,mocker):
        mockSMTP=mocker.patch('consumers.email-consumer.email_script.SMTP')
        mockMailSender=mocker.patch('consumers.email-consumer.email_script.MailSender')
        mockKafkaConsumerFactory=mocker.patch('consumers.email-consumer.email_script.KafkaConsumerFactory')
        mockKafkaConsumerFactory.create.side_effect= Exception
        with pytest.raises(SystemExit) as keyerror:
            emaillib.start_email_consumer({"email": { "smtp": "", "port": "", "password": "", "sender": ""}, "kafka_consumer": "", "kafka_topics":{"topic_consumer_name_list": {"email": ""}}})
            assert keyerror.type == SystemExit
            assert keyerror.value.code == 42



class TestSlack():

    def test_createSlackBot(self,mocker):
        mockSlackClient=mocker.patch('consumers.slack-consumer.slack.SlackClient')
        mockMongo=mocker.patch('consumers.slack-consumer.slack.Mongo')
        slacktest=slacklib.SlackBot(mockSlackClient,mockMongo)
        assert slacktest._mongo == mockMongo
        assert slacktest._client == mockSlackClient
        assert slacktest._isListening == False

    def test_SlackBot_send_message(self,mocker):
        mockSlackClient=mocker.patch('consumers.slack-consumer.slack.SlackClient')
        mockMongo=mocker.patch('consumers.slack-consumer.slack.Mongo')
        slacktest=slacklib.SlackBot(mockSlackClient.return_value,mockMongo.return_value)
        slacktest.send_message("Alice", "Hi from Bob")
        mockSlackClient.return_value.api_call.assert_called_with("chat.postMessage", channel="Alice", text="Hi from Bob")

    def test_SlackBot_start(self,mocker):
        mockSlackClient=mocker.patch('consumers.slack-consumer.slack.SlackClient')
        mockMongo=mocker.patch('consumers.slack-consumer.slack.Mongo')
        slacktest=slacklib.SlackBot(mockSlackClient,mockMongo)
        mockf=mocker.patch('consumers.slack-consumer.slack.SlackBot.listen')
        mockMongo.return_value.update_slack_id.return_value= "yes"
        mockSlackClient.return_value.api_call.return_value={"members":[{"profile":{"email":""}}]}
        slacktest.start()
        assert slacktest._isListening == True
        
    def test_SlackBot_listen(self,mocker):
        mockSlackClient=mocker.patch('consumers.slack-consumer.slack.SlackClient')
        mockMongo=mocker.patch('consumers.slack-consumer.slack.Mongo')
        slacktest=slacklib.SlackBot(mockSlackClient.return_value,mockMongo.return_value)
        slacktest.listen()

    def test_SlackBot_close(self,mocker):
        mockSlackClient=mocker.patch('consumers.slack-consumer.slack.SlackClient')
        mockMongo=mocker.patch('consumers.slack-consumer.slack.Mongo')
        slacktest=slacklib.SlackBot(mockSlackClient.return_value,mockMongo.return_value)
        slacktest.close()
        assert slacktest._isListening == False
        
    def test_SlackBot__parse_event(self,mocker):
        mockSlackClient=mocker.patch('consumers.slack-consumer.slack.SlackClient')
        mockMongo=mocker.patch('consumers.slack-consumer.slack.Mongo')
        slacktest=slacklib.SlackBot(mockSlackClient,mockMongo)
        mockSlackClient.api_call.return_value={"members":[{"id":"male", "profile":{"email":"com"}}]}
        slacktest._parse_event({"type":"member_joined_channel","user": "male"})
        mockMongo.update_slack_id.assert_called_once_with("com", "male")
    
    def test_create_SlackConsumer(self,mocker):
        mockSlackBot=mocker.patch('consumers.slack-consumer.slack.SlackBot')
        mockKafkaConsumer=mocker.patch('consumers.slack-consumer.slack.KafkaConsumer')
        sctest=slacklib.SlackConsumer(mockKafkaConsumer, mockSlackBot)
        assert mockSlackBot == sctest._bot
        
    def test_SlackConsumer_consume(self,mocker):
        mockSlackBot=mocker.patch('consumers.slack-consumer.slack.SlackBot')
        mockKafkaConsumer=mocker.patch('consumers.slack-consumer.slack.KafkaConsumer')
        sctest=slacklib.SlackConsumer(mockKafkaConsumer, mockSlackBot)
        mockf=mocker.patch("consumers.slack-consumer.slack.SlackConsumer._decorate")
        mockf.return_value=""
        sctest.consume({"recipients":["x"]})
        mockSlackBot.send_message.assert_called_once_with("x","")

    def test_SlackConsumer__decorate(self,mocker):
        mockSlackBot=mocker.patch('consumers.slack-consumer.slack.SlackBot')
        mockKafkaConsumer=mocker.patch('consumers.slack-consumer.slack.KafkaConsumer')
        sctest=slacklib.SlackConsumer(mockKafkaConsumer, mockSlackBot)
        sctest._decorate({"author":"", "object_kind":"", "project_name":"", "project_url":"", "app":"", "issue_url":"", "title":"", "status":"", "last_edited_at":"","last_edited_by_id":"","created_on":"", "description":""})
        
    def test_SlackConsumer_decorate_push(self,mocker):
        mockSlackBot=mocker.patch('consumers.slack-consumer.slack.SlackBot')
        mockKafkaConsumer=mocker.patch('consumers.slack-consumer.slack.KafkaConsumer')
        sctest=slacklib.SlackConsumer(mockKafkaConsumer, mockSlackBot)
        sctest._decorate({"author":"", "object_kind":"", "project_name":"", "project_url":"", "app":"", "commits_url":"", "commits_author_name":"","commits_author_email":"", "title":"", "status":"", "last_edited_at":"", "last_edited_by":"", "last_edited_by_id":"", "created_on":"22", "description":"bad"})
        
    def test_SlackConsumer_decorate_redmineissue(self,mocker):
        mockSlackBot=mocker.patch('consumers.slack-consumer.slack.SlackBot')
        mockKafkaConsumer=mocker.patch('consumers.slack-consumer.slack.KafkaConsumer')
        sctest=slacklib.SlackConsumer(mockKafkaConsumer, mockSlackBot)
        sctest._decorate({"priority":"","author":"", "object_kind":"", "project_name":"", "project_url":"", "app":"", "subject":"", "title":"", "status":"", "last_edited_at":"", "last_edited_by":"", "state":"","last_edited_by_id":"", "created_on":"22", "description":"bad"})
    
        
    def test_SlackConsumer_extract_recipient_list(self,mocker):
        mockSlackBot=mocker.patch('consumers.slack-consumer.slack.SlackBot')
        mockKafkaConsumer=mocker.patch('consumers.slack-consumer.slack.KafkaConsumer')
        sctest=slacklib.SlackConsumer(mockKafkaConsumer, mockSlackBot)
        assert sctest.extract_recipient_list({'recipients': 'egg', 'b': 'spam'})

    def test_start_slack_consumer(self,mocker):
        mockmongo=mocker.patch('consumers.slack-consumer.slack.Mongo')
        mockKafkaConsumerFactory=mocker.patch('consumers.slack-consumer.slack.KafkaConsumerFactory')
        mockslackbot=mocker.patch('consumers.slack-consumer.slack.SlackBot')
        mockslackConsumer=mocker.patch('consumers.slack-consumer.slack.SlackConsumer')
        slacklib.start_slack_consumer({"mongo":{"db_name":"dbn", "host":"h", "port":""},"slack": { "bot_token": "s"}, "kafka_consumer": "", "kafka_topics":{"topic_consumer_name_list": {"slack": ""}}})
        mockKafkaConsumerFactory.create.assert_called_with("", [""])
        mockslackbot.return_value.close.assert_called_with()
        mockslackConsumer.return_value.close.assert_called_with()


class TestTelegram:
    def test_create_TelegramBot(self,mocker):
        mocktelebot = mocker.patch('consumers.telegram-consumer.telegram.TeleBot')
        mockmongo = mocker.patch('consumers.telegram-consumer.telegram.Mongo')
        tbot=telegramlib.TelegramBot(mocktelebot, mockmongo)
        assert tbot._mongo == mockmongo
        assert tbot._bot == mocktelebot
        
    #send welcome?

    def test_TelegramBot_set_bot(self,mocker):
        mocktelebot = mocker.patch('consumers.telegram-consumer.telegram.TeleBot')
        tb=mocktelebot.return_value
        mockmongo = mocker.patch('consumers.telegram-consumer.telegram.Mongo')
        mockf = mocker.patch('consumers.telegram-consumer.telegram.TelegramBot.close')
        tbot=telegramlib.TelegramBot(mocktelebot, mockmongo)
        tbot.set_bot(tb)
        assert tbot._bot == tb

    def test_TelegramBot_get_bot(self,mocker):
        mocktelebot = mocker.patch('consumers.telegram-consumer.telegram.TeleBot')
        mockmongo = mocker.patch('consumers.telegram-consumer.telegram.Mongo')
        tbot=telegramlib.TelegramBot(mocktelebot.return_value, mockmongo.return_value)
        assert tbot.get_bot()== mocktelebot.return_value

    def test_TelegramBot_close(self,mocker):
        mocktelebot = mocker.patch('consumers.telegram-consumer.telegram.TeleBot')
        mockmongo = mocker.patch('consumers.telegram-consumer.telegram.Mongo')
        tbot=telegramlib.TelegramBot(mocktelebot, mockmongo)
        tbot.close()
        mocktelebot.stop_polling.assert_called_once_with()
        mocktelebot.stop_bot.assert_called_once_with()

    def test_TelegramBot_start(self,mocker):
        mocktelebot = mocker.patch('consumers.telegram-consumer.telegram.TeleBot')
        mockmongo = mocker.patch('consumers.telegram-consumer.telegram.Mongo')
        tbot=telegramlib.TelegramBot(mocktelebot.return_value, mockmongo.return_value)
        tbot.start()
        mocktelebot.return_value.polling.assert_called_with()


    def test_TelegramBot_send_message(self,mocker):
        mocktelebot = mocker.patch('consumers.telegram-consumer.telegram.TeleBot')
        mockmongo = mocker.patch('consumers.telegram-consumer.telegram.Mongo')
        tbot=telegramlib.TelegramBot(mocktelebot, mockmongo)
        tbot.send_message(27,"Test")
        mocktelebot.send_message.assert_called_with(27, "Test")


    def test_create_TelegramConsumer(self,mocker):
        mockKafkaConsumerFactory=mocker.patch('consumers.telegram-consumer.telegram.KafkaConsumerFactory')
        mockTelegramBot=mocker.patch('consumers.telegram-consumer.telegram.TelegramBot')
        ata=telegramlib.TelegramConsumer(mockKafkaConsumerFactory, mockTelegramBot)
        assert mockTelegramBot == ata._bot

    def test_TelegramConsumer__decorate(self,mocker):
        mockTelegramBot=mocker.patch('consumers.telegram-consumer.telegram.TelegramBot')
        mockKafkaConsumer=mocker.patch('consumers.telegram-consumer.telegram.KafkaConsumer')
        tctest=telegramlib.TelegramConsumer(mockKafkaConsumer, mockTelegramBot)
        tctest._decorate({"author":"", "object_kind":"", "project_name":"", "project_url":"", "app":"", "issue_url":"", "title":"", "status":"", "last_edited_at":"","last_edited_by_id":"","created_on":"", "description":""})
      
    def test_TelegramConsumer_decorate_push(self,mocker):
        mockTelegramBot=mocker.patch('consumers.telegram-consumer.telegram.TelegramBot')
        mockKafkaConsumer=mocker.patch('consumers.telegram-consumer.telegram.KafkaConsumer')
        tctest=telegramlib.TelegramConsumer(mockKafkaConsumer, mockTelegramBot)
        tctest._decorate({"author":"", "object_kind":"", "project_name":"", "project_url":"", "app":"", "commits_url":"", "commits_author_name":"","commits_author_email":"", "title":"", "status":"", "last_edited_at":"", "last_edited_by":"", "last_edited_by_id":"", "created_on":"22", "description":"bad"})
        
    def test_TelegramConsumer_decorate_redmineissue(self,mocker):
        mockTelegramBot=mocker.patch('consumers.telegram-consumer.telegram.TelegramBot')
        mockKafkaConsumer=mocker.patch('consumers.telegram-consumer.telegram.KafkaConsumer')
        tctest=telegramlib.TelegramConsumer(mockKafkaConsumer, mockTelegramBot)
        tctest._decorate({"priority":"","author":"", "object_kind":"", "project_name":"", "project_url":"", "app":"", "subject":"", "title":"", "status":"", "last_edited_at":"", "last_edited_by":"", "state":"","last_edited_by_id":"", "created_on":"22", "description":"bad"})
    
        
    def test_TelegramConsumer_consume(self,mocker):
        mockKafkaConsumerFactory=mocker.patch('consumers.telegram-consumer.telegram.KafkaConsumerFactory')
        mockTelegramBot=mocker.patch('consumers.telegram-consumer.telegram.TelegramBot')
        ata=telegramlib.TelegramConsumer(mockKafkaConsumerFactory, mockTelegramBot)
        mockf=mocker.patch("consumers.telegram-consumer.telegram.TelegramConsumer._decorate")
        mockf.return_value=""
        ata.consume({"recipients":["x"]})
        mockTelegramBot.send_message.assert_called_once_with("x","")


    def test_TelegramConsumer_extract_recipient_list(self,mocker):
        mockKafkaConsumerFactory=mocker.patch('consumers.telegram-consumer.telegram.KafkaConsumerFactory')
        mockTelegramBot=mocker.patch('consumers.telegram-consumer.telegram.TelegramBot')
        ata=telegramlib.TelegramConsumer(mockKafkaConsumerFactory, mockTelegramBot)
        assert ata.extract_recipient_list({'recipients':"3"}) == "3"
        

    def test_start_telegram_consumer(self,mocker):
        mockKafkaConsumerFactory=mocker.patch('consumers.telegram-consumer.telegram.KafkaConsumerFactory')
        mockMongo=mocker.patch('consumers.telegram-consumer.telegram.Mongo')
        mockTelegramBot=mocker.patch('consumers.telegram-consumer.telegram.TelegramBot')
        mockTeleBot=mocker.patch('consumers.telegram-consumer.telegram.TeleBot')
        mockTelegramConsumer=mocker.patch('consumers.telegram-consumer.telegram.TelegramConsumer')
        mockThread=mocker.patch('consumers.telegram-consumer.telegram.Thread')
        telegramlib.start_telegram_consumer({'mongo': {'db_name': "dbn", 'host': "host", 'port': "port"}, 'telegram': {'bot_token': "bot"}, 'kafka_consumer': "kc", 'kafka_topics': {'topic_consumer_name_list':{'telegram': "tel"}}})
        mockMongo.assert_called_with("dbn", "host", "port")
        mockTeleBot.assert_called_with("bot")
        mockTelegramBot.assert_called_with(mockTeleBot.return_value, mockMongo.return_value)
        mockKafkaConsumerFactory.create.assert_called_with("kc", ["tel"])
        mockTelegramConsumer.assert_called_with(mockKafkaConsumerFactory.create.return_value, mockTelegramBot.return_value)
        mockThread.return_value.start.assert_called_with()
        mockTelegramConsumer.return_value.start.assert_called_with()
        mockTelegramConsumer.return_value.close.assert_called_with()
        mockTelegramBot.return_value.close.assert_called_with()

    def test_start_telegram_consumer_KafkaConsumerFactory_error(self,mocker):
        mockKafkaConsumerFactory=mocker.patch('consumers.telegram-consumer.telegram.KafkaConsumerFactory')
        mockMongo=mocker.patch('consumers.telegram-consumer.telegram.Mongo')
        mockTelegramBot=mocker.patch('consumers.telegram-consumer.telegram.TelegramBot')
        mockTeleBot=mocker.patch('consumers.telegram-consumer.telegram.TeleBot')
        mockTelegramConsumer=mocker.patch('consumers.telegram-consumer.telegram.TelegramConsumer')
        mockThread=mocker.patch('consumers.telegram-consumer.telegram.Thread')
        mockKafkaConsumerFactory.create.side_effect= Exception
        with pytest.raises(SystemExit) as keyerror:
            telegramlib.start_telegram_consumer({'mongo': {'db_name': "dbn", 'host': "host", 'port': "port"}, 'telegram': {'bot_token': "bot"}, 'kafka_consumer': "kc", 'kafka_topics': {'topic_consumer_name_list':{'telegram': "tel"}}})
            assert keyerror.type == SystemExit
            assert keyerror.value.code == 42

    def test_start_telegram_consumer_Thread_error(self,mocker):
        mockKafkaConsumerFactory=mocker.patch('consumers.telegram-consumer.telegram.KafkaConsumerFactory')
        mockMongo=mocker.patch('consumers.telegram-consumer.telegram.Mongo')
        mockTelegramBot=mocker.patch('consumers.telegram-consumer.telegram.TelegramBot')
        mockTeleBot=mocker.patch('consumers.telegram-consumer.telegram.TeleBot')
        mockTelegramConsumer=mocker.patch('consumers.telegram-consumer.telegram.TelegramConsumer')
        mockThread=mocker.patch('consumers.telegram-consumer.telegram.Thread')
        mockThread.return_value.start.side_effect= KeyboardInterrupt
        with pytest.raises(SystemExit) as keyerror:
            telegramlib.start_telegram_consumer({'mongo': {'db_name': "dbn", 'host': "host", 'port': "port"}, 'telegram': {'bot_token': "bot"}, 'kafka_consumer': "kc", 'kafka_topics': {'topic_consumer_name_list':{'telegram': "tel"}}})
            assert keyerror.type == SystemExit
            assert keyerror.value.code == 42

if __name__ == '__main__':
    main()
