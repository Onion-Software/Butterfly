import pytest
import mongodb.mongo

class TestMongo(object):
    
    def test_create_Mongo(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        mongodb.mongo.Mongo("a", "b", "c")
        mockconnect.assert_called_once_with("a", host="b", port="c")
        
    def test_Mongo_first_element_if_exists(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        assert testm.first_element_if_exists([1, 2, 3, 4]) == 1
    
    def test_Mongo_first_element_if_exists_empty(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        assert testm.first_element_if_exists([]) == None
    
    def test_Mongo_insert_contact(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mocktelegram=mocker.patch("mongodb.mongo.Telegram")
        mockslack=mocker.patch("mongodb.mongo.Slack")
        mockpreferences=mocker.patch("mongodb.mongo.Preferences")
        mockholidays=mocker.patch("mongodb.mongo.Holidays")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mockf=mocker.patch("mongodb.mongo.Contact.save")
        mocktelegram.return_value='t'
        mockslack.return_value='s'
        mockpreferences.return_value='p'
        mockholidays.return_value='h'
        testm.insert_contact("name", "surname", "email", "telegramname", "slackemail", True, True, False, 2, 6, 1, 2, 5, 8 )
        
        mocktelegram.assert_called_once_with(username="telegramname")
        mockslack.assert_called_once_with(email="slackemail")
        mockpreferences.assert_called_once_with(use_email=True, use_telegram=True, use_slack=False)
        mockholidays.assert_called_once_with(begin_1=2, begin_2=1, begin_3=5, end_1=6, end_2=2, end_3=8)
        mockcontact.assert_called_once_with(name="name", surname="surname", email="email", telegram='t', slack='s', preferences='p', holidays='h')
        mockcontact.return_value.save.assert_called_once_with()
    
    def test_Mongo_insert_contact_exception(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        with pytest.raises(Exception):
            testm.insert_contact("name", "surname", "email", "telegramname", "slackemail", True, True, False, 2, None )

    def test_Mongo_update_contact(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mockf=mocker.patch("mongodb.mongo.Mongo.find_contact_by_email")
        con=mockcontact.return_value
        mockf.return_value=con
        testm.update_contact("oldmail", "nname", "nsurname", "nemail", "ntelegramname", "nslackemail", True, True, False, 2, 6, 1, 3, 10, 30)
        assert con.name == "nname"
        assert con.surname == "nsurname"
        assert con.email == "nemail"
        assert con.telegram.username == "ntelegramname"
        assert con.slack.email == "nslackemail"
        assert con.preferences.use_email == True
        assert con.preferences.use_telegram == True
        assert con.preferences.use_slack == False
        assert con.holidays.begin_1 == 2
        assert con.holidays.end_1 == 6
        assert con.holidays.begin_2 == 1
        assert con.holidays.end_2 == 3
        assert con.holidays.begin_3 == 10
        assert con.holidays.end_3 == 30
        con.save.assert_called_once_with()
            
    def test_Mongo_update_contact_exception(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        with pytest.raises(Exception):
            testm.update_contact("email", "name", "surname", "newemail", "telegramname", "slackemail", True, True, False, 2, None )

    
    def test_Mongo_find_contact_by_email(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mockcontact.objects.return_value=["x"]
        assert "x" == testm.find_contact_by_email("a@mail.com")
    
    def test_Mongo_delete_contact(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockcontact= mocker.patch("mongodb.mongo.Contact")
        testm.delete_contact(mockcontact)
        mockcontact.delete.assert_called_once_with()
    
    def test_Mongo_find_contacts(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        class testcontact():
            class ts():
                email="mail@is.com"
            slack=ts()
            email="mailer"
            class tt():
                username="tgrammer"
            telegram= tt()
            name= ""
            surname= ""
        mockproject=mocker.patch("mongodb.mongo.Contact")
        badtest = testcontact()
        badtest.name="test"
        mockproject.objects.return_value=[testcontact(), badtest]
        assert testm.find_contacts("test") == [badtest]
    
    
    def test_Mongo_list_contacts(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        testm.list_contacts()
        mockcontact.objects.assert_called_once_with()
    
    def test_Mongo_insert_project(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockproject=mocker.patch("mongodb.mongo.Project")
        testm.insert_project("name", "url")
        mockproject.assert_called_once_with(name="name", url="url")
        mockproject.return_value.save.assert_called_once_with()
    
    def test_Mongo_update_project(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockproject=mocker.patch("mongodb.mongo.Project")
        testm.update_project("oldurl", "name", "url")
    
    def test_Mongo_find_project_by_url(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockproject= mocker.patch("mongodb.mongo.Project")
        mockproject.objects.return_value=["x", "y"]
        assert testm.find_project_by_url("test.com")== "x"
    
    def test_Mongo_delete_project(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockproject= mocker.patch("mongodb.mongo.Project")
        mockf= mocker.patch("mongodb.mongo.Mongo.find_project_by_url")
        testm.delete_contact(mockproject)
        mockproject.delete.assert_called_once_with()
    
    def test_Mongo_find_projects(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        class ptest():
            name="none"
            url="none"
        mockproject=mocker.patch("mongodb.mongo.Project")
        badtest = ptest()
        badtest.name="test"
        mockproject.objects.return_value=[ptest(), badtest]
        assert testm.find_projects("test") == [badtest]
    
    def test_Mongo_list_projects(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockproject=mocker.patch("mongodb.mongo.Project")
        testm.list_projects()
        mockproject.objects.assert_called_once_with()
          
    def test_Mongo_insert_subscription(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockproject=mocker.patch("mongodb.mongo.Project")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mocksubscription=mocker.patch("mongodb.mongo.Subscription")
        mockproject.objects.return_value=["project"]
        mockcontact.objects.return_value=["contact"]
        testm.insert_subscription("mail", "url", "prior", "keyw")
        mockproject.objects.assert_called_once_with(url="url")
        mockcontact.objects.assert_called_once_with(email="mail")
        mocksubscription.assert_called_once_with(contact="contact", project="project", priority="prior", keywords="keyw")
        mocksubscription.return_value.save.assert_called_once_with()
        
    
    def test_Mongo_insert_subscription_exception(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockproject=mocker.patch("mongodb.mongo.Project")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mocksubscription=mocker.patch("mongodb.mongo.Subscription")
        mockproject.objects.return_value=["project"]
        mockcontact.objects.return_value=[]
        with pytest.raises(Exception):
            testm.insert_subscription("mail", "url", "prior", "keyw")

    
    def test_Mongo_update_subscription(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        class st():
            contact="x"
            project="x"
            priority="x"
            keywords="x"
        mocksubscription=mocker.patch("mongodb.mongo.Mongo.find_subscription_by_email_url")
        mockcontact=mocker.patch("mongodb.mongo.Mongo.find_contact_by_email")
        mockproject=mocker.patch("mongodb.mongo.Mongo.find_project_by_url")
        mockproject.return_value="project"
        mockcontact.return_value="contact"
        testm.update_subscription("oldmaile", "oldurl","mail", "url", "prior", "keyw")
        mocksubscription.assert_called_once_with("oldmaile", "oldurl")
        mocksubscription.return_value.save.assert_called_once_with()
        
    
    def test_Mongo_delete_subscription(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mocksubscription= mocker.patch("mongodb.mongo.Subscription")
        testm.delete_contact(mocksubscription)
        mocksubscription.delete.assert_called_once_with()
    
    def test_Mongo_find_subscription_by_email_url(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockproject= mocker.patch("mongodb.mongo.Project")
        mockcontact= mocker.patch("mongodb.mongo.Contact")
        mocksubscription= mocker.patch("mongodb.mongo.Subscription")
        mockproject.objects.return_value=["pro"]
        mockcontact.objects.return_value=["con", "tact"]
        mocksubscription.objects.return_value=["yes"]
        assert "yes" == testm.find_subscription_by_email_url("email", "url")
        mocksubscription.objects.assert_called_once_with(contact="con", project="pro")
    
    def test_Mongo_find_subscriptions(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        class testcontact():
            class ts():
                email="mail@is.com"
            slack=ts()
            email="mailer"
            class tt():
                username="tgrammer"
            telegram= tt()
            name= "na"
            surname= "a"
        class ptest():
            name="none"
            url="none"
        class stest():
            contact=testcontact()
            project=ptest()
        mocksubscription=mocker.patch("mongodb.mongo.Subscription")
        badtest = stest()
        badtest.contact.name="test"
        mocksubscription.objects.return_value=[badtest]
        assert testm.find_subscriptions("test") == [badtest]
    
    def test_Mongo_list_subscriptions(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mocksubscription=mocker.patch("mongodb.mongo.Subscription")
        testm.list_subscriptions()
        mocksubscription.objects.assert_called_once_with()
    
    def test_Mongo_update_telegram_id(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mc=mockcontact.return_value
        mockcontact.objects.return_value=[mc]
        testm.update_telegram_id("username", 13)
        assert mc.telegram.id == 13
        mc.save.assert_called_once_with()
    
    def test_Mongo_update_telegram_id_exception(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mc=mockcontact.return_value
        mockcontact.objects.return_value=[]
        with pytest.raises(Exception):
            testm.update_telegram_id("username", 13)
    
    def test_Mongo_update_slack_id(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mc=mockcontact.return_value
        mockcontact.objects.return_value=[mc]
        testm.update_slack_id("email", 24)
        assert mc.slack.id == 24
        mc.save.assert_called_once_with()
    
    def test_Mongo_update_slack_id_exception(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mc=mockcontact.return_value
        mockcontact.objects.return_value=[]
        with pytest.raises(Exception):
            testm.update_slack_id("email", 24)

        
    def test_Mongo_get_interested_recipients(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockf=mocker.patch("mongodb.mongo.Mongo.find_project_by_url")
        mockf2=mocker.patch("mongodb.mongo.Mongo.add_recipients_to_dict")
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mocksubscription=mocker.patch("mongodb.mongo.Subscription")
        mockd=mocker.patch("mongodb.mongo.date")
        mockd.today.return_value=0
        class testcontact():
            class holy():
                begin_1=2
                begin_2=20
                begin_3=12
                end_1=5
                end_2=25
                end_3=17
            holidays= holy()
            class ts():
                email="mail@is.com"
            slack=ts()
            email="mailer"
            class tt():
                username="tgrammer"
            telegram= tt()
            name= "na"
            surname= "a"
        class stest():
            contact=testcontact()
            keywords=[]
            priority=1
        mocksubscription.objects.return_value=[stest(),stest()]
        assert testm.get_interested_recipients({"project_url":"url", "description":"something"}) == {"telegram":[], "email":[], "slack":[]}
        
        
    def test_Mongo_get_interested_recipients_empty(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        mockf=mocker.patch("mongodb.mongo.Mongo.find_project_by_url")
        mocksubscription=mocker.patch("mongodb.mongo.Subscription")
        mocksubscription.objects.return_value= None
        assert testm.get_interested_recipients({"project_url":"url", "description":"something"}) == None
    
    def test_Mongo_add_recipients_to_dict(self,mocker):
        mockconnect=mocker.patch("mongodb.mongo.connect")
        testm=mongodb.mongo.Mongo("a", "b", "c")
        class TestRecipients():
            class tp():
                use_telegram=True
                use_email=True
                use_slack=True
            preferences=tp()
            email="mailer"
            class tt():
                id="tgrammer"
            telegram= tt()
            class ts():
                id="slacker"
            slack= ts()
        mockcontact=mocker.patch("mongodb.mongo.Contact")
        mockcontact.objects.return_value=[TestRecipients()]
        rec={"telegram":["tuser"],"email":["euser"],"slack":["suser"]}
        testm.add_recipients_to_dict(rec, "mail")
        assert rec == {"telegram":["tuser", "tgrammer"],"email":["euser", "mailer"],"slack":["suser", "slacker"]}
        
    
