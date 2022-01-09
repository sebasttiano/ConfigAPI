""" Collection of decorators"""

import logging
import hashlib
from functools import wraps
from flask import request, abort
from settings import config


logger = logging.getLogger('CApi')


def auth(func):
    """Check authorization"""
    @wraps(func)
    def decorated(*args, **kwargs):
        requisites = request.authorization
        if not auth or not _verify_password(requisites.username, requisites.password):
            return abort(401)
        return func(*args, **kwargs)
    return decorated


def _verify_password(username: str, password: str) -> bool:
    """
    Handler for basic HTTP auth.
    Args:
        username: user's login
        password: user's password
    Returns:
        HTTP response with json
    """

    pass_hash = hashlib.sha512(password.encode('utf-8')).hexdigest()
    try:
        good_pass = config.get("Users", username)
        if good_pass == pass_hash:
            return True
        logger.error(f"Attempting to login with an invalid {username=} or {password=}")
        return False
    except AttributeError as err:
        logger.error(f"Bad auth\n{err}")
        return False


class CheckExceptions:  # pylint: disable=too-few-public-methods
    """
    Try to exec the main functions,
    stop the program execution if except
    """

    def __init__(self, exceptions_tuple):
        self.exceptions_tuple = exceptions_tuple

    def __call__(self, func_to_decorate):

        def func_wrapper(*args, **kwargs):  # pylint: disable=inconsistent-return-statements
            """
            Try to call the function.
            Catch the exceptions. Log it.
            """

            logger.info(f"Start of exec {func_to_decorate.__name__}")
            try:
                checker = func_to_decorate(*args, **kwargs)

            except self.exceptions_tuple as func_error:
                if func_to_decorate.__name__ == "init_db":
                    logger.error(f"Couldn't initialize test data."
                                 f"Perhaps they have already been initialized.\n"
                                 f"The error that occured: {func_error}")
                else:
                    logger.error(type(func_error).__name__ + ': ' + str(func_error))
            else:
                logger.info(f"End of exec {func_to_decorate.__name__}")
                return checker

        return func_wrapper
