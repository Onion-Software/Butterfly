import main

class TestMain(object):
    def test_see_topics(self, mocker):
        x=mocker.patch("main.KafkaConsumerFactory")
        config={"kafka_consumer":"x"}
        main.see_topics(config)
        x.create.assert_called_once_with( "x", "abc")
    
    def test_create_kafka_topic(self, mocker):
        x=mocker.patch("main.KafkaAdminClient")
        y=mocker.patch("main.NewTopic")
        main.create_kafka_topic({"kafka_producer":{"bootstrap_servers":""},"kafka_topics":{"topic_producer_name_list":["x", "y"],"topic_consumer_name_list":["x", "y"]}})
        assert True