from typing import NamedTuple


class ConnectAndReadTimeout(NamedTuple):
    """
    see: https://2.python-requests.org/en/master/user/advanced/#timeouts
    """
    connect_timeout: float
    read_timeout: float
