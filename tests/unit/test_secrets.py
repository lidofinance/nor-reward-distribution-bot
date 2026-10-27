import io
import json
import logging

import pytest
from metrics.logging import JsonFormatter, log_unhandled_exception
from utils.secrets import MASKED_VALUE, SecretsMasker, secret_values

pytestmark = pytest.mark.unit

KEY = '0x' + 'ab' * 32
RPC = 'https://rpc.example/v3/secret-key-1/'
SECRETS = {
    'WEB3_RPC_ENDPOINTS': [RPC, 'https://rpc.example/v3/secret-key-2'],
    'WALLET_PRIVATE_KEY': KEY,
}


def record(msg) -> logging.LogRecord:
    return logging.LogRecord('test', logging.INFO, __file__, 1, msg, None, None)


def test_secret_values_cover_list_items_and_url_without_trailing_slash():
    values = secret_values(SECRETS)

    assert KEY in values
    assert RPC in values
    assert RPC.rstrip('/') in values
    assert 'https://rpc.example/v3/secret-key-2' in values


def test_secret_values_cover_url_path_query_and_password():
    values = secret_values(
        {
            'A': 'https://rpc.example/v3/secret-key-1/',
            'B': 'https://rpc.example/eth?apikey=secret-key-2',
            'C': 'https://user:secret-pass-3@rpc.example/',
        }
    )

    assert '/v3/secret-key-1/' in values
    assert '/v3/secret-key-1' in values
    assert 'apikey=secret-key-2' in values
    assert 'secret-pass-3' in values
    assert '/eth' not in values


def test_masker_hides_url_path_logged_without_the_host():
    error = "HTTPSConnectionPool(host='rpc.example', port=443): Max retries exceeded with url: /v3/secret-key-1/"

    assert 'secret-key' not in SecretsMasker(SECRETS).mask(error)


def test_short_and_empty_values_are_not_masked():
    assert secret_values({'A': '', 'B': None, 'C': 'short', 'D': ['x'], 'E': 42}) == []


def test_masker_hides_secrets_inside_text():
    text = f'HTTPConnectionPool(host={RPC.rstrip("/")}): error; key={KEY}'

    masked = SecretsMasker(SECRETS).mask(text)

    assert 'secret-key' not in masked
    assert KEY not in masked
    assert masked.count(MASKED_VALUE) == 2


def test_json_formatter_masks_secrets_in_dict_and_string_messages():
    formatter = JsonFormatter(SecretsMasker(SECRETS))

    for msg in ({'msg': 'Failed.', 'error': f'cannot reach {RPC}'}, f'Failed to reach {RPC}'):
        line = formatter.format(record(msg))

        assert 'secret-key' not in line
        assert MASKED_VALUE in line
        json.loads(line)


def test_json_formatter_masks_json_escaped_secret():
    secret = 'pass"word/with/quote'
    formatter = JsonFormatter(SecretsMasker({'TOKEN': secret}))

    line = formatter.format(record({'msg': secret}))

    assert 'word/with/quote' not in line
    assert json.loads(line)['msg'] == MASKED_VALUE


def test_unhandled_exception_goes_through_the_masked_logger():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter(SecretsMasker(SECRETS)))
    unhandled = logging.getLogger('unhandled')
    unhandled.addHandler(handler)
    unhandled.propagate = False
    try:
        try:
            raise ConnectionError(f'Max retries exceeded with url: {RPC}')
        except ConnectionError as error:
            log_unhandled_exception(type(error), error, error.__traceback__)
    finally:
        unhandled.removeHandler(handler)
        unhandled.propagate = True

    line = json.loads(stream.getvalue())

    assert line['levelname'] == 'CRITICAL'
    assert 'Traceback' in line['error']
    assert 'secret-key' not in line['error']


def test_json_formatter_without_masker_keeps_the_text():
    line = JsonFormatter().format(record({'msg': RPC}))

    assert json.loads(line)['msg'] == RPC
