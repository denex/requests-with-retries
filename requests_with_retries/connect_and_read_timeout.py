from typing import NamedTuple


class ConnectAndReadTimeout(NamedTuple):
    """
    see: https://2.python-requests.org/en/master/user/advanced/#timeouts

    The connect timeout is the number of seconds Requests will wait
    for your client to establish a connection to a remote machine
    (corresponding to the connect()) call on the socket.
    It’s a good practice to set connect timeouts to slightly larger
    than a multiple of 3, which is the default TCP packet retransmission window.

    Once your client has connected to the server and sent the HTTP request,
    the read timeout is the number of seconds the client will wait
    for the server to send a response. (Specifically, it’s the number of seconds
    that the client will wait between bytes sent from the server.
    In 99.9% of cases, this is the time before the server sends the first byte).

    """
    connect_timeout: float
    read_timeout: float
