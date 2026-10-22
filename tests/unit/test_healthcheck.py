from datetime import datetime, timedelta

import pytest
import requests
from metrics import healthcheck
from metrics.healthcheck import start_pulse_server

pytestmark = pytest.mark.unit


@pytest.fixture
def server():
    server = start_pulse_server('127.0.0.1', 0)
    yield server
    server.shutdown()
    server.server_close()


def url(server, path):
    host, port = server.server_address[:2]
    return f'http://{host}:{port}{path}'


def test_pulse_server_binds_to_the_given_host(server, monkeypatch):
    monkeypatch.setattr(healthcheck, '_last_pulse', datetime.now())

    response = requests.get(url(server, '/healthcheck'), timeout=5)

    assert server.server_address[0] == '127.0.0.1'
    assert response.status_code == 200
    assert response.json() == {'metrics': 'ok', 'reason': 'ok'}


def test_healthcheck_fails_without_pulse_for_ten_minutes(server, monkeypatch):
    monkeypatch.setattr(healthcheck, '_last_pulse', datetime.now() - timedelta(minutes=11))

    response = requests.get(url(server, '/healthcheck'), timeout=5)

    assert response.status_code == 503
    assert response.json()['metrics'] == 'fail'


def test_pulse_refreshes_the_healthcheck(server, monkeypatch):
    monkeypatch.setattr(healthcheck, '_last_pulse', datetime.now() - timedelta(minutes=11))

    requests.get(url(server, '/pulse/'), timeout=5)
    response = requests.get(url(server, '/healthcheck'), timeout=5)

    assert response.status_code == 200


def test_server_does_not_serve_files(server, monkeypatch):
    monkeypatch.setattr(healthcheck, '_last_pulse', datetime.now())

    response = requests.head(url(server, '/main.py'), timeout=5)

    assert response.status_code == 501
