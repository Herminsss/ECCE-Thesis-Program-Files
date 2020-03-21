
from utils import setup_logger
import config

### SET all LOGGER_DISABLED to True to disable logging
### WARNING: the mcts log file gets big quite quickly

LOGGER_DISABLED = {
                    'main': True, 
                    'memory': True, 
                    'tourney': True, 
                    'mcts': True, 
                    'model': True
                  }

logger_mcts = setup_logger('logger_mcts', config.RUN_FOLDER + 'connect4/logs/logger_mcts.log')
logger_mcts.disabled = LOGGER_DISABLED['mcts']

logger_main = setup_logger('logger_main', config.RUN_FOLDER + 'connect4/logs/logger_main.log')
logger_main.disabled = LOGGER_DISABLED['main']

logger_tourney = setup_logger('logger_tourney', config.RUN_FOLDER + 'connect4/logs/logger_tourney.log')
logger_tourney.disabled = LOGGER_DISABLED['tourney']

logger_memory = setup_logger('logger_memory', config.RUN_FOLDER + 'connect4/logs/logger_memory.log')
logger_memory.disabled = LOGGER_DISABLED['memory']

logger_model = setup_logger('logger_model', config.RUN_FOLDER + 'connect4/logs/logger_model.log')
logger_model.disabled = LOGGER_DISABLED['model']
 