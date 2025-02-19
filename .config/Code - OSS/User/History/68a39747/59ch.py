import logging
import typing
from os.path import basename
from time import ctime

from .firmware_tables import FIRMWARE_NAMES
from .flash import write_flash_all, write_fw_signature, get_fw_info
from .init_data_dir import PYTHON_VALIDITY_DATA_DIR
from .sensor import reboot, write_hw_reg32, read_hw_reg32, identify_sensor
from .usb import usb, SupportedDevices

firmware_home = PYTHON_VALIDITY_DATA_DIR


def default_fwext_name():
    dev = SupportedDevices.from_usbid(usb.usb_dev().idVendor, usb.usb_dev().idProduct)
    # It looks like the firmware file must match DLL, not the hardware.
    # Both DLL and xpfwext are universal.
    # The device dependant code seems to be loaded dynamically (via encrypted blobs).
    # So, it is important that xpfwext file is matching the blobs contents.
    return FIRMWARE_NAMES[dev]


def upload_fwext(fw_path: typing.Optional[str] = None):
    fwi = get_fw_info(2)
    if fwi is not None:
        logging.info('Detected firmware version %d.%d (%s))' %
                     (fwi.major, fwi.minor, ctime(fwi.buildtime)))
        return
    else:
        logging.info('No firmware detected. Uploading...')

    # no idea what this is:
    write_hw_reg32(0x8000205c, 7)
    if read_hw_reg32(0x80002080) not in [2, 3]:
        raise Exception('Unexpected register value')

    dev = identify_sensor()
    logging.debug('Sensor: %s' % dev.name)
    # ^ TODO -- what is the real reason to detect HW at this stage?
    #           just a guess: perhaps it is used to construct fwext filename

    default_name = firmware_home + '/' + default_fwext_name()
    if not fw_path:
        fw_path = default_name
    elif basename(fw_path) != default_name:
        logging.warning('WARNING: Your device fw is supposed to be called {}'.format(default_name))

    with open(fw_path, 'rb') as f:
        fwext = f.read()

    fwext = fwext[fwext.index(b'\x1a') + 1:]
    fwext, signature = fwext[:-0x100], fwext[-0x100:]

    write_flash_all(2, 0, fwext)
    write_fw_signature(2, signature)

    fwi = get_fw_info(2)
    if fwi is None:
        raise Exception('No firmware detected')

    logging.info('Loaded FWExt version %d.%d (%s), %d modules' %
                 (fwi.major, fwi.minor, ctime(fwi.buildtime), len(fwi.modules)))

    # Reboot
    reboot()
    raise Exception('Reboot')
