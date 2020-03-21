# -*- coding: utf-8 -*-
# %matplotlib inline

import numpy as np
np.set_printoptions(suppress=True)

from shutil import copyfile
import random

from keras.utils import plot_model

from game import Game, GameState
from agent import Agent
from memory import Memory
from model import Residual_CNN
from funcs import playMatches, playMatchesBetweenVersions

import loggers as lg

import initialize
import pickle
import config

def setPlayer(player_version):
  game = Game()

  # create an untrained neural network objects from the config file
  player_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + game.grid_shape,   game.action_size, config.HIDDEN_CNN_LAYERS)

  #If loading an existing neural network, set the weights from that model
  print('LOADING MODEL VERSION ' + str(player_version) + '...')
  m_tmp = player_NN.read(game.name, player_version)
  player_NN.model.set_weights(m_tmp.get_weights())

  player = Agent('player', game.state_size, game.action_size, config.MCTS_SIMS, config.CPUCT, player_NN)
  return player

def makeMove(gameboard, NAOpiece, player):
  np_gameboard = np.array([gameboard[int(i/7)][i%7] for i in range(42)])
  gs = GameState(np_gameboard, NAOpiece)
  
  # _, preds, moves = player.get_preds(gs)
  # best_move = 0

  # for move in moves:
  #   best_move = move if preds[move] > preds[best_move] else best_move

  # return int(best_move/7), best_move % 7

  action, pi, _, _ = player.act(gs, 0)
  str_pi = ""

  for y in range (6):
      for x in range (7):
          str_pi += "%.4f" % pi[x+y*7] + " "
      str_pi += "\n"

  print(str_pi)

  return int(action/7), action % 7

"""
Training
"""

def updateInitFile(memory_version, model_version):
    init_file = open("./initialize.py", "wb")
    init_info = 'INITIAL_MEMORY_VERSION = %i\nINITIAL_MODEL_VERSION = %i' % (memory_version, model_version)
    init_file.write(init_info)
    init_file.close()

#---------------------

