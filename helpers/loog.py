import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime, timezone
from helpers.config import AppConfig

config = AppConfig()

class CustomFormatter(logging.Formatter):
    def formatLevel(self, record):
        # Convert levelname to lowercase
        record.levelname = record.levelname.lower()
        return super().format(record)
    
    def format(self, record):
        log = {
            'level': record.levelname.lower(),
            'time': self.formatTime(record),
        }

        if isinstance(record.msg, dict):
            log.update(record.msg)
        else:
            log['message'] = record.getMessage()

        return json.dumps(log, ensure_ascii=False)

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
def create_log_directory():
    import os
    log_dir = '/var/log/yang-genai-chat-ui'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        os.chmod(log_dir, 0o755)

def setup_logging():
    logger = logging.getLogger('yang-genai-chat-ui')
    logger.setLevel(logging.INFO)
    formatter = CustomFormatter(json.dumps({'level': '%(levelname)s', 'msg': '%(message)s', 'time': '%(asctime)s'}))
    handler = RotatingFileHandler('/var/log/yang-genai-chat-ui/app.log', maxBytes=int(float(config.log_max_size)), backupCount=int(float(config.log_max_backups)))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# setup logging for script
create_log_directory()
setup_logging()
logger = logging.getLogger('yang-genai-chat-ui')