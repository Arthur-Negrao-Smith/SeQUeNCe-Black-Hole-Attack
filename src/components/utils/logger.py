import logging
import sys

class Logger():

    _instance = None

    def __new__(cls, name):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, name: str):
        if self._initialized:
            return
        
        log_format: str = "%(filename)s - %(levelname)s - %(message)s"
        self.formatter: logging.Formatter = logging.Formatter(log_format)
        
        self.root_log: logging.Logger = logging.getLogger(name)
        self.root_log.setLevel(logging.DEBUG)

        self.handler: logging.Handler = logging.StreamHandler(sys.stdout)
        self.handler.setFormatter(self.formatter)

        self.root_log.addHandler(self.handler)

        self.disable()

        self._initialized = True

    def set_log_level(self, log_level: int) -> None:
        self.log_level = log_level
        self.root_log.setLevel(self.log_level)

    def disable(self) -> None:
        """
        Disable logger
        """
        logging.disable(logging.CRITICAL)

    def enable(self, log_level: int = logging.DEBUG) -> None:
        """
        Enable logger
        """
        logging.disable(logging.NOTSET)
        self.handler.setLevel(log_level)
        
    def warning(self, text: str) -> None:
        """
        Create a warning message
        """
        self.root_log.warning(text)

    def log(self, text: str) -> None:
        """
        Create a log message
        """
        self.root_log.log(logging.INFO, text)

    def debug(self, text: str) -> None:
        """
        Create a debug message
        """
        self.root_log.debug(text)

    def _setup_logger(self) -> None:
        _format: str = "%(filename)s - %(loglevel)s - %(message)s"
        formatter: logging.Formatter = logging.Formatter(_format)
        handler: logging.Handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self.root_log.addHandler(handler)
        self.root_log.setLevel(self.log_level)