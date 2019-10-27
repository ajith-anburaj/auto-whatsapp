import logging.config
import yaml

with open('/Users/ajith.a/PycharmProjects/auto-whatsapp/config/logger.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger('dev')
