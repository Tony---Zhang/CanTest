import os
import pytest
import threading
from time import sleep
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from helpers import take_screenhot_and_logcat
from can.can_adapter import CanAdapter
from can.check_frame import CheckFrame

from conf.appium_config import appium_start

receive_data = []

"""
DeviceIndex:
Ginkgo product (for I2C,SPI, CAN adapters, and Sniffers, etc) supply the way one PC could connect multiple products and 
working simultaneously, the DeviceIndex is used to identify and distinguish those adapters. 
For example, one PC connected two CAN Interface (adapters), then DeviceIndex = 0 is used to specify first one, and 
DeviceIndex = 1 is used to specify the second one. This python program is used to test one CAN interface (or adapter), so 
it's fixed to 0, if have multiple adapters connected to one PC, then please modify this parameter for different devices
"""
DeviceIndex = 0
"""
CANIndex:
In one CAN Interface (or adapter), printed on form factor (the shell on top), it has two CAN channels, CAN1 and CAN2, 
in Extend (recommanded, or classic) CAN software, it could be selected by "CAN1" (Equal: CANIndex = 0)
or "CAN2"(Equal: CANIndex = 1), 
So when CANIndex = 0 here, means CAN1 has been chosen
"""
CANIndex = 0


class ReadThread(threading.Thread):
    def __init__(self, timeout):
        threading.Thread.__init__(self)
        self._timeout = timeout
        self.can_adapter = CanAdapter(
            can_index=CANIndex, device_index=DeviceIndex)

    def stop(self):
        self.can_adapter.interrupt()

    def run(self):
        self.can_adapter.run(receive_data, self._timeout)


class CheckThread(threading.Thread):
    def __init__(self, timeout, check_data):
        threading.Thread.__init__(self)
        self._timeout = timeout
        self._check_data = check_data

    def check_result(self, can_frame):
        for i in range(0, len(self._check_data)):
            check = self._check_data[i]
            if check.is_equal_to(can_frame):
                print('Find check can frame')
                print("Checking.RemoteFlag = %s" % can_frame.control)
                print("Checking.ExternFlag = %s" % can_frame.extented)
                print("Checking.ID = %s" % can_frame.id)
                print("Checking.DataLen = %d" % can_frame.data_length)
                print("Checking.Data: %s" % can_frame.data)
                print("Checking.TimeStamp = %d" % can_frame.timestamp)
                self._check_data.remove(check)
                return True
        print('Not match can frame, skip')
        return False

    def run(self):
        time_acc = 0
        while time_acc < self._timeout:
            if len(self._check_data) == 0:
                print('Test case passed')
                time_acc = self._timeout
            # Delay
            while len(receive_data) > 0:
                check = receive_data.pop()
                self.check_result(check)
            time_acc = time_acc + 0.1
            sleep(0.1)
        assert len(self._check_data) == 0


def find_element_xy_in_container(x, y, width, height, index, size):
    location_x = x + (width / size) * index + 1
    location_y = y + (height / size) * index + 1
    return dict(x=location_x, y=location_y)


class TestSimpleAndroid():
    @property
    def package(self):
        return 'com.thoughtworks.hmipatent'

    @pytest.fixture(scope="function")
    def driver(self, request, device_logger):
        driver = appium_start(
            self.package,
            '/Users/shuaiz/Downloads/hmipatent-debug.apk',
            False,
            {"appWaitPackage": "com.android.systemui", "appWaitActivity": "*"}
        )
        driver.implicitly_wait(3)
        calling_request = request._pyfuncitem.name

        def fin():
            take_screenhot_and_logcat(driver, device_logger, calling_request)
            driver.quit()

        request.addfinalizer(fin)
        return driver  # provide the fixture value

    @pytest.mark.run(order=1)
    def test_open_main_page(self, driver):
        self.enable_can_usb(driver)
        self.enable_media_control(driver)
        driver_app_field = self.find_element_by_text(driver, '行车应用')
        assert driver_app_field is not None
        resident_app_field = self.find_element_by_text(driver, '驻车应用')
        assert resident_app_field is not None
        #
    # def test_open_window(self, driver):
        window_label = self.find_element_by_text(driver, '车窗')
        assert window_label is not None
        window_container = self.find_element_by_id(
            driver, self.package, 'main_widget_window_view')

        timeout = 30
        readTh = ReadThread(timeout)
        # Open can device and read can data
        readTh.start()

        touch = TouchAction(driver)
        half_open_location = find_element_xy_in_container(
            window_container.location['x'], window_container.location['y'], window_container.size['width'], window_container.size['height'], 1, 4)
        all_open_location = find_element_xy_in_container(
            window_container.location['x'], window_container.location['y'], window_container.size['width'], window_container.size['height'], 3, 4)

        touch.tap(None, half_open_location['x'],
                  half_open_location['y'], 1).perform()
        touch.tap(None, all_open_location['x'],
                  all_open_location['y'], 1).perform()

        check_can_frame_1 = CheckFrame(
            id='0x10AEC041', data='0x40 01 00 00 00 00 00 00 ', control='0', extended='1')
        check_can_frame_2 = CheckFrame(
            id='0x10AEC041', data='0x40 03 00 00 00 00 00 00 ', control='0', extended='1')
        checkTh = CheckThread(timeout, [check_can_frame_1, check_can_frame_2])
        checkTh.start()
        checkTh.join()
        readTh.stop()

    def enable_can_usb(self, driver):
        message = self.find_element_by_id(driver, 'android', 'message')
        assert message.text == '允许应用“HMI Demo”访问该USB设备吗？'
        button = self.find_element_by_id(driver, 'android', 'button1')
        button.click()

    def enable_media_control(self, driver):
        self.find_element_by_text(driver, '允许').click()
        switch_field = driver.find_elements_by_android_uiautomator(
            'new UiSelector().clickable(true)')
        switch_field[0].click()
        self.find_element_by_text(driver, '允许').click()
        driver.back()

    def find_element_by_text(self, driver, text):
        return driver.find_element_by_android_uiautomator('new UiSelector().text("{}")'.format(text))

    def find_element_by_id(self, driver, scope, element_id):
        return driver.find_element_by_id('{}:id/{}'.format(scope, element_id))
