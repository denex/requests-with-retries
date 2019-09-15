requests-with-retries
=====================

Doing request with retry

Example
-------

```python
with SessionWithRetries() as session:
    response = session.get('http://example.com/')
    print(response.text)
```

It will try 3 times to connect and 2 time to read
