import logging
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

logger = logging.getLogger(__name__)


_last_pulse = datetime.now()


def pulse(port: int):
    try:
        requests.get(f'http://localhost:{port}/pulse/', timeout=10)
    except requests.exceptions.ConnectionError as error:
        logger.warning({'msg': 'Healthcheck server is not responding.', 'error': str(error)})


class PulseRequestHandler(BaseHTTPRequestHandler):
    # Seconds to wait for a client to send its request. Without it a stalled client holds the connection forever.
    timeout = 5

    def do_GET(self):
        global _last_pulse

        if self.path == '/pulse/':
            _last_pulse = datetime.now()

        # timedelta should be higher than one epoch
        if datetime.now() - _last_pulse > timedelta(minutes=10):
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b'{"metrics": "fail", "reason": "timeout exceeded"}\n')
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"metrics": "ok", "reason": "ok"}\n')

    def log_request(self, *args, **kwargs):
        # Disable non-error logs
        pass


def start_pulse_server(host: str, port: int) -> ThreadingHTTPServer:
    """Serve the health check on host:port in a daemon thread. The host must accept loopback connections for pulse()."""
    server = ThreadingHTTPServer(
        (host, port),
        RequestHandlerClass=PulseRequestHandler,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
