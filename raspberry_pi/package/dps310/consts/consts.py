from enum import IntEnum, auto

class opMode(IntEnum):
    IDLE            = 0x00
    CMD_PRS         = 0x01
    CMD_TEMP        = 0x02
    CONT_PRS        = 0x05
    CONT_TMP        = 0x06
    CONT_BOTH       = 0x07
    ERR             = 0xFF

class config_registers():
    TMP_CONF        = (0x07, 0x77, 0)
    PM_CONF         = (0x06, 0x77, 0) 
    MEAS_CTRL       = (0x08, 0x07, 0)
    FIFO_EN         = (0x09, 0x02, 1)
    TEMP_RDY        = (0x08, 0x20, 5)
    PRS_RDY         = (0x08, 0x10, 4)
    INT_FLAG_FIFO   = (0x0A, 0x04, 2)
    INT_FLAG_TEMP   = (0x0A, 0x02, 1)
    INT_FLAG_PRS    = (0x0A, 0x01, 0)

class registers():
    PROD_ID         = {0x0D, 0x0F, 0}
    REV_ID          = {0x0D, 0xF0, 4}
    TMP_SENSOR      = {0x07, 0x80, 7}
    TMP_SENSORREC   = {0x28, 0x80, 7}
    TMP_SE          = {0x09, 0x08, 3}
    PRS_SE          = {0x09, 0x04, 2}
    FIFO_FL         = {0x0C, 0x80, 7}
    FIFO_EMPTY      = {0x0B, 0x01, 0}
    FIFO_FULL       = {0x0B, 0x02, 1}
    INT_HL          = {0x09, 0x80, 7}
    INT_SEL         = {0x09, 0x70, 4}

class measurement_rate(IntEnum):
    MEAS_RATE_1     = 0
    MEAS_RATE_2     = auto() 
    MEAS_RATE_4     = auto()  
    MEAS_RATE_8     = auto()  
    MEAS_RATE_16    = auto()
    MEAS_RATE_32    = auto()
    MEAS_RATE_64    = auto()
    MEAS_RATE_128   = auto()