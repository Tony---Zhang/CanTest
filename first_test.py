import os
import pytest
from appium import webdriver
from helpers import take_screenhot_and_logcat

from conf.appium_config import appium_start


class TestSimpleAndroid():
    @pytest.fixture(scope="function")
    def driver(self, request, device_logger):
        driver = appium_start('com.thoughtworks.hmipatent', '/Users/shuaiz/Downloads/hmipatent-debug.apk')
        calling_request = request._pyfuncitem.name

        def fin():
            take_screenhot_and_logcat(driver, device_logger, calling_request)
            # driver.quit()

        request.addfinalizer(fin)
        return driver  # provide the fixture value

    @pytest.mark.run(order=1)
    def test_open_main_page(self, driver):
        driver.find_element_by_xpath('//android.widget.Button[contains(@text, "允许")]').click()
