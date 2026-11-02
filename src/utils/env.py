import os
from typing import Literal, overload


@overload
def from_file_or_env(env_name: str, required: Literal[True]) -> str: ...


@overload
def from_file_or_env(env_name: str, required: bool = False) -> str | None: ...


def from_file_or_env(env_name: str, required: bool = False) -> str | None:
    """Return the value of `<env_name>_FILE` (the content of that file) or, when it is not set, of `env_name`.

    The file form is for secrets mounted by the platform (one secret per file). The file is read once, when this
    function is called at startup, so a changed secret takes effect only after a restart: the bot must not change
    its key or its RPC endpoints in the middle of a cycle. Trailing whitespace of the file is dropped; an empty
    file gives an empty string, which the caller treats like an unset variable.
    """
    filepath_env = f'{env_name}_FILE'
    filepath = os.getenv(filepath_env)

    if filepath:
        try:
            with open(filepath, encoding='utf-8') as file:
                return file.read().rstrip()
        except OSError as error:
            raise ValueError(f'{filepath_env} points to a file that cannot be read: {error}. Fix or remove the variable.') from error
        except UnicodeDecodeError as error:
            # No details from the decoder: they would quote bytes of the secret.
            raise ValueError(f'{filepath_env} points to a file that is not UTF-8 text. Fix or remove the variable.') from error

    value = os.getenv(env_name)
    if value is None and required:
        raise ValueError(f'{env_name} or {filepath_env} must be set.')

    return value
