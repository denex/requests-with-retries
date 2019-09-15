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


def test__max_wait_time__by_default():
    assert SessionWithRetries().max_wait_time() < 1.0


def test__max_wait_time__worst_case():
    assert SessionWithRetries().max_wait_time(worst_case=True) < 4.0


@pytest.fixture
def patched_socket_connect():
    m_sock = Mock()
    m_sock.connect.side_effect = ConnectionRefusedError()
    with patch.object(socket, 'socket', autospec=True, return_value=m_sock):
        yield m_sock.connect


# noinspection PyPep8Naming
def test__SessionWithRetries__doing_retries(patched_socket_connect):
    with SessionWithRetries() as session:
        with patch.object(
            Retry, 'sleep', autospec=True
        ) as p_sleep, pytest.raises(
            requests.exceptions.ConnectionError
        ):
            session.get('http://localhost:8000/')

    p_sleep.call_count = session.DEFAULT_CONNECT_ATTEMPTS


def test__timeouts__applied(patched_socket_connect):
    with SessionWithRetries() as session:
        with patch.object(session, 'send', autospec=True) as m_send:
            session.get('http://localhost:8000/')
        m_send.assert_called_once()
        assert m_send.call_args[1]['timeout'] == session.DEFAULT_TIMEOUT


# noinspection PyPep8Naming
def test__request__raises_ValueError_on_timeout(patched_socket_connect):
    with SessionWithRetries() as session:
        with pytest.raises(
            ValueError,
            match='Do not pass timeout to request directly. Set timeout in session constructor',
        ):
            session.get('http://localhost:8000', timeout=3)
