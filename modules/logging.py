import logging
import coloredlogs

def setup_logging(name=__name__):
    """Configure colored logging with custom settings"""
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    fmt = '%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'
    coloredlogs.install(
        logger=logger,
        fmt=fmt,
        datefmt='%H:%M:%S',
        field_styles={
            'asctime': {'color': 'green'},
            'name': {'color': 'blue', 'bold': True},
            'process': {'color': 'yellow'},
            'levelname': {'color': 'black', 'bold': True},
            'message': {'color': 'white'}
        },
        level_styles={
            'debug': {'color': 'cyan'},
            'info': {'color': 'green'},
            'warning': {'color': 'yellow'},
            'error': {'color': 'red'},
            'critical': {'color': 'red', 'bold': True, 'background': 'white'}
        }
    )
    
    return logger