import os
import pytest

from appium import webdriver
from helpers import take_screenhot_and_logcat

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)
APPIUM_LOCAL_HOST_URL = 'http://localhost:4723/wd/hub'


class TestSimpleAndroid():
    @pytest.fixture(scope="function")
    def driver(self, request, device_logger):
        desired_caps = {
            'platformName': 'Android',
            'platformVersion': '8.1.0',
            'deviceName': 'QHAP8YNK8Q',
            'automationName': 'UiAutomator2',
            'unicodeKeyboard': True,
            'autoGrantPermissions': True,
            'appPackage': 'com.thoughtworks.hmipatent',
            'fullReset': True,
            'app': PATH('/Users/shuaiz/Downloads/hmipatent-debug.apk'),
            'appWaitActivity': '*'
        }
        calling_request = request._pyfuncitem.name
        driver = webdriver.Remote(APPIUM_LOCAL_HOST_URL, desired_caps)

        def fin():
            take_screenhot_and_logcat(driver, device_logger, calling_request)
            # driver.quit()

        request.addfinalizer(fin)
        return driver  # provide the fixture value

    @pytest.mark.run(order=1)
    def test_open_main_page(self, driver):
        driver.find_element_by_xpath('//android.widget.Button[contains(@text, "允许")]').click()