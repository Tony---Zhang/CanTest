import os
import pytest
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from helpers import take_screenhot_and_logcat

from conf.appium_config import appium_start

def find_element_xy_in_container(x, y, width, height, index, size):
    location_x = x + (width / size) * index + 1
    location_y = y + (height / size) * index + 1
    return dict(x = location_x, y = location_y)

class TestSimpleAndroid():
    @pytest.fixture(scope="function")
    def driver(self, request, device_logger):
        driver = appium_start('com.thoughtworks.hmipatent', '/Users/shuaiz/Downloads/hmipatent-debug.apk',  False)
        calling_request = request._pyfuncitem.name

        def fin():
            take_screenhot_and_logcat(driver, device_logger, calling_request)
            # driver.quit()

        request.addfinalizer(fin)
        return driver  # provide the fixture value

    @pytest.mark.run(order=1)
    def test_open_main_page(self, driver):
        self.enable_can_usb(driver)
        self.enable_media_control(driver)
        driver_app_field = driver.find_element_by_android_uiautomator('new UiSelector().text("行车应用")')
        assert driver_app_field is not None
        resident_app_field = driver.find_element_by_android_uiautomator('new UiSelector().text("驻车应用")')
        assert resident_app_field is not None
        
    def test_open_window(self, driver):
        window_label = driver.find_element_by_android_uiautomator('new UiSelector().text("车窗")')
        assert window_label is not None
        window_container = driver.find_element_by_id("com.thoughtworks.hmipatent:id/main_widget_window_view")
        touch = TouchAction(driver)
        half_open_location = find_element_xy_in_container(window_container.location['x'], window_container.location['y'], window_container.size['width'], window_container.size['height'], 1, 4)
        all_open_location = find_element_xy_in_container(window_container.location['x'], window_container.location['y'], window_container.size['width'], window_container.size['height'], 3, 4)
        
        touch.tap(None, half_open_location['x'], half_open_location['y'], 1).perform()
        touch.tap(None, all_open_location['x'], all_open_location['y'], 1).perform()

    def enable_can_usb(self, driver):
        message = driver.find_element_by_id("android:id/message")
        assert message.text == '允许应用“HMI Demo”访问该USB设备吗？'
        button = driver.find_element_by_id("android:id/button1")
        button.click()

    def enable_media_control(self, driver):
        driver.find_element_by_android_uiautomator('new UiSelector().text("允许")').click()
        switch_field = driver.find_elements_by_android_uiautomator("new UiSelector().clickable(true)")
        switch_field[0].click()
        driver.find_element_by_android_uiautomator('new UiSelector().text("允许")').click()
        driver.back()