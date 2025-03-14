import os
from flask import current_app

def handle_logger(message: str, type_logger: str = 'error'):
    """
    Logs messages in Flask's logger, but only in non-production environments.

    Parameters:
    - message (str): The message to log.
    - type_logger (str): The type of log ('error', 'warning' or 'info'). Default is 'error'.
    """
    environment = os.getenv('FLASK_ENV', 'dev').lower()

    # Skip logging in production
    if environment == 'prod':
        return

    log_levels = {
        'error': current_app.logger.error,
        'info': current_app.logger.info,
        'warning': current_app.logger.warning
    }

    log_function = log_levels.get(type_logger, current_app.logger.warning)
    log_function(message)
