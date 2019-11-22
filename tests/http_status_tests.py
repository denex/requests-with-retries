from contextlib import contextmanager
import http
from http.client import HTTPResponse
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RetryError
from urllib3.connection import HTTPConnection

from requests_with_retries import SessionWithRetries


@contextmanager
def patch_http_response(status=200, reason='OK', length=0, version='1.0', msg=None):
    m_response = MagicMock(spec=http.client.HTTPResponse)
    m_response.status = status
    m_response.reason = reason
    m_response.length = length
    m_response.msg = msg or {}
    m_response.version = version

    with patch.object(HTTPConnection, 'getresponse', return_value=m_response) as m:
        yield m


def test_retry_on_500():
    with SessionWithRetries(
        status=1,  # retries
        status_forcelist={500},  # on 500
    ) as session:
        with patch_http_response(status=500) as m:
            with pytest.raises(RetryError):
                session.get('http://example.com/')

        assert m.call_count == 2
