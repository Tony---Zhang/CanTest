class CanFrame:
    def __init__(self, id, data, control, extented, data_length, timestamp):
        self._id = id
        self._data = data
        self._control = control
        self._extended = extented
        self._data_length = data_length
        self._timestamp = timestamp

    @property
    def id(self):
        return "0x%X" % self._id

    @property
    def data(self):
        data = "0x"
        for i in range(0, self._data_length):
            data = data + "%02X " % self._data[i]
        return data

    @property
    def data_length(self):
        return self._data_length

    @property
    def control(self):
        return "%d" % self._control

    @property
    def extented(self):
        return "%d" % self._extended

    @property
    def timestamp(self):
        return self._timestamp
