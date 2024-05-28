from smbus2 import SMBus

class I2C():
    def __init__(self, address, bus=1, mode="normal"):
        self._address = address
        self._bus = bus
        self._smbus = SMBus(self._bus)
        self._mode = mode

    def esp32_write(self, reg, data):
        _cmd = 0x02
        if not isinstance(data, list):
            data = [data]
        return self._smbus.write_i2c_block_data(self._address, _cmd, [reg]+data)

    def esp32_read(self, reg, len):
        _cmd = 0x01
        self._smbus.write_i2c_block_data(self._address, _cmd, [reg])
        result = []
        for _ in range(len):
            result.append(self.read_byte())
        return result

    def write_byte(self, data):
        return self._smbus.write_byte(self._address, data)

    def write_byte_data(self, reg, data):
        if self._mode == "normal":
            return self._smbus.write_byte_data(self._address, reg, data)
        elif self._mode == "esp32":
            return self.esp32_write(reg, data)

    def write_word_data(self, reg, data):
        if self._mode == "normal":
            return self._smbus.write_word_data(self._address, reg, data)
        elif self._mode == "esp32":
            return self.esp32_write(reg, data)

    def write_block_data(self, reg, data):
        if self._mode == "normal":
            return self._smbus.write_i2c_block_data(self._address, reg, data)
        elif self._mode == "esp32":
            return self.esp32_write(reg, data)

    def read_byte(self):
        return self._smbus.read_byte(self._address)

    def read_byte_data(self, reg):
        if self._mode == "normal":
            return self._smbus.read_byte_data(self._address, reg)
        elif self._mode == "esp32":
            return self.esp32_read(reg, 1)[0]
            
    def read_word_data(self, reg):
        if self._mode == "normal":
            return self._smbus.read_word_data(self._address, reg)
        elif self._mode == "esp32":
            result = self.esp32_read(reg, 2)
            return result[1]<<8 | result[0]

    def read_block_data(self, reg, num):
        if self._mode == "normal":
            return self._smbus.read_i2c_block_data(self._address, reg, num)
        elif self._mode == "esp32":
            return self.esp32_read(reg, num)

    def is_ready(self):
        addresses = I2C.scan(self._bus)
        if self._address in addresses:
            return True
        else:
            return False

    @staticmethod
    def scan(busnum=1, force=False):
        devices = []
        for addr in range(0x03, 0x77 + 1):
            read = SMBus.read_byte, (addr,), {'force':force}
            write = SMBus.write_byte, (addr, 0), {'force':force}
            for func, args, kwargs in (read, write):
                try:
                    with SMBus(busnum) as bus:
                        data = func(bus, *args, **kwargs)
                        devices.append(addr)
                        break
                except OSError as expt:
                    if expt.errno == 16:
                        # just busy, maybe permanent by a kernel driver or just temporary by some user code
                        pass
        return devices
