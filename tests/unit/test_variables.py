import json

import pytest
import variables

pytestmark = pytest.mark.unit


def test_env_vars_for_log_masks_secrets(monkeypatch):
    monkeypatch.setattr(
        variables,
        'PRIVATE_ENV_VARS',
        {
            'WEB3_RPC_ENDPOINTS': ['https://rpc.example/v3/secret-key-1', 'https://rpc.example/v3/secret-key-2'],
            'WALLET_PRIVATE_KEY': '0x' + '1' * 64,
        },
    )

    logged = variables.env_vars_for_log()

    assert logged['WEB3_RPC_ENDPOINTS'] == [variables.MASKED_VALUE, variables.MASKED_VALUE]
    assert logged['WALLET_PRIVATE_KEY'] == variables.MASKED_VALUE
    assert 'secret-key' not in json.dumps(logged)
    assert '1' * 64 not in json.dumps(logged)


def test_env_vars_for_log_keeps_public_values_and_empty_secrets(monkeypatch):
    monkeypatch.setattr(variables, 'PRIVATE_ENV_VARS', {'WALLET_PRIVATE_KEY': None})

    logged = variables.env_vars_for_log()

    assert logged['WALLET_PRIVATE_KEY'] == ''
    for key, value in variables.PUBLIC_ENV_VARS.items():
        assert logged[key] == value
