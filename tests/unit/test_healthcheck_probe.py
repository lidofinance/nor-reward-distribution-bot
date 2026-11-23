import socket
from datetime import datetime, timedelta

import healthcheck as probe_script
import pytest
from metrics import healthcheck
from metrics.healthcheck import start_pulse_server

pytestmark = pytest.mark.unit


@pytest.fixture
def server():
    server = start_pulse_server('127.0.0.1', 0)
    yield server
    server.shutdown()
    server.server_close()


def url(server):
    host, port = server.server_address[:2]
    return f'http://{host}:{port}/healthcheck'


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def test_probe_passes_while_the_bot_pulses(server, monkeypatch):
    monkeypatch.setattr(healthcheck, '_last_pulse', datetime.now())

    assert probe_script.probe(url(server)) == 0


def test_probe_fails_without_pulse_for_ten_minutes(server, monkeypatch, capsys):
    monkeypatch.setattr(healthcheck, '_last_pulse', datetime.now() - timedelta(minutes=11))

    assert probe_script.probe(url(server)) == 1
    assert '503' in capsys.readouterr().err


def test_probe_fails_when_nothing_listens(capsys):
    assert probe_script.probe(f'http://127.0.0.1:{free_port()}/healthcheck') == 1
    assert 'Healthcheck failed' in capsys.readouterr().err


def test_main_probes_the_port_from_the_environment(server, monkeypatch):
    monkeypatch.setattr(healthcheck, '_last_pulse', datetime.now())
    monkeypatch.setenv('HEALTHCHECK_SERVER_PORT', str(server.server_address[1]))

    assert probe_script.main() == 0


def test_main_probes_the_default_port_without_the_variable(monkeypatch):
    monkeypatch.delenv('HEALTHCHECK_SERVER_PORT', raising=False)
    monkeypatch.setattr(probe_script, 'probe', lambda url: url)

    assert probe_script.main() == 'http://localhost:9010/healthcheck'


def test_main_fails_on_a_port_without_the_server(monkeypatch):
    monkeypatch.setenv('HEALTHCHECK_SERVER_PORT', str(free_port()))

    assert probe_script.main() == 1
