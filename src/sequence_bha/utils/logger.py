import logging

def show_logs():
    """
    Show all logs and formats them
    """
    logging.basicConfig(level=logging.DEBUG, format='%(filename)s - %(levelname)s - %(message)s')