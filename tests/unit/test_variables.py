import importlib
import json

import pytest
import variables
from logmask import MASKED_VALUE

pytestmark = pytest.mark.unit

TEST_KEY = '0x' + '1' * 64


@pytest.fixture
def load_variables(monkeypatch):
    """Reload the variables module with extra env; the module is reloaded with the original env afterwards."""

    def load(**env):
        with monkeypatch.context() as mp:
            for name, value in env.items():
                if value is None:
                    mp.delenv(name, raising=False)
                else:
                    mp.setenv(name, value)
            return importlib.reload(variables)

    yield load
    importlib.reload(variables)


def test_private_key_from_file(load_variables, tmp_path):
    key_file = tmp_path / 'wallet-private-key'
    key_file.write_text(TEST_KEY + '\n')

    loaded = load_variables(WALLET_PRIVATE_KEY_FILE=str(key_file), WALLET_PRIVATE_KEY=None)

    assert loaded.WALLET_PRIVATE_KEY == TEST_KEY
    assert loaded.ACCOUNT is not None
    assert loaded.PUBLIC_ENV_VARS['ACCOUNT'] == loaded.ACCOUNT.address
    assert loaded.PUBLIC_ENV_VARS['WALLET_PRIVATE_KEY_FILE'] == str(key_file)


def test_empty_private_key_file_gives_dry_mode(load_variables, tmp_path):
    key_file = tmp_path / 'wallet-private-key'
    key_file.write_text('')

    loaded = load_variables(WALLET_PRIVATE_KEY_FILE=str(key_file), WALLET_PRIVATE_KEY=TEST_KEY)

    assert loaded.ACCOUNT is None
    assert loaded.PUBLIC_ENV_VARS['ACCOUNT'] == ''


def test_missing_private_key_file_fails_at_startup(load_variables, tmp_path):
    with pytest.raises(ValueError, match='WALLET_PRIVATE_KEY_FILE'):
        load_variables(WALLET_PRIVATE_KEY_FILE=str(tmp_path / 'missing'))


def test_rpc_endpoints_from_file(load_variables, tmp_path):
    rpc_file = tmp_path / 'web3-rpc-endpoints'
    rpc_file.write_text('https://rpc.example/one,https://rpc.example/two\n')

    loaded = load_variables(WEB3_RPC_ENDPOINTS_FILE=str(rpc_file), WEB3_RPC_ENDPOINTS='https://rpc.example/env')

    assert ['https://rpc.example/one', 'https://rpc.example/two'] == loaded.WEB3_RPC_ENDPOINTS


def test_rpc_endpoints_are_required(load_variables):
    with pytest.raises(ValueError, match='WEB3_RPC_ENDPOINTS or WEB3_RPC_ENDPOINTS_FILE'):
        load_variables(WEB3_RPC_ENDPOINTS=None, WEB3_RPC_ENDPOINTS_FILE=None)


def test_env_start_still_works(load_variables):
    loaded = load_variables(WALLET_PRIVATE_KEY=TEST_KEY, WEB3_RPC_ENDPOINTS='https://rpc.example/env', WALLET_PRIVATE_KEY_FILE=None)

    assert loaded.ACCOUNT is not None
    assert ['https://rpc.example/env'] == loaded.WEB3_RPC_ENDPOINTS
    assert loaded.PUBLIC_ENV_VARS['WALLET_PRIVATE_KEY_FILE'] == ''


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

    assert logged['WEB3_RPC_ENDPOINTS'] == [MASKED_VALUE, MASKED_VALUE]
    assert logged['WALLET_PRIVATE_KEY'] == MASKED_VALUE
    assert 'secret-key' not in json.dumps(logged)
    assert '1' * 64 not in json.dumps(logged)


def test_env_vars_for_log_keeps_public_values_and_empty_secrets(monkeypatch):
    monkeypatch.setattr(variables, 'PRIVATE_ENV_VARS', {'WALLET_PRIVATE_KEY': None})

    logged = variables.env_vars_for_log()

    assert logged['WALLET_PRIVATE_KEY'] == ''
    for key, value in variables.PUBLIC_ENV_VARS.items():
        assert logged[key] == value
