from enum import IntEnum

__all__ = ['DPS_FAILED', 'DPS_FAILED_INIT', 'DPS_FAILED_SETUP', 'DPS_FAILED_READING', 'DPS_FAILED_WRITING', 'DPS_STATUS_ERROR', 'opMode', 'config_registers', 'registers', 'measurement_conf', 'data_registers']

class _DPS_ERROR(Exception):
    "dps310 base error"

class DPS_FAILED(_DPS_ERROR):
    "Something went wrong on dps310"

class DPS_FAILED_INIT(_DPS_ERROR):
    "Failed initializing dps310"

class DPS_FAILED_SETUP(_DPS_ERROR):
    "Failed setting up dps310"

class DPS_FAILED_READING(_DPS_ERROR):
    "Failed reading data from the dps310"

class DPS_FAILED_WRITING(_DPS_ERROR):
    "Failed writing data on the dps310"

class DPS_STATUS_ERROR(_DPS_ERROR):
    "Status of dps310 is invalid"

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
    PRS_CONF        = (0x06, 0x77, 0)
    MEAS_CTRL       = (0x08, 0x07, 0)
    FIFO_EN         = (0x09, 0x02, 1)
    TEMP_RDY        = (0x08, 0x20, 5)
    PRS_RDY         = (0x08, 0x10, 4)
    INT_FLAG_FIFO   = (0x0A, 0x04, 2)
    INT_FLAG_TEMP   = (0x0A, 0x02, 1)
    INT_FLAG_PRS    = (0x0A, 0x01, 0)

class registers():
    PROD_ID         = (0x0D, 0x0F, 0)
    REV_ID          = (0x0D, 0xF0, 4)
    TMP_SENSOR      = (0x07, 0x80, 7)
    TMP_SENSORREC   = (0x28, 0x80, 7)
    TMP_SE          = (0x09, 0x08, 3)
    PRS_SE          = (0x09, 0x04, 2)
    FIFO_FL         = (0x0C, 0x80, 7)
    FIFO_EMPTY      = (0x0B, 0x01, 0)
    FIFO_FULL       = (0x0B, 0x02, 1)
    INT_HL          = (0x09, 0x80, 7)
    INT_SEL         = (0x09, 0x70, 4)

class measurement_conf(IntEnum):
    MEAS_RATE_1     = 0
    MEAS_RATE_2     = 1
    MEAS_RATE_4     = 2
    MEAS_RATE_8     = 3
    MEAS_RATE_16    = 4
    MEAS_RATE_32    = 5
    MEAS_RATE_64    = 6
    MEAS_RATE_128   = 7

class data_registers():
    PRS             = (0x00, 3)
    TMP             = (0x03, 3)
    COEFFS          = (0x10, 18)

class scale_factor():
    scale_factors   = (524288, 1572864, 3670016, 7864320, 253952, 516096, 1040384, 2088960)
