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
