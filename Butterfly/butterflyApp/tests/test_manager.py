import pytest
import manager.manager

class TestPersonalManager(object):
    def test_create_PersonalManager(self, mocker):
        mockMongo=mocker.patch("manager.manager.Mongo")
        mockProducer=mocker.patch("manager.manager.Producer")
        test=manager.manager.PersonalManager(mockMongo, mockProducer)
        assert test._producer == mockProducer
        assert test._mongo == mockMongo
        
    def test_PersonalManager_process(self, mocker):
        mockMongo=mocker.patch("manager.manager.Mongo")
        mockProducer=mocker.patch("manager.manager.Producer")
        mockfunc=mocker.patch("manager.manager.PersonalManager._add_preferences")
        mockMongo.get_interested_recipients.return_value= "egg"
        test=manager.manager.PersonalManager(mockMongo, mockProducer)
        data={"project_url":"tester"}
        test.process(data)
        mockProducer.produce.assert_called_once_with(data)
        mockfunc.assert_called_once_with(data, "egg")
        
    def test_PersonalManager_stop(self, mocker):
        mockMongo=mocker.patch("manager.manager.Mongo")
        mockProducer=mocker.patch("manager.manager.Producer")
        test=manager.manager.PersonalManager(mockMongo, mockProducer)
        test.stop()
        mockProducer.close.assert_called_once_with()

    def test_PersonalManager__add_preferences(self, mocker):
        mockMongo=mocker.patch("manager.manager.Mongo")
        mockProducer=mocker.patch("manager.manager.Producer")
        test=manager.manager.PersonalManager(mockMongo, mockProducer)
        testdict= {"test":"1"}
        test._add_preferences(testdict, {"user":"spam"})
        assert testdict == {"test":"1", "recipients":{"user":"spam"}}

class TestDispatcherProducer(object):
    
    def test_create_DispatcherProducer(self, mocker):
        mockproducer= mocker.patch("manager.manager.Producer")
        mockkafkaproducer= mocker.patch("manager.manager.KafkaProducer")
        dipro = manager.manager.DispatcherProducer(mockproducer)
        assert True
    
    def test_DispatcherProducer_produce(self, mocker):
        mockproducer= mocker.patch("manager.manager.Producer")
        mockkafkaproducer= mocker.patch("manager.manager.KafkaProducer")
        mockextract=mocker.patch("manager.manager.DispatcherProducer.extract_topic_list")
        mocksend=mocker.patch("manager.manager.DispatcherProducer.send")
        mockextract.return_value={"user":"spam"}
        dipro = manager.manager.DispatcherProducer(mockproducer)  
        dipro.produce({"recipients":{"user":"spam"}})
        mockextract.assert_called_once_with({})
        mocksend.assert_called_once_with("user", {})
        
    
    def test_DispatcherProducer_extract_topic_list(self, mocker):
        mockproducer= mocker.patch("manager.manager.Producer")
        mockkafkaproducer= mocker.patch("manager.manager.KafkaProducer")
        dipro = manager.manager.DispatcherProducer(mockproducer)
        testd={"msg":"egg", "recipients":"spam"}
        assert "spam" == dipro.extract_topic_list(testd)
        assert testd == {"msg":"egg"}
    
    
        
class TestDispatcherConsumer(object):
    
    def test_create_DispatcherConsumer(self, mocker):
        mockconsumer= mocker.patch("manager.manager.Consumer")
        mockkafkaconsumer= mocker.patch("manager.manager.KafkaConsumer")
        mockprocessor= mocker.patch("manager.manager.Processor")
        dicon = manager.manager.DispatcherConsumer(mockkafkaconsumer,mockprocessor)
        assert dicon._processor == mockprocessor
    
    def test_DispatcherConsumer_consume(self, mocker):
        mockconsumer= mocker.patch("manager.manager.Consumer")
        mockkafkaconsumer= mocker.patch("manager.manager.KafkaConsumer")
        mockprocessor= mocker.patch("manager.manager.Processor")
        dicon = manager.manager.DispatcherConsumer(mockkafkaconsumer,mockprocessor)  
    
    def test_DispatcherConsumer_close(self, mocker):
        mockconsumer= mocker.patch("manager.manager.Consumer")
        mockkafkaconsumer= mocker.patch("manager.manager.KafkaConsumer")
        mockprocessor= mocker.patch("manager.manager.Processor")
        dicon = manager.manager.DispatcherConsumer(mockkafkaconsumer,mockprocessor) 
        dicon.consume({})
        mockprocessor.process.assert_called_once_with({})
    
