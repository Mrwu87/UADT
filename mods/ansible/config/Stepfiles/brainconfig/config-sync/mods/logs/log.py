import logging
from logging.handlers import TimedRotatingFileHandler
# Setup a log formatter
formatter = logging.Formatter(
    "%(asctime)12s - '%(filename)12s' - [line:%(lineno)4d] - %(levelname).4s : %(message)s")
# Setup a log file handler and set level/formater

# logFile = TimedRotatingFileHandler(filename='mods/logs/config/runtime' , when='D', interval=1, backupCount=30)
# logFile.suffix = '%Y%m%d.log'
logFile = TimedRotatingFileHandler(filename='UADT/mods/logs/config/runtime')

logFile.setFormatter(formatter)

# logFile = logging.FileHandler("%s/logs/%s.log" % (os.getenv('PYTHONENV'),datetime.now().strftime("%Y%m%d-%H%M%S")))
# logFile.setFormatter(formatter)

# Setup a log console handler and set level/formater
logConsole = logging.StreamHandler()
logConsole.setFormatter(formatter)
# Setup a logger

service_logger = logging.getLogger('service')
service_logger.setLevel(logging.INFO)
service_logger.addHandler(logFile)
#service_logger.addHandler(logConsole)
