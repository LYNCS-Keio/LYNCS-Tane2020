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
        self.__pi = handler
        self.__addr = addr
        try:
            self.__bus = self.__pi.i2c_open(1, self.__addr)
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
            val = self.__pi.i2c_read_byte_data(self.__bus, reg)
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
            (ret, val) = self.__pi.i2c_read_i2c_block_data(self.__bus, reg, length)
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
            val = self.__pi.i2c_read_word_data(self.__bus, reg)
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

    def writeByte(self, reg, data):
        """
        1Byte書き込む。
        
        Parameters
        -------
        reg : int 
            書き込むレジスタのアドレス。
        data : int
            書き込むデータ。
        """
        try:
            self.__pi.i2c_write_byte_data(self.__bus, reg, data)
        except:
            raise I2C_FAILED_WRITING

    def writeByteBitfield(self, reg, mask, shift, data):
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
        """        
        try:
            old = self.readByte(reg)
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        else:
            try:
                self.writeByte(reg, (old & ~mask) | (data << shift) & mask)
            except I2C_FAILED_WRITING:
                raise I2C_FAILED_WRITING

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
            self.__pi.i2c_write_i2c_block_data(self.__bus, reg, data)
        except:
            raise I2C_FAILED_WRITING

    def writeWord(self, reg, data):
        """
        1Word書き込む。

        Parameter
        -------
        reg : int
            書き込むレジスタのアドレス。
        data : int
            書き込むデータ。
        """
        try:
            self.__pi.i2c_write_word_data(self.__bus, reg, data)
        except:
            raise I2C_FAILED_WRITING

    def writeWordBitfield(self, reg, mask, shift, data):
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
        """
        try:
            old = self.readWord(reg)
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        else:
            try:
                self.writeWord(reg, (old & ~mask) | (data << shift) & mask)
            except I2C_FAILED_WRITING:
                raise I2C_FAILED_WRITING

