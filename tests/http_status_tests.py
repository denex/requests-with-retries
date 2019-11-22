from contextlib import contextmanager
import http
from http.client import HTTPResponse
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RetryError
from urllib3.connection import HTTPConnection

from requests_with_retries import SessionWithRetries


@contextmanager
def patch_http_response(**attrs):
    m_response = MagicMock(spec=http.client.HTTPResponse)
    m_response.status = 200
    m_response.length = 0
    m_response.msg = {}
    m_response.version = '1.0'
    m_response.reason = 'OK'

    for attr, value in attrs.items():
        setattr(m_response, attr, value)

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
