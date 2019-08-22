import threading
from time import sleep
from can.can_adapter import CanAdapter

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

    def run(self):
        can_adapter = CanAdapter(can_index=CANIndex, device_index=DeviceIndex)
        can_adapter.run(receive_data, self._timeout)


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
                return True
        print('Can not find check can frame')
        return False

    def run(self):
        time_acc = 0
        while time_acc < self._timeout:
            # Delay
            if len(receive_data) > 0:
                check = receive_data.pop()
                self.check_result(check)
            time_acc = time_acc + 0.1
            sleep(0.1)


class CheckFrame:
    def __init__(self, id, data, control, extended):
        self._id = id
        self._data = data
        self._control = control
        self._extended = extended

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    @property
    def control(self):
        return self._control

    @property
    def extented(self):
        return self._extended

    def is_equal_to(self, other):
        return self.id == other.id and self.data == other.data and self.control == other.control and self.extented == other.extented


timeout = 30
readTh = ReadThread(timeout)
readTh.start()
check_can_frame_1 = CheckFrame(
    '0x10AEC041', '0x40 01 00 00 00 00 00 00 ', '0', '1')
check_can_frame_2 = CheckFrame(
    '0x10AEC041', '0x40 03 00 00 00 00 00 00 ', '0', '1')
checkTh = CheckThread(timeout, [check_can_frame_1, check_can_frame_2])
checkTh.start()
readTh.join()
checkTh.join()
# Enter the enter to continue
# print("Enter the enter to continue")
# input()
