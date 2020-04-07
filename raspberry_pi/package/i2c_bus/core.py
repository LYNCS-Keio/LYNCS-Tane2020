import pigpio

""" description
pigpioを用いたi2c library



"""

__all__ = ['I2C_FAILED', 'I2C_FAILED_OPEN', 'I2C_FAILED_READING', 'I2C_FAILED_WRITING', 'i2c_bus']

class _I2C_ERROR(Exception):
    "i2c_bus base error"

class I2C_FAILED(_I2C_ERROR):
    "Something went wrong on i2c_bus"

class I2C_FAILED_OPEN(_I2C_ERROR):
    "Failed Opening bus error"

class I2C_FAILED_READING(_I2C_ERROR):
    "Failed reading the device"

class I2C_FAILED_WRITING(_I2C_ERROR):
    "Failed writing on the device"


class i2c_bus():
    def __init__(self, handler, addr):
        """ 
        i2cバスのコンストラクタ

        Parameters
        -------
        handler : pigpio.pi()
            pigpioのハンドラー。
        addr : int
            デバイスのアドレス。
        """
        self._handler = handler
        self._addr = addr
        try:
            self._bus = self._handler.i2c_open(1, self._addr)
        except TypeError:
            raise TypeError
        except:
            raise I2C_FAILED_OPEN

    def readByte(self, reg):
        """ 
        1Byte読み込む。

        Parameters
        -------
        reg : int
            読み込むレジスタのアドレス。

        Returns
        -------
        val : int
            読み込んだデータ。
        """
        try:
            val = self._handler.i2c_read_byte_data(self._bus, reg)
        except:
            raise I2C_FAILED_READING
        else:
            return val

    def readByteBitfield(self, reg, mask, shift):
        """
        レジスタの一部だけを読み取る。

        Parameters
        -------
        reg : int
            読み込むレジスタのアドレス。
        mask : int
            レジスタ内での目的データのマスク。
        shift : int
            マスクしたデータのビットシフト数。

        Returns
        -------
        val : int
            読み込んだデータ。

        Notes
        -----
        例えば 11011001 というデータが格納されたレジスタの3bit目から6bit目(110)を読み出すとき
        maskは 00011100, shiftは2となる。
        """
        try:
            val = self.readByte(reg)
            val = (val & mask) >> shift
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        except:
            raise I2C_FAILED
        else:
            return val

    def readBytes(self, reg, length):
        """
        複数バイトを読み出す。

        Parameters
        -------
        reg : int
            読み込むレジスタのアドレス。
        length : 読み込むバイト数。

        Returns
        -------
        val : list of int
            読み込んだデータ。
        """
        try:
            (ret, val) = self._handler.i2c_read_i2c_block_data(self._bus, reg, length)
            if ret >= 0:
                int_val = [x for x in val]
            else:
                raise I2C_FAILED_READING
        except:
            raise I2C_FAILED_READING
        else:
            return int_val

    def readWord(self, reg):
        """
        1Word読み込む。

        Parameters
        -------
        reg : int
            読み込むレジスタのアドレス。

        Returns
        -------
        val : int
            読み込んだデータ。
        """
        try:
            val = self._handler.i2c_read_word_data(self._bus, reg)
        except:
            raise I2C_FAILED_READING
        else:
            return val

    def readWordBitfield(self, reg, mask, shift):
        """
        レジスタの一部だけを読み取る。

        Parameters
        -------
        reg : int
            読み込むレジスタのアドレス。
        mask : int
            レジスタ内での目的データのマスク。
        shift : int
            マスクしたデータのビットシフト数。

        Returns
        -------
        val : int
            読み込んだデータ。
        """
        try:
            val = self.readWord(reg)
            val = (val & mask) >> shift
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        except:
            raise I2C_FAILED
        else:
            return val

    def writeByte(self, reg, data, no_check=False):
        """
        1Byte書き込む。
        
        Parameters
        -------
        reg : int 
            書き込むレジスタのアドレス。
        data : int
            書き込むデータ。
        no_check : bool
            Trueの場合書き込み後の確認を行わない。
        """
        try:
            self._handler.i2c_write_byte_data(self._bus, reg, data)
            if no_check == False:
                stat = self.readByte(reg)
                if stat != data:
                    #print("checkfailed", stat, data)
                    raise I2C_FAILED_WRITING
                else:
                    #print("checkpassed", bin(data), hex(reg))
                    pass
            else:
                #print("check skipped")
                pass
        except:
            raise I2C_FAILED_WRITING
        else:
            return 0

    def writeByteBitfield(self, reg, mask, shift, data, no_check=False):
        """
        レジスタの一部だけに書き込む。

        Parameters
        -------
        reg : int
            書き込むレジスタのアドレス。
        mask : int
            レジスタ内での目的データのマスク。
        shift : int
            マスクしたデータのビットシフト数。
        data : int
            書き込むデータ。
        no_check : bool
            Trueの場合書き込み後の確認を行わない。
        """        
        try:
            old = self.readByte(reg)
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        else:
            try:
                buf = (old & ~mask) | (data << shift) & mask
                self.writeByte(reg, buf, no_check)
            except I2C_FAILED_WRITING:
                raise I2C_FAILED_WRITING
            else:
                return 0

    def writeBytes(self, reg, data):
        """
        複数バイト書き込む。

        Parameters
        -------
        reg : int
            書き込むレジスタのアドレス。
        data : int
            書き込むデータ。
        """
        try:
            self._handler.i2c_write_i2c_block_data(self._bus, reg, data)
        except:
            raise I2C_FAILED_WRITING

    def writeWord(self, reg, data, no_check=False):
        """
        1Word書き込む。

        Parameter
        -------
        reg : int
            書き込むレジスタのアドレス。
        data : int
            書き込むデータ。
        no_check : bool
            Trueの場合書き込み後の確認を行わない。
        """
        try:
            self._handler.i2c_write_word_data(self._bus, reg, data)
            if no_check == False:
                if self.readWord(reg) != data:
                    raise I2C_FAILED_WRITING
        except:
            raise I2C_FAILED_WRITING
        else:
            return 0

    def writeWordBitfield(self, reg, mask, shift, data, no_check=False):
        """
        レジスタの一部だけに書き込む。

        Parameters
        -------
        reg : int
            書き込むレジスタのアドレス。
        mask : int
            レジスタ内での目的データのマスク。
        shift : int
            マスクしたデータのビットシフト数。
        data : int
            書き込むデータ。
        no_check : bool
            Trueの場合書き込み後の確認を行わない。
        """
        try:
            old = self.readWord(reg)
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        else:
            try:
                buf = (old & ~mask) | (data << shift) & mask
                self.writeWord(reg, buf, no_check)
            except I2C_FAILED_WRITING:
                raise I2C_FAILED_WRITING
            else:
                return 0

