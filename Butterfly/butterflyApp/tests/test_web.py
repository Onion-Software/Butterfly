import pytest
import importlib

weblib= importlib.import_module("web-app.app")


class TestApplication(object):
    def test_create_Application(self,mocker):
        mockflask=mocker.patch("web-app.app.Flask")
        mockmongo=mocker.patch("web-app.app.Mongo")
        mockf=mocker.patch("web-app.app.Application._add_api_routes")
        mockf2=mocker.patch("web-app.app.Application._add_website_routes")
        test = weblib.Application(mockflask, mockmongo)
        assert test._app == mockflask
        assert test._mongo == mockmongo
        mockf.assert_called_once_with()
        mockf2.assert_called_once_with()
        
        
    def test_Application__shutdown_app_exception(self,mocker):
        mockflask=mocker.patch("web-app.app.Flask")
        mockmongo=mocker.patch("web-app.app.Mongo")
        mockf=mocker.patch("web-app.app.Application._add_api_routes")
        mockf2=mocker.patch("web-app.app.Application._add_website_routes")
        test = weblib.Application(mockflask, mockmongo)
        mockf3= mocker.patch("web-app.app.request")
        mockf3.environ.get. return_value = None
        with pytest.raises(Exception):
            test._shutdown_app()
            
    def test_routes(self,mocker):
        mockflask=mocker.patch("web-app.app.Flask")
        mockmongo=mocker.patch("web-app.app.Mongo")
        mockf=mocker.patch("web-app.app.Application._add_api_routes")
        mockf2=mocker.patch("web-app.app.Application._add_website_routes")
        test = weblib.Application(mockflask, mockmongo)
        test._add_api_routes()
        test._add_website_routes()
        assert True

    
