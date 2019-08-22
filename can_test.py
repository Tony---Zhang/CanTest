from ctypes import *
from time import sleep
# import USB-CAN module
import can.control_can
from can.can_frame import CanFrame

# get can board info
CAN_GET_BOARD_INFO = 1
# receiving can status
CAN_GET_STATUS = 1
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
"""
DevType: fixed for below setting
"""
DevType = can.control_can.VCI_USBCAN2

receive_data = []


# Scan device
def scan_device():
    result = can.control_can.VCI_ScanDevice(1)
    if(result == 0):
        return False
    else:
        print("Have %d device connected!" % result)
        return True


# Get board info
def get_board_info(device_index):
    if(CAN_GET_BOARD_INFO == 1):
        CAN_BoardInfo = can.control_can.VCI_BOARD_INFO_EX()
        result = can.control_can.VCI_ReadBoardInfoEx(
            device_index, byref(CAN_BoardInfo))
        if(result == can.control_can.STATUS_ERR):
            return False
        else:
            print("--CAN_BoardInfo.ProductName = %s" %
                  bytes(CAN_BoardInfo.ProductName).decode('ascii'))
            print("--CAN_BoardInfo.FirmwareVersion = V%d.%d.%d" %
                  (CAN_BoardInfo.FirmwareVersion[1], CAN_BoardInfo.FirmwareVersion[2], CAN_BoardInfo.FirmwareVersion[3]))
            print("--CAN_BoardInfo.HardwareVersion = V%d.%d.%d" %
                  (CAN_BoardInfo.HardwareVersion[1], CAN_BoardInfo.HardwareVersion[2], CAN_BoardInfo.HardwareVersion[3]))
            print("--CAN_BoardInfo.SerialNumber = ", end='')
            for i in range(0, len(CAN_BoardInfo.SerialNumber)):
                print("%02X" % CAN_BoardInfo.SerialNumber[i], end='')
            print("")
            return True
    return True


# Open device
def open_device(dev_type, dev_index):
    result = can.control_can.VCI_OpenDevice(dev_type, dev_index, 0)
    if(result == can.control_can.STATUS_ERR):
        return False
    else:
        print("Open device success!")
        return True


# Start CAN
def start_can(dev_type, device_index, can_index):
    result = can.control_can.VCI_StartCAN(dev_type, device_index, can_index)
    if(result == can.control_can.STATUS_ERR):
        return False
    else:
        print("Start CAN success!")
        return True


if scan_device() == False:
    print("No device connected!")
    exit()
if get_board_info(DeviceIndex) == False:
    print("Get board info failed!")
    exit()
if open_device(DevType, DeviceIndex) == False:
    print("Open device failed!")
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
    DevType, DeviceIndex, CANIndex, byref(CAN_InitEx))
if(result == can.control_can.STATUS_ERR):
    print("Init device failed!")
    exit()
else:
    print("Init device success!")

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
    DevType, DeviceIndex, CANIndex, byref(CAN_FilterConfig))
if(result == can.control_can.STATUS_ERR):
    print("Set filter failed!")
    exit()
else:
    print("Set filter success!")


if start_can(DevType, DeviceIndex, CANIndex) == False:
    print("Start CAN failed!")
    exit()
# Delay
sleep(0.5)

# Get CAN status
if(CAN_GET_STATUS == 1):
    CAN_Status = can.control_can.VCI_CAN_STATUS()
    result = can.control_can.VCI_ReadCANStatus(
        DevType, DeviceIndex, CANIndex, byref(CAN_Status))
    if(result == can.control_can.STATUS_ERR):
        print("Get CAN status failed!")
    else:
        print("Buffer Size : %d" % CAN_Status.BufferSize)
        print("ESR : 0x%08X" % CAN_Status.regESR)
        print("------Error warning flag : %d" %
              ((CAN_Status.regESR >> 0) & 0x01))
        print("------Error passive flag : %d" %
              ((CAN_Status.regESR >> 1) & 0x01))
        print("------Bus-off flag : %d" % ((CAN_Status.regESR >> 2) & 0x01))
        print("------Last error code(%d) : " %
              ((CAN_Status.regESR >> 4) & 0x07), end='')
        Error = ["No Error", "Stuff Error", "Form Error", "Acknowledgment Error",
                 "Bit recessive Error", "Bit dominant Error", "CRC Error", "Set by software"]
        print(Error[(CAN_Status.regESR >> 4) & 0x07])


timeout = 30
time_acc = 0

del receive_data[:]
# Read data
while time_acc <= timeout:
    DataNum = can.control_can.VCI_GetReceiveNum(DevType, DeviceIndex, CANIndex)
    if(DataNum > 0):
        print('receive: {}'.format(DataNum))
        CAN_ReceiveData = (can.control_can.VCI_CAN_OBJ*DataNum)()
        can.control_can.VCI_Receive(
            DevType, DeviceIndex, CANIndex, byref(CAN_ReceiveData), DataNum, 0)
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

for i in range(0, len(receive_data)):
    can_frame = receive_data[i]
    print("--CAN_Number: %d" % i)
    print("--CAN_ReceiveData.RemoteFlag = %d" % can_frame.control)
    print("--CAN_ReceiveData.ExternFlag = %d" % can_frame.extented)
    print("--CAN_ReceiveData.ID = %s" % can_frame.id)
    print("--CAN_ReceiveData.DataLen = %d" % can_frame.data_length)
    print("--CAN_ReceiveData.Data: %s" % can_frame.data)
    print("--CAN_ReceiveData.TimeStamp = %d" % can_frame.timestamp)

# Enter the enter to continue
print("Enter the enter to continue")
input()

# Stop receive can data
result = can.control_can.VCI_ResetCAN(DevType, DeviceIndex, CANIndex)
print("VCI_ResetCAN result = %d" % result)
# Close device
result = can.control_can.VCI_CloseDevice(DevType, DeviceIndex)
print("VCI_CloseDevice result = %d" % result)