#Training continues until running out of configured memory
def startTraining():
  lg.logger_main.info('=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*')
  lg.logger_main.info('=*=*=*=*=*=.      NEW LOG      =*=*=*=*=*')
  lg.logger_main.info('=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*')

  env = Game()

  ######## LOAD MEMORIES IF NECESSARY ########

  if initialize.INITIAL_MEMORY_VERSION == None:
    memory = Memory(config.MEMORY_SIZE)
  else:
    print('LOADING MEMORY VERSION ' + str(initialize.INITIAL_MEMORY_VERSION) + '...')
    memory_pickle = open(config.RUN_FOLDER + env.name + "/memory/memory" + str(initialize.INITIAL_MEMORY_VERSION).zfill(4) + ".p", "rb")
    memory = pickle.load(memory_pickle)
    memory_pickle.close()

    #copy the past run's config if continuing from previous run
    copyfile(config.RUN_FOLDER + env.name + '/config.py', './config.py')

  ######## LOAD MODEL IF NECESSARY ########

  # create an untrained neural network objects from the config file
  current_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + env.grid_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)
  best_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) +  env.grid_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)

  #If loading an existing neural network, set the weights from that model
  if initialize.INITIAL_MODEL_VERSION != None and initialize.INITIAL_MODEL_VERSION != 0:
    best_player_version  = initialize.INITIAL_MODEL_VERSION
    print('LOADING MODEL VERSION ' + str(initialize.INITIAL_MODEL_VERSION) + '...')
    m_tmp = best_NN.read(env.name, best_player_version)
    current_NN.model.set_weights(m_tmp.get_weights())
    best_NN.model.set_weights(m_tmp.get_weights())

  #otherwise just ensure the weights on the two players are the same
  else:
    best_player_version = 0
    best_NN.model.set_weights(current_NN.model.get_weights())

  #copy the config file to the run folder
  copyfile('./config.py', config.RUN_FOLDER + env.name + '/config.py')
  plot_model(current_NN.model, to_file=config.RUN_FOLDER + env.name + '/models/model.png', show_shapes = True)

  print('\n')

  ######## CREATE THE PLAYERS ########

  current_player = Agent('current_player', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, current_NN)
  best_player = Agent('best_player', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, best_NN)
  #user_player = User('player1', env.state_size, env.action_size)
  iteration = 0

  while 1:

    iteration += 1
    reload(lg)
    reload(config)

    print('ITERATION NUMBER ' + str(iteration))

    lg.logger_main.info('BEST PLAYER VERSION: %d', best_player_version)
    print('BEST PLAYER VERSION ' + str(best_player_version))

    ######## SELF PLAY ########
    print('SELF PLAYING ' + str(config.EPISODES) + ' EPISODES...')
    _, memory, _, _ = playMatches(best_player, best_player, config.EPISODES, lg.logger_main, 
                                    turns_until_tau0 = config.TURNS_UNTIL_TAU0, memory = memory)
    print('\n')

    memory.clear_stmemory()

    if len(memory.ltmemory) >= config.MEMORY_SIZE:
      print("Ending Training (Reached Full Memory)")
      break

    if len(memory.ltmemory) >= config.MEMORY_BEFORE_TRAINING:

      ######## RETRAINING ########
      print('RETRAINING...')
      current_player.replay(memory.ltmemory)
      print('')

      lg.logger_memory.info('====================')
      lg.logger_memory.info('NEW MEMORIES')
      lg.logger_memory.info('====================')
      
      memory_samp = random.sample(memory.ltmemory, min(1000, len(memory.ltmemory)))
      
      for s in memory_samp:
        current_value, current_probs, _ = current_player.get_preds(s['state'])
        best_value, best_probs, _ = best_player.get_preds(s['state'])

        lg.logger_memory.info('MCTS VALUE FOR %s: %f', s['playerTurn'], s['value'])
        lg.logger_memory.info('CUR PRED VALUE FOR %s: %f', s['playerTurn'], current_value)
        lg.logger_memory.info('BES PRED VALUE FOR %s: %f', s['playerTurn'], best_value)
        lg.logger_memory.info('THE MCTS ACTION VALUES: %s', ['%.2f' % elem for elem in s['AV']]  )
        lg.logger_memory.info('CUR PRED ACTION VALUES: %s', ['%.2f' % elem for elem in  current_probs])
        lg.logger_memory.info('BES PRED ACTION VALUES: %s', ['%.2f' % elem for elem in  best_probs])
        lg.logger_memory.info('ID: %s', s['state'].id)
        lg.logger_memory.info('INPUT TO MODEL: %s', current_player.model.convertToModelInput(s['state']))

        s['state'].render(lg.logger_memory)
          
      ######## TOURNAMENT ########
      print('TOURNAMENT...')
      scores, _, points, sp_scores = playMatches(best_player, current_player, config.EVAL_EPISODES, lg.logger_tourney,                                                                    turns_until_tau0 = 0, memory = None)
      print('\nSCORES')
      print(scores)
      print('\nSTARTING PLAYER / NON-STARTING PLAYER SCORES')
      print(sp_scores)
      #print(points)

      print('\n\n')

      if scores['current_player'] > scores['best_player'] * config.SCORING_THRESHOLD:
        best_player_version += 1
        best_NN.model.set_weights(current_NN.model.get_weights())
        best_NN.write(env.name, best_player_version)
    
    else:
      print('MEMORY BEFORE INITIATING TRAINING: ' + str(len(memory.ltmemory)) + "/" + str(config.MEMORY_BEFORE_TRAINING))
      
    print('TOTAL MEMORY SIZE: ' + str(len(memory.ltmemory)) + "/" + str(config.MEMORY_SIZE)) 
    
    memory_pickle = open(config.RUN_FOLDER + env.name + "/memory/memory" + str(iteration).zfill(4) + ".p", "wb" )
    pickle.dump(memory, memory_pickle)
    memory_pickle.close()
    updateInitFile(iteration, best_player_version)