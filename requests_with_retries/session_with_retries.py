from typing import Any, Dict, Optional, Tuple, Union

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .connect_and_read_timeout import ConnectAndReadTimeout


class SessionWithRetries(requests.Session):
    """
    >>> with SessionWithRetries() as session:
    ...     session.get('http://example.com/').ok
    True
    """
    DEFAULT_TIMEOUT = ConnectAndReadTimeout(
        # https://2.python-requests.org/en/master/user/advanced/#timeouts
        connect_timeout=0.7,
        read_timeout=3,
    )

    DEFAULT_CONNECT_ATTEMPTS: int = 3
    DEFAULT_READ_ATTEMPTS: int = 2
    DEFAULT_BACKOFF_FACTOR: float = 0.1

    def __init__(
        self,
        timeout: Union[float, Tuple[float, float]] = DEFAULT_TIMEOUT,
        connect_attempts: int = DEFAULT_CONNECT_ATTEMPTS,
        read_attempts: int = DEFAULT_READ_ATTEMPTS,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        **retry_options: Dict[str, Any],
    ):
        super().__init__()

        self.__timeout = timeout

        self.__retry = Retry(
            connect=connect_attempts,
            read=read_attempts,
            backoff_factor=backoff_factor,
            **retry_options,
        )

        self.mount('https://', HTTPAdapter(max_retries=self.__retry))
        self.mount('http://', HTTPAdapter(max_retries=self.__retry))

    def request(self, *args, **kwargs) -> Response:
        """
        Override in order to explicitly pass timeout
        """

        if 'timeout' in kwargs:
            raise ValueError(
                'Do not pass timeout to request directly.'
                ' Set timeout in session constructor'
            )

        return super().request(
            *args, **kwargs,
            timeout=self.__timeout,
        )

    def sum_of_connect_time(self) -> Optional[float]:
        """

        :return:
        """

        connect_timeout = (
            self.__timeout[0]
            if isinstance(self.__timeout, tuple)
            else self.__timeout
        )
        if connect_timeout is None:
            return None

        number_of_times_to_connect = min(filter(None, (self.__retry.connect, self.__retry.total)))
        time_socket_waits = connect_timeout * number_of_times_to_connect
        time_backoff_wait = self.__retries_time(number_of_times_to_connect)

        return time_socket_waits + time_backoff_wait

    def sum_of_backoff_time(self, worst_case: bool = False) -> float:
        """
        :param worst_case: Hypothetical case when
               all retries (connect, read, redirect, status)
               are involved
        :return: Approximate amount of seconds could spend in retries
        """
        reduce_func = sum if worst_case else max
        sum_of_retries = reduce_func(
            filter(
                None,
                (
                    self.__retry.connect,
                    self.__retry.read,
                    self.__retry.redirect,
                    self.__retry.status
                )
            )
        )
        max_retries = (
            sum_of_retries
            if self.__retry.total is None
            else min(self.__retry.total, sum_of_retries)
        )

        return self.__retries_time(max_retries)

    def __retries_time(self, number_of_retries) -> float:
        # Each retry waits for
        # {backoff factor} * (2 ** ({number of total retries} - 1))
        # so sum of wait time will be {backoff factor} * (2 ** {number of total retries} - 1)
        return self.__retry.backoff_factor * (2 ** number_of_retries - 1)
