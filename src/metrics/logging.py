import json
import logging
import sys
import traceback
from time import time
from types import TracebackType

from utils.secrets import SecretsMasker
from variables import PRIVATE_ENV_VARS


class JsonFormatter(logging.Formatter):
    def __init__(self, masker: SecretsMasker | None = None):
        super().__init__()
        self._masker = masker

    def format(self, record: logging.LogRecord) -> str:
        message = record.msg if isinstance(record.msg, dict) else {'msg': record.getMessage()}

        to_json_msg = json.dumps(
            {
                'name': record.name,
                'levelname': record.levelname,
                'funcName': record.funcName,
                'lineno': record.lineno,
                'module': record.module,
                'pathname': record.pathname,
                'timestamp': int(time()),
                **message,
            }
        )
        # Secrets are hidden in every log line, including messages from third-party libraries.
        return self._masker.mask(to_json_msg) if self._masker else to_json_msg


def log_unhandled_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    """Send the traceback of an unhandled exception through the logger, so that it is formatted and masked too."""
    error = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.getLogger('unhandled').critical({'msg': 'Unhandled exception. Shut down.', 'error': error})


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter(SecretsMasker(PRIVATE_ENV_VARS)))

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
)
sys.excepthook = log_unhandled_exception
