#!/usr/bin/env python3
"""로컬 프록시 서버: discovery_maker.html을 서빙하고 Anthropic API를 프록시합니다.
실행: python3 server.py
브라우저에서: http://localhost:8000/discovery_maker.html
"""
import http.server
import urllib.request
import json
import os

PORT = 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/messages':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            api_key = self.headers.get('x-api-key', '')

            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=body,
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                },
                method='POST'
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    result = resp.read()
                    self.send_response(resp.status)
                    self._cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(result)
            except urllib.error.HTTPError as e:
                result = e.read()
                self.send_response(e.code)
                self._cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(result)
        else:
            self.send_response(404)
            self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, x-api-key, anthropic-version')

    def log_message(self, fmt, *args):
        pass  # 로그 없애기


os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f'서버 시작: http://localhost:{PORT}/discovery_maker.html')
http.server.HTTPServer(('', PORT), Handler).serve_forever()
