log_config = {
    "version": 1,
    "formatters": {
        "format_for_file": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": '%d/%m/%Y %H:%M:%S'
        },
        "format_for_console": {
            "format": "%(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "avia_file_handler": {
            "class": "logging.FileHandler",
            "formatter": "format_for_file",
            "filename": "avia_bot.log",
            "encoding": "UTF-8",
            "level": "DEBUG",
        },
        "stream_handler": {
            "class": "logging.StreamHandler",
            "formatter": "format_for_file",
            "level": "INFO",
        },
    },
    "loggers": {
        "avia_bot": {
            "handlers": ["avia_file_handler", "stream_handler"],
            "level": "DEBUG",
        },
    },
}