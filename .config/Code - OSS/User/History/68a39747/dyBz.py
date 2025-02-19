import logging
import typing
from os.path import basename
from time import ctime

from .flash import write_flash_all, write_fw_signature, get_fw_info
from .init_data_dir import PYTHON_VALIDITY_DATA_DIR
from .sensor import reboot, write_hw_reg32, read_hw_reg32, identify_sensor
from .usb import usb, SupportedDevices

"""Defines various constants for firmware files"""

from .usb import SupportedDevices

FIRMWARE_URIS = {
    SupportedDevices.DEV_90: {
        'driver': 'https://download.lenovo.com/pccbbs/mobiles/n1cgn08w.exe',
        'referral': 'https://support.lenovo.com/us/en/downloads/DS120491',
        'sha512': 'd839fa65adf4c952ecb4a5c4b2fc5b5bdedd8e02a421564bdc7fae1d281be4ea26fcde2333f2ab78d56cef0fdccce0a3cf429300b89544cdc9cfee6d0fe0db55'
    },
    SupportedDevices.DEV_97: {
        'driver': 'https://download.lenovo.com/pccbbs/mobiles/nz3gf07w.exe',
        'referral': 'https://download.lenovo.com/pccbbs/mobiles/nz3gf07w.exe',
        'sha512': 'a4a4e6058b1ea8ab721953d2cfd775a1e7bc589863d160e5ebbb90344858f147d695103677a8df0b2de0c95345df108bda97196245b067f45630038fb7c807cd'
    },
    SupportedDevices.DEV_9a: {
        'driver': 'https://download.lenovo.com/pccbbs/mobiles/nz3gf07w.exe',
        'referral': 'https://download.lenovo.com/pccbbs/mobiles/nz3gf07w.exe',
        'sha512': 'a4a4e6058b1ea8ab721953d2cfd775a1e7bc589863d160e5ebbb90344858f147d695103677a8df0b2de0c95345df108bda97196245b067f45630038fb7c807cd'
    },
    SupportedDevices.DEV_9d: {
        'driver': 'https://download.lenovo.com/pccbbs/mobiles/nz3gf07w.exe',
        'referral': 'https://download.lenovo.com/pccbbs/mobiles/nz3gf07w.exe',
        'sha512': 'a4a4e6058b1ea8ab721953d2cfd775a1e7bc589863d160e5ebbb90344858f147d695103677a8df0b2de0c95345df108bda97196245b067f45630038fb7c807cd'
    }
}

FIRMWARE_NAMES = {
    SupportedDevices.DEV_90: '6_07f_Lenovo.xpfwext',
    SupportedDevices.DEV_97: '6_07f_lenovo_mis_qm.xpfwext',
    SupportedDevices.DEV_9a: '6_07f_lenovo_mis_qm.xpfwext',
    SupportedDevices.DEV_9d: '6_07f_lenovo_mis_qm.xpfwext'
}


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
