import http.client as httplib


class MockResposne:

    def __init__(self, headers=None, status_code=None, content=None):
        self.headers = headers or {'Content-Type': 'text/html; charset="utf-8"'}
        self.status_code = status_code or httplib.OK
        self.content = content or ''
