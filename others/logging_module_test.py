import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s '
    'thread: %(threadName)s output msg: %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    # filename='./myapp.log',
    # filemode='w'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("this is a info log")
    logger.info("this is a info log 2")
