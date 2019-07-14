import producers.producer
import importlib
redminelib=importlib.import_module("producers.redmine-producer.redmine")
gitlablib=importlib.import_module("producers.gitlab-producer.gitlab")
import pytest
from werkzeug.exceptions import HTTPException

class TestProducer(object):

    #test su class KafkaProducerFactory
    def test_create_KafkaProducerFactory(self,mocker):
        mockProduce = mocker.patch("producers.producer.KafkaProducer");
        mockProduce.return_value = True
        assert producers.producer.KafkaProducerFactory.create({}) == True


    def test_KafkaProducerFactory_noBroker_error(self,mocker):
        mockkafka = mocker.patch('producers.producer.KafkaProducer')
        mockkafka.side_effect =producers.producer.errors.NoBrokersAvailable
        with pytest.raises(Exception):
            producers.producer.KafkaProducerFactory.create({})

    def test_KafkaProducerFactory_KeyboardInterrupt_error(self,mocker):
        mockkafka = mocker.patch('producers.producer.KafkaProducer')
        mockkafka.side_effect = KeyboardInterrupt
        with pytest.raises(SystemExit) as keyerror:
            producers.producer.KafkaProducerFactory.create({})
            assert keyerror.type == SystemExit
            assert keyerror.value.code == 42


    class TestProduce(producers.producer.Producer):
        def produce(self, data: dict):
            pass    
    
    def test_create_Producer(self,mocker):
        mockkafka = mocker.patch('producers.producer.KafkaProducer')
        test= TestProducer.TestProduce(mockkafka)
        assert mockkafka == test._producer
        
    def test_Producer_send(self,mocker):
        mockkafka = mocker.patch('producers.producer.KafkaProducer')
        test= TestProducer.TestProduce(mockkafka)
        test.send("spam", {"lunch":"egg"})
        mockkafka.send.assert_called_once_with("spam", {"lunch":"egg"})  
        
    def test_Producer_close(self,mocker):
        mockkafka = mocker.patch('producers.producer.KafkaProducer')
        test= TestProducer.TestProduce(mockkafka)
        test.close()
        mockkafka.close.assert_called_once_with()                
        

    #Class FlaskServer TEST
    def test_create_FlaskServer(self,mocker):
        mockflask=mocker.patch('producers.producer.Flask')
        mockproducer =mocker.patch('producers.producer.Producer')
        test=producers.producer.FlaskServer(mockflask,mockproducer)
        assert test._app==mockflask
        assert test._producer==mockproducer

    def test_FlaskServer_start(self,mocker):
        mockflask=mocker.patch('producers.producer.Flask')
        mockproducer =mocker.patch('producers.producer.Producer')
        test=producers.producer.FlaskServer(mockflask,mockproducer)
        test.start("spam",23)
        mockflask.run.assert_called_once_with(host="spam",port=23)

    def test_FlaskServer__shutdown_app(self,mocker):
        mockflask=mocker.patch('producers.producer.Flask')
        mockproducer =mocker.patch('producers.producer.Producer')
        mockf= mocker.patch('producers.producer.request')
        test=producers.producer.FlaskServer(mockflask,mockproducer)
        def emptyf():
            x= 2 + 3
        mockf.environ.get.return_value= emptyf
        test._shutdown_app()
        mockf.environ.get.assert_called_once_with('werkzeug.server.shutdown')

    def test_FlaskServer__shutdown_app_exception(self,mocker):
        mockflask=mocker.patch('producers.producer.Flask')
        mockproducer =mocker.patch('producers.producer.Producer')
        mockf= mocker.patch('producers.producer.request')
        test=producers.producer.FlaskServer(mockflask,mockproducer)
        mockf.environ.get.return_value= None
        with pytest.raises(Exception):
            test._shutdown_app()
        

    def test_FlaskServer_close(self,mocker):
        mockflask=mocker.patch('producers.producer.Flask')
        mockf=mocker.patch('producers.producer.FlaskServer._shutdown_app')
        mockproducer =mocker.patch('producers.producer.Producer')
        test=producers.producer.FlaskServer(mockflask,mockproducer)
        test.close()
        mockf.assert_called_once_with()
        mockproducer.close.assert_called_once_with()
        

