import os
import pytest
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from helpers import take_screenhot_and_logcat

from conf.appium_config import appium_start

def find_element_xy_in_container(x, y, width, height, index, size):
    locationX = x + (width / size) * index + 1
    locationY = y + (height / size) * index + 1
    return dict(x = locationX, y = locationY)

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
        driver.find_element_by_android_uiautomator('new UiSelector().text("允许")').click()
        # driver.find_element_by_xpath('//android.widget.Button[contains(@text, "允许")]').click()
        swithcField = driver.find_elements_by_android_uiautomator("new UiSelector().clickable(true)")
        swithcField[0].click()
        driver.find_element_by_android_uiautomator('new UiSelector().text("允许")').click()
        driver.back()

        driverAppField = driver.find_element_by_android_uiautomator('new UiSelector().text("行车应用")')
        assert driverAppField is not None
        residentAppField = driver.find_element_by_android_uiautomator('new UiSelector().text("驻车应用")')
        assert residentAppField is not None

        windowLabelField = driver.find_element_by_android_uiautomator('new UiSelector().text("车窗")')
        assert windowLabelField is not None
        windowContainer = driver.find_element_by_id("com.thoughtworks.hmipatent:id/main_widget_window_view")
        touch = TouchAction(driver)
        halfOpenLocation = find_element_xy_in_container(windowContainer.location['x'], windowContainer.location['y'], windowContainer.size['width'], windowContainer.size['height'], 1, 4)
        allOpenLocation = find_element_xy_in_container(windowContainer.location['x'], windowContainer.location['y'], windowContainer.size['width'], windowContainer.size['height'], 3, 4)
        
        touch.tap(None, halfOpenLocation['x'], halfOpenLocation['y'], 1).perform()
        touch.tap(None, allOpenLocation['x'], allOpenLocation['y'], 1).perform()