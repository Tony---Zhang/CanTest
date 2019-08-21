import os
import sys
import time
import re
from appium import webdriver

def str_sub(content,num):
    ct = content.replace('[','').replace(']','')
    return ct.split(':')[num].strip()

def get_serialno():
    """
    Objective:解决当多个手机连接电脑，Android adb shell命令使用问题.
    当只有一台手机时，自动连接。
    """
    phone_brand = []
    serial_num = []

    if os.popen("adb get-state").read() != "device":
        os.popen("adb kill-server")
        os.popen("adb start-server")
        time.sleep(2)
    device_list = os.popen(" adb devices -l").read()

    if "model" not in device_list:
        print("-> Did not detect any Device.")
        sys.exit()
    else:
        serial_num = [sn.split()[0] for sn in device_list.split('\n') if sn and not sn.startswith('List')]
        for sn in serial_num:
            for mi in os.popen("adb -s {0} shell getprop".format(sn)):
                if "ro.build.fingerprint" in mi:
                    model = str_sub(mi,1).split('/')
                    phone_brand.append(model[0])
    devices_info = dict(zip(phone_brand, serial_num))

    if len(devices_info.keys()) > 1:
        print(devices_info)
        deviceId = input(" \n -> Please input mobile brand to connect:")
        return deviceId
    elif len(devices_info.keys()) == 1:
        return list(devices_info.values())[0]

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)
APPIUM_LOCAL_HOST_URL = 'http://localhost:4723/wd/hub'

# Read mobile deviceId
device_id = get_serialno()

# Read mobile os Version
os_version = os.popen('adb -s {0} shell getprop ro.build.version.release'.format(device_id)).read()
    
def appium_start(package, path, reset, bundle):
    desired_caps = {
        'automationName': 'UiAutomator2',
        'platformName': 'Android',                      #平台
        'platformVersion': os_version,                  #系统版本
        'deviceName': device_id,                        #测试设备ID
        'app': PATH(path),
        'adbExecTimeout': 50000,
        'noReset': not reset,
        'fullReset': reset,
        'unicodeKeyboard': True,
        'resetKeyboard': True,
        'autoGrantPermissions': True,
        'appPackage': package
    }
    if "appWaitPackage" in bundle:
        desired_caps.setdefault("appWaitPackage", bundle["appWaitPackage"])
    if "appWaitActivity" in bundle:
        desired_caps.setdefault("appWaitActivity", bundle["appWaitActivity"])
    uninstall(device_id, package)
    return webdriver.Remote(APPIUM_LOCAL_HOST_URL, desired_caps)

def uninstall(device_id, package):
    os.popen("adb -s {0} uninstall {1}".format(device_id, package))