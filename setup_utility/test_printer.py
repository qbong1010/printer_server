import functools
import logging
import python_escpos as escpos
from typing import Dict, Literal, Optional, Type, Union

from escpos import Escpos
from escpos.exceptions import DeviceNotFoundError, USBNotFoundError

#: keeps track if the usb dependency could be loaded (:py:class:`escpos.printer.Usb`)
_DEP_USB = False

try:
    import usb.core
    import usb.util

    _DEP_USB = True
except ImportError:
    pass


def is_usable() -> bool:
    """Indicate whether this component can be used due to dependencies."""
    usable = False
    if _DEP_USB:
        usable = True
    return usable


def dependency_usb(func):
    """Indicate dependency on usb."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Throw a RuntimeError if usb not installed."""
        if not is_usable():
            raise RuntimeError(
                "Printing with USB connection requires a usb library to "
                "be installed. Please refer to the documentation on "
                "what to install and install the dependencies for USB."
            )
        return func(*args, **kwargs)

    return wrapper