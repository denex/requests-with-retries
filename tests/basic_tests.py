import socket
from unittest.mock import Mock, patch

import pytest
import requests
from urllib3 import Retry

from requests_with_retries import SessionWithRetries


# noinspection PyPep8Naming
def test__SessionWithRetries__returns_something():
    with SessionWithRetries() as session:
        response = session.get('http://example.com/')
    assert response.ok
    assert response.text


def test__sum_of_connect_time():
    assert 2.0 < SessionWithRetries().sum_of_connect_time() < 3.0


def test__sum_of_backoff_time():
    assert 0.5 < SessionWithRetries().sum_of_backoff_time() < 1.0


def test__sum_of_backoff_time__worst_case():
    assert 3.0 < SessionWithRetries().sum_of_backoff_time(worst_case=True) < 4.0


@pytest.fixture
def p_socket_connect_error():
    m_sock = Mock()
    m_sock.connect.side_effect = ConnectionRefusedError()
    with patch.object(socket, 'socket', autospec=True, return_value=m_sock):
        yield m_sock.connect


# noinspection PyPep8Naming
def test__SessionWithRetries__doing_retries(p_socket_connect_error):
    with SessionWithRetries() as session:
        with patch.object(
            Retry, 'sleep', autospec=True
        ) as p_sleep, pytest.raises(
            requests.exceptions.ConnectionError
        ):
            session.get('http://localhost:8000/')

    assert p_sleep.call_count == session.DEFAULT_CONNECT_ATTEMPTS


def test__timeouts__applied(p_socket_connect_error):
    with SessionWithRetries() as session:
        with patch.object(session, 'send', autospec=True) as m_send:
            session.get('http://localhost:8000/')
        m_send.assert_called_once()
        assert m_send.call_args[1]['timeout'] == session.DEFAULT_TIMEOUT


# noinspection PyPep8Naming
def test__request__raises_ValueError_on_timeout(p_socket_connect_error):
    with SessionWithRetries() as session:
        with pytest.raises(
            ValueError,
            match='Do not pass timeout to request directly. Set timeout in session constructor',
        ):
            session.get('http://localhost:8000', timeout=3)
