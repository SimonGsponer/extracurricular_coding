import logging
from pathlib import Path

def initialize_logger():
    logger_fp = Path("logs/logging_info.json")

    logger = logging.getLogger("uuid-4-experiment-logger")
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(logger_fp)

    formatter = logging.Formatter('{"timestamp": "%(asctime)s", "name": "%(name)s", "levelname": "%(levelname)s", "message": "%(message)s"}')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

def main():

    logger = initialize_logger()

    for i in range(5):
        logger.info('creating an instance of auxiliary_module.Auxiliary')

if __name__ == '__main__':
    main()
