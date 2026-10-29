import logging

from logmask import setup_logging
from variables import PRIVATE_ENV_VARS

# JSON lines to stderr. Every line is masked with every form of the private values, including the messages of
# third-party libraries, warnings and the traceback of an unhandled exception (sys, threading and unraisable hooks).
setup_logging(PRIVATE_ENV_VARS, level=logging.INFO)
