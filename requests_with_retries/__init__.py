from .connect_and_read_timeout import ConnectAndReadTimeout
from .session_with_retries import SessionWithRetries

__all__ = (SessionWithRetries.__name__, ConnectAndReadTimeout.__name__)

name = 'requests-with-retries'
