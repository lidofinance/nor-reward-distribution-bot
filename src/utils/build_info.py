import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Written by the Dockerfile from the BUILD_VERSION, BUILD_BRANCH and BUILD_COMMIT build args (/app/build-info.json in the image).
BUILD_INFO_PATH = Path(__file__).resolve().parents[2] / 'build-info.json'
BUILD_INFO_KEYS: tuple[str, ...] = ('version', 'branch', 'commit', 'buildTime')
UNKNOWN = 'unknown'


def load_build_info(path: Path = BUILD_INFO_PATH) -> dict[str, str]:
    """Return version, branch, commit and buildTime of this build. Missing or unreadable values are 'unknown'."""
    info = dict.fromkeys(BUILD_INFO_KEYS, UNKNOWN)

    try:
        with open(path) as file:
            data = json.load(file)
    except FileNotFoundError:
        return info
    except (OSError, ValueError) as error:
        logger.warning({'msg': 'Failed to read build info.', 'path': str(path), 'error': str(error)})
        return info

    if not isinstance(data, dict):
        logger.warning({'msg': 'Build info is not a JSON object.', 'path': str(path)})
        return info

    for key in BUILD_INFO_KEYS:
        value = data.get(key)
        if value:
            info[key] = str(value)

    return info