def test_create_dispatcher_producer(mocker):
    mockkafkaproducer= mocker.patch("manager.manager.KafkaProducerFactory")
    mockdispatcherproducer= mocker.patch("manager.manager.DispatcherProducer")
    mockkafkaproducer.create.return_value = "spam"
    manager.manager.create_dispatcher_producer({"kafka_producer":"egg"})
    mockdispatcherproducer.assert_called_once_with("spam")
    
        
def test_create_dispatcher_producer_exception(mocker):
    mockkafkaproducer= mocker.patch("manager.manager.KafkaProducerFactory")
    mockdispatcherproducer= mocker.patch("manager.manager.DispatcherProducer")
    mockkafkaproducer.create.side_effect = Exception
    with pytest.raises(SystemExit) as keyerror:
        manager.manager.create_dispatcher_producer({"kafka_producer":"egg"})
        assert keyerror.type == SystemExit
        assert keyerror.value.code == 42

def test_create_personal_manager(mocker):
    mockmongo= mocker.patch("manager.manager.Mongo")
    mockerpersonalmanager= mocker.patch("manager.manager.PersonalManager")
    mocker.patch("manager.manager.create_dispatcher_producer")
    mongo = manager.manager.create_personal_manager({"mongo":{"db_name":"db", "host":"h", "port":"p"}})
    mockerpersonalmanager.return_value="x"
    mockmongo.assert_called_once_with("db", "h", "p")
        
def test_create_dispatcher_consumer(mocker):
    mockkafkaconsumer= mocker.patch("manager.manager.KafkaConsumerFactory")
    mockdispatcherconsumer= mocker.patch("manager.manager.DispatcherConsumer")
    mockcreatepenmanager= mocker.patch("manager.manager.create_personal_manager")
    mockcreatepenmanager.return_value="x"
    mockkafkaconsumer.create.return_value = "spam"
    manager.manager.create_dispatcher_consumer({"kafka_consumer":"spam","kafka_topics":{"topic_producer_name_list":{"egg":"2"}}})
    mockdispatcherconsumer.assert_called_once_with("spam", mockcreatepenmanager.return_value)
        
def test_create_dispatcher_consumer_exception(mocker):
    mockkafkaconsumer= mocker.patch("manager.manager.KafkaConsumerFactory")
    mockdispatcherconsumer= mocker.patch("manager.manager.DispatcherConsumer")
    mockcreatepenmanager= mocker.patch("manager.manager.create_personal_manager")
    mockkafkaconsumer.create.return_value = "spam"
    mockkafkaconsumer.create.side_effect = Exception
    with pytest.raises(SystemExit) as keyerror:
        manager.manager.create_dispatcher_consumer({})
        assert keyerror.type == SystemExit
        assert keyerror.value.code == 42

def test_start_manager(mocker):
    mockDisCon=mocker.patch("manager.manager.DispatcherConsumer")
    mockf=mocker.patch("manager.manager.create_dispatcher_consumer")
    mockf.return_value=mockDisCon
    manager.manager.start_manager({"spam":"egg"})
    mockf.assert_called_once_with({"spam":"egg"})
    mockDisCon.start.assert_called_once_with()
    mockDisCon.close.assert_called_once_with()
        
def test_start_manager_exception(mocker):
    mockDisCon=mocker.patch("manager.manager.DispatcherConsumer")
    mockf=mocker.patch("manager.manager.create_dispatcher_consumer")
    mockf.return_value=mockDisCon
    mockDisCon.start.side_effect = KeyboardInterrupt
    with pytest.raises(SystemExit) as keyerror:
        manager.manager.start_manager({"spam":"egg"})
        assert keyerror.type == SystemExit
        assert keyerror.value.code == 42
        