class TestGitLabProducer(object):

    def test_create_GitLabProducer(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        assert test._producer== mockkafka

    def test_GitLabProducer_produce(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        mockf = mocker.patch('producers.gitlab-producer.gitlab.GitLabProducer.send')
        mockf2 = mocker.patch('producers.gitlab-producer.gitlab.GitLabProducer._parse')
        mockf2.return_value = "x"
        test=gitlablib.GitLabProducer(mockkafka, "server")
        test.produce({"spam":"egg"})
        mockf.assert_called_once_with("gitlab", "x")

    def test_GitLabProducer__parse_newissue(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        mockf = mocker.patch('producers.gitlab-producer.gitlab.GitLabProducer._find_new_issue_keys')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        json= {"object_kind":"issue","project":{"name":"json","web_url":"url.com", "path_with_namespace":"qqq"},"object_attributes":{"last_edited_at":None}}
        test._parse(json)
        mockf.assert_called_once_with(json, {"app": "GitLab", "object_kind": "issue", "project_name": "json", "project_url": "http://server/qqq"})
        
    def test_GitLabProducer__parse_modifiedissue(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        mockf = mocker.patch('producers.gitlab-producer.gitlab.GitLabProducer._find_modified_issue_keys')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        json= {"object_kind":"issue","project":{"name":"json","web_url":"url.com", "path_with_namespace":"qqq"},"object_attributes":{"last_edited_at":"some date"}}
        test._parse(json)
        mockf.assert_called_once_with(json, {"app": "GitLab", "object_kind": "issue", "project_name": "json", "project_url": "http://server/qqq"})
    
    def test_GitLabProducer__parse_push(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        mockf = mocker.patch('producers.gitlab-producer.gitlab.GitLabProducer._find_push_keys')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        json= {"object_kind":"push","project":{"name":"json","web_url":"url.com", "path_with_namespace":"qqq"},"object_attributes":{"last_edited_at":None}}
        test._parse(json)
        mockf.assert_called_once_with(json, {"app": "GitLab", "object_kind": "push", "project_name": "json", "project_url": "http://server/qqq"})
    
    def test_GitLabProducer__parse_note(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        mockf = mocker.patch('producers.gitlab-producer.gitlab.GitLabProducer._find_note_keys')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        json= {"object_kind":"note","project":{"name":"json","web_url":"url.com", "path_with_namespace":"qqq"},"object_attributes":{"last_edited_at":None}}
        test._parse(json)
        mockf.assert_called_once_with(json, {"app": "GitLab", "object_kind": "note", "project_name": "json", "project_url": "http://server/qqq"})
    
    def test_GitLabProducer__parse_none(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        json= {"object_kind":"unknown","project":{"name":"json","web_url":"url.com", "path_with_namespace":"qqq"},"object_attributes":{"last_edited_at":None}}
        with pytest.raises(Exception):
            test._parse(json)

    def test_GitLabProducer__find_note_keys_commit(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        data={"commit":{"message":"committed"}, "issue":{"title":"non funziona", "url":"urll", "id":""}, "user":{"name":"Spam"}, "object_attributes": {"description":"a commit was made", "created_at":"somewhere"}} 
        nresult={"title":"committed", "author":"Spam", "description":"a commit was made", 'created_on': 'somewhere', 'project_url': '','issue_url': '/issues/'}
        assert nresult == test._find_note_keys(data, {"project_url":""})
        
    def test_GitLabProducer__find_note_keys_nocommit(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        data={"issue":{"title":"non funziona", "url":"urll", "url":"urll", "id":""}, "user":{"name":"Spam"}, "object_attributes": {"description":"errors awry", "created_at":"somewhere"}} 
        nresult={"title":"non funziona", "author":"Spam", "description":"errors awry", 'created_on': 'somewhere', 'issue_url': '/issues/', 'project_url': ''}
        assert nresult == test._find_note_keys(data,  {"project_url":""})
        
    def test_GitLabProducer__find_issue_keys(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        data={"user":{"name":"Spam"}, "object_attributes": {"title":"titolo", "description":"Qualcosa", "state":"finito", "created_at":"somewhere", "url":"urll", "id":""}} 
        nresult={"title":"titolo", "author":"Spam", "description":"Qualcosa",  'created_on': 'somewhere', 'issue_url': '/issues/', 'status': 'finito', 'project_url': ''}
        assert nresult == test._find_issue_keys(data,  {"project_url":""})

    def test_GitLabProducer__find_new_issue_keys(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        mockf=mocker.patch("producers.gitlab-producer.gitlab.GitLabProducer._find_issue_keys")
        test._find_new_issue_keys({},{"x":"y"})
        mockf.assert_called_once_with({}, {"x":"y"})

    def test_GitLabProducer__find_modified_issue_keys(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        mockf=mocker.patch("producers.gitlab-producer.gitlab.GitLabProducer._find_issue_keys")
        data={"object_attributes":{"last_edited_at":"somewhere", "last_edited_by_id":"someone"}} 
        nresult={"function":"called", "last_edited_at":"somewhere", "last_edited_by_id":"someone"}
        mockf.return_value= {"function":"called"}
        assert test._find_modified_issue_keys(data, {})
        mockf.assert_called_once_with(data, {})

    def test_GitLabProducer__find_push_keys(self,mocker):
        mockkafka = mocker.patch('producers.gitlab-producer.gitlab.KafkaProducer')
        test=gitlablib.GitLabProducer(mockkafka, "server")
        data={"commits":{0:{"id":"","message":"committion","timestamp":"yesterday","url":"url","author":{"name":"Nome", "email":"em"}}},"user_name":""} 
        nresult={"description":"committion", 'author': '', 'created_on': 'yesterday', "commits_url":'/commit/', "commits_author_name":"Nome", "commits_author_email":"em", 'project_url': ''}
        assert nresult == test._find_push_keys(data, {'project_url':""})


    def test_start_gitlab_producer(self,mocker):
        mockkafkapf=mocker.patch("producers.gitlab-producer.gitlab.KafkaProducerFactory")
        mockflask=mocker.patch("producers.gitlab-producer.gitlab.Flask")
        mockflasks=mocker.patch("producers.gitlab-producer.gitlab.FlaskServer")
        mockglp=mocker.patch("producers.gitlab-producer.gitlab.GitLabProducer")
        mockkafkapf.create.return_value="kafka"
        mockglp.return_value= "x"
        mockflask.return_value= "flask"
        gitlablib.start_gitlab_producer({"kafka_producer":"kf","gitlab":{"app_name":"ap", "ip":"ip", "port":22, "server": ""}})
        mockkafkapf.create.assert_called_once_with("kf")
        mockflask.assert_called_once_with("ap")
        mockglp.assert_called_once_with("kafka", "")
        mockflasks.assert_called_once_with("flask","x")
        mockflasks.return_value.start.assert_called_once_with("ip", 22)
        mockflasks.return_value.close.assert_called_once_with()
        
        
    def test_start_gitlab_producer_exception(self,mocker):
        mockkafkapf=mocker.patch("producers.gitlab-producer.gitlab.KafkaProducerFactory")
        mockkafkapf.create.side_effect = Exception
        with pytest.raises(SystemExit) as keyerror:
            gitlablib.start_gitlab_producer({"kafka_producer":"kf","gitlab":{"app_name":"ap", "ip":"ip", "port":22}})
            assert keyerror.type == SystemExit
            assert keyerror.value.code == 42

    def test_start_gitlab_producer_keyboardinterrupt(self,mocker):
        mockkafkapf=mocker.patch("producers.gitlab-producer.gitlab.KafkaProducerFactory")
        mockflask=mocker.patch("producers.gitlab-producer.gitlab.Flask")
        mockflasks=mocker.patch("producers.gitlab-producer.gitlab.FlaskServer")
        mockglp=mocker.patch("producers.gitlab-producer.gitlab.GitLabProducer")
        mockkafkapf.create.return_value="kafka"
        mockglp.return_value= "x"
        mockflask.return_value= "flask"
        gitlablib.start_gitlab_producer({"kafka_producer":"kf","gitlab":{"app_name":"ap", "ip":"ip", "port":22, "server":""}})
        mockflasks.return_value.start.side_effect= KeyboardInterrupt
        with pytest.raises(SystemExit) as keyerror:
            gitlablib.start_gitlab_producer({"kafka_producer":"kf","gitlab":{"app_name":"ap", "ip":"ip", "port":22, "server":""}})
            assert keyerror.type == SystemExit
            assert keyerror.value.code == 42




class TestRedmine(object):

    def test_create_RedmineProducer(self,mocker):
        mockkafka = mocker.patch('producers.redmine-producer.redmine.KafkaProducer')
        test=redminelib.RedmineProducer(mockkafka, "server")
        assert test._producer== mockkafka


    def test_RedmineProducer_produce(self,mocker):
        mockkafka = mocker.patch('producers.redmine-producer.redmine.KafkaProducer')
        mockf = mocker.patch('producers.redmine-producer.redmine.RedmineProducer.send')
        mockf2 = mocker.patch('producers.redmine-producer.redmine.RedmineProducer._parse')
        mockf2.return_value = "x"
        test=redminelib.RedmineProducer(mockkafka, "server")
        test.produce({"spam":"egg"})
        mockf.assert_called_once_with("redmine", "x")

    def test_RedmineProducer__parse(self,mocker):
        mockkafka = mocker.patch('producers.redmine-producer.redmine.KafkaProducer')
        test=redminelib.RedmineProducer(mockkafka, "server")
        test._parse({"author":{"login":""}, "project":{"name":"", "identifier":"idi"},"priority":{"name":"n"},"updated_on":"2", "created_on":"1","subject":"", "prioritychanged":"","description":"", "status_id":{"name":""}})

    def test_start_redmine_producer(self,mocker):
        mockkafkapf=mocker.patch("producers.redmine-producer.redmine.KafkaProducerFactory")
        mockflask=mocker.patch("producers.redmine-producer.redmine.Flask")
        mockflasks=mocker.patch("producers.redmine-producer.redmine.FlaskServer")
        mockglp=mocker.patch("producers.redmine-producer.redmine.RedmineProducer")
        mockkafkapf.create.return_value="kafka"
        mockglp.return_value= "x"
        mockflask.return_value= "flask"
        redminelib.start_redmine_producer({"kafka_producer":"kf","redmine":{"app_name":"ap", "ip":"ip", "port":22, "server": ""}})
        mockkafkapf.create.assert_called_once_with("kf")
        mockflask.assert_called_once_with("ap")
        mockglp.assert_called_once_with("kafka", "")
        mockflasks.assert_called_once_with("flask","x")
        mockflasks.return_value.start.assert_called_once_with("ip", 22)
        mockflasks.return_value.close.assert_called_once_with()
        


    
if __name__ == '__main__':
    main()
        
        
