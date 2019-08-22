from ctypes import *
import threading
from time import sleep
# import USB-CAN module
import can.control_can
from can.can_frame import CanFrame


class CanAdapter:
    DevType = can.control_can.VCI_USBCAN2
    debug = False

    def __init__(self, can_index, device_index):
        self._can_index = can_index
        self._device_index = device_index
        self._interrupt = False

    @property
    def can_index(self):
        return self._can_index

    @property
    def device_index(self):
        return self._device_index

    # Scan device
    def scan_device(self):
        result = can.control_can.VCI_ScanDevice(1)
        if(result == 0):
            return False
        else:
            self.log("Have %d device connected!" % result)
            return True

    # Get board info
    def get_board_info(self):
        CAN_BoardInfo = can.control_can.VCI_BOARD_INFO_EX()
        result = can.control_can.VCI_ReadBoardInfoEx(
            self.device_index, byref(CAN_BoardInfo))
        if(result == can.control_can.STATUS_ERR):
            return False
        else:
            self.log("--CAN_BoardInfo.ProductName = %s" %
                     bytes(CAN_BoardInfo.ProductName).decode('ascii'))
            self.log("--CAN_BoardInfo.FirmwareVersion = V%d.%d.%d" %
                     (CAN_BoardInfo.FirmwareVersion[1], CAN_BoardInfo.FirmwareVersion[2], CAN_BoardInfo.FirmwareVersion[3]))
            self.log("--CAN_BoardInfo.HardwareVersion = V%d.%d.%d" %
                     (CAN_BoardInfo.HardwareVersion[1], CAN_BoardInfo.HardwareVersion[2], CAN_BoardInfo.HardwareVersion[3]))
            self.log("--CAN_BoardInfo.SerialNumber = ")
            for i in range(0, len(CAN_BoardInfo.SerialNumber)):
                self.log("%02X" % CAN_BoardInfo.SerialNumber[i])
            self.log("")
            return True

    # Open device
    def open_device(self):
        result = can.control_can.VCI_OpenDevice(
            CanAdapter.DevType, self.device_index, 0)
        if(result == can.control_can.STATUS_ERR):
            return False
        else:
            self.log("Open device success!")
            return True

    # Start CAN
    def start_can(self):
        result = can.control_can.VCI_StartCAN(
            CanAdapter.DevType, self.device_index, self.can_index)
        if(result == can.control_can.STATUS_ERR):
            return False
        else:
            self.log("Start CAN success!")
            return True

    # Get CAN status
    def get_status(self):
        CAN_Status = can.control_can.VCI_CAN_STATUS()
        result = can.control_can.VCI_ReadCANStatus(
            CanAdapter.DevType, self.device_index, self.can_index, byref(CAN_Status))
        if(result == can.control_can.STATUS_ERR):
            self.log("Get CAN status failed!")
        else:
            self.log("Buffer Size : %d" % CAN_Status.BufferSize)
            self.log("ESR : 0x%08X" % CAN_Status.regESR)
            self.log("------Error warning flag : %d" %
                     ((CAN_Status.regESR >> 0) & 0x01))
            self.log("------Error passive flag : %d" %
                     ((CAN_Status.regESR >> 1) & 0x01))
            self.log("------Bus-off flag : %d" %
                     ((CAN_Status.regESR >> 2) & 0x01))
            self.log("------Last error code(%d) : " %
                     ((CAN_Status.regESR >> 4) & 0x07))
            Error = ["No Error", "Stuff Error", "Form Error", "Acknowledgment Error",
                     "Bit recessive Error", "Bit dominant Error", "CRC Error", "Set by software"]
            self.log(Error[(CAN_Status.regESR >> 4) & 0x07])

    # Stop receive can data
    def stop(self):
        result = can.control_can.VCI_ResetCAN(
            CanAdapter.DevType, self.device_index, self.can_index)
        self.log("VCI_ResetCAN: %d" % result)

    # Close device
    def close(self):
        result = can.control_can.VCI_CloseDevice(
            CanAdapter.DevType, self.device_index)
        self.log("VCI_CloseDevice: %d" % result)

    def interrupt(self):
        self._interrupt = True

    def log(self, msg):
        if self.debug:
            print(msg)

    def run(self, receive_data, timeout):
        if self.scan_device() == False:
            self.log("No device connected!")
            exit()
        if self.get_board_info() == False:
            self.log("Get board info failed!")
            exit()
        if self.open_device() == False:
            self.log("Open device failed!")
            exit()

        # Can configuration
        CAN_InitEx = can.control_can.VCI_INIT_CONFIG_EX()
        CAN_InitEx.CAN_ABOM = 0
        CAN_InitEx.CAN_Mode = 0
        # Baud Rate: 1M
        # SJW, BS1, BS2, PreScale, detail in controlcan.py
        CAN_InitEx.CAN_BRP = 9
        CAN_InitEx.CAN_BS1 = 1
        CAN_InitEx.CAN_BS2 = 2
        CAN_InitEx.CAN_SJW = 1

        CAN_InitEx.CAN_NART = 1  # text repeat send management: disable text repeat sending
        CAN_InitEx.CAN_RFLM = 0  # FIFO lock management: new text overwrite old
        CAN_InitEx.CAN_TXFP = 0  # send priority management: by order
        CAN_InitEx.CAN_RELAY = 0  # relay feature enable: close relay function
        result = can.control_can.VCI_InitCANEx(
            CanAdapter.DevType, self.device_index, self.can_index, byref(CAN_InitEx))
        if(result == can.control_can.STATUS_ERR):
            self.log("Init device failed!")
            exit()
        else:
            self.log("Init device success!")

        # Set filter
        CAN_FilterConfig = can.control_can.VCI_FILTER_CONFIG()
        CAN_FilterConfig.FilterIndex = 0
        CAN_FilterConfig.Enable = 1
        CAN_FilterConfig.ExtFrame = 0
        CAN_FilterConfig.FilterMode = 0
        CAN_FilterConfig.ID_IDE = 0
        CAN_FilterConfig.ID_RTR = 0
        CAN_FilterConfig.ID_Std_Ext = 0
        CAN_FilterConfig.MASK_IDE = 0
        CAN_FilterConfig.MASK_RTR = 0
        CAN_FilterConfig.MASK_Std_Ext = 0
        result = can.control_can.VCI_SetFilter(
            CanAdapter.DevType, self.device_index, self.can_index, byref(CAN_FilterConfig))
        if(result == can.control_can.STATUS_ERR):
            self.log("Set filter failed!")
            exit()
        else:
            self.log("Set filter success!")

        if self.start_can() == False:
            self.log("Start CAN failed!")
            exit()
        # Delay
        sleep(0.5)

        self.get_status()

        time_acc = 0
        del receive_data[:]
        # Read data
        while time_acc <= timeout and not self._interrupt:
            DataNum = can.control_can.VCI_GetReceiveNum(
                CanAdapter.DevType, self.device_index, self.can_index)
            if(DataNum > 0):
                self.log('received: {}'.format(DataNum))
                CAN_ReceiveData = (can.control_can.VCI_CAN_OBJ*DataNum)()
                can.control_can.VCI_Receive(
                    CanAdapter.DevType, self.device_index, self.can_index, byref(CAN_ReceiveData), DataNum, 0)
                for i in range(0, DataNum):
                    can_frame = CanFrame(
                        id=CAN_ReceiveData[i].ID,
                        data=CAN_ReceiveData[i].Data,
                        control=CAN_ReceiveData[i].RemoteFlag,
                        extented=CAN_ReceiveData[i].ExternFlag,
                        data_length=CAN_ReceiveData[i].DataLen,
                        timestamp=CAN_ReceiveData[i].TimeStamp)
                    receive_data.append(can_frame)
            # Delay
            time_acc = time_acc + 0.1
            sleep(0.1)

        self.stop()
        self.close()
