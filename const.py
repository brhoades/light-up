#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Constants File
#  This file holds various constants used to communicate between functions.

#Graph type
class gt:
    NOTHING = 0                               # No idea when this would be used
    UNLIT = 1                                 # Unlit tile, default state
    LIT = 2                                   # This is a lit tile, lit by a bulb
    BULB = 3                                  # This is a bulb
    BLACK_THRESHOLD = 9                       # Threshold for where all black squares begin afterwards
    TRANSFORM = 10                            # What we add to data graph's black value to get our constant
    BLACK0 = 10                               # A black square that cannot be bordered by a light
    BLACK1 = 11                               # A black square that must be bordered by 1 light
    BLACK2 = 12                               # A black square that must be bordered by 2 lights
    BLACK3 = 13                               # A black square that must be bordered by 3 lights
    BLACK4 = 14                               # A black square that must be bordered by 4 lights
    BLACK = 15                                # A black square that just blocks light
    MAX = 16
    
    lookup = [NOTHING, UNLIT, LIT, BULB, BLACK_THRESHOLD, BLACK0, BLACK1, \
                BLACK2, BLACK3, BLACK4, BLACK]
    placeable = [BLACK0, BLACK1, BLACK2, BLACK3, BLACK4, BLACK]
                    
    ###
    OWNER = 0
    TYPE = 1

#Symbol lookup table
class sym:
    tb = []
    for i in range(0,gt.BLACK+1):
        tb.append("?")
    tb[gt.NOTHING] = "?"
    tb[gt.UNLIT] = " "
    tb[gt.LIT] = "█"
    tb[gt.BULB] = "B"
    tb[gt.BLACK0] = "0"
    tb[gt.BLACK1] = "1"
    tb[gt.BLACK2] = "2"
    tb[gt.BLACK3] = "3"
    tb[gt.BLACK4] = "4"
    tb[gt.BLACK] = "X"

#Operator Types / Parameter Types
class opp:
    #Survival Strategy Types
    COMMA = "0"
    PLUS = "1"
    
    #Initialization Types
    VALIDITY_ENFORCED_PLUS_UNIFORM_RANDOM = "0"
    UNIFORM_RANDOM = "1"
    
    #Parent Selection Types
    TOURNAMENT_WITH_REPLACEMENT = "0"
    #FITNESS_PROPORTIONAL= 1 Shared
    #UNIFORM_RANDOM = 2 Shared
    
    #Mutation Types
    #Currently not needed
    
    #Survival Selection Types
    TOURNAMENT_WITHOUT_REPLACEMENT = "0"
    #FITNESS_PROPORTIONAL = 1 Shared
    #UNIFORM_RANDOM = 2 Shared
    TRUNCATION = "3"
    
    #Termination Criteria Types
    FITNESS_EVALUATION_LIMIT = "0"
    GENERATIONAL_LIMIT = "1"
    CONVERGENCE = "2"
    
    #Fitness Type
    PENALTY_FUNCTION = 1
    VALIDITY_ENFORCED = 0
    
    #######MULTIPLE OPERATORS#######
    FITNESS_PROPORTIONAL = "1"
    UNIFORM_RANDOM = "2"
    
    ##Fitness Proportional Parameters
    REMOVAL = "0"
    IGNORE = "1"

#Configuration Indicies
class ci:
    GRAPH = 'graph'
    #####Graph Parameters#####
    GENERATE = 'gen'
    SEED = 'seed'
    BLACK0 = 'black0'
    BLACK1 = 'black1'
    BLACK2 = 'black2'
    BLACK3 = 'black3'
    BLACK4 = 'black4'
    BLACK = 'black'
    X = 'x'
    Y = 'y'
    
    POP = 'pop'
    #####Population Parameters#####
    MU = 'mu'
    LAMBDA = 'lambda'
    
    INIT = 'init'
    #####Initilization Parameters#####
    #TYPE = 'type' sharedx50
    
    PARENT_SEL = 'parsel'
    #####Parent Selection Parameters#####
    #TYPE = 'type' sharedx50
    #K = 'k' shared
    #FITNESS_PROPORTIONAL_TYPE = 'fitpro' shared
    
    MUTATE = 'mute'
    #####Mutate Parameters#####
    #TYPE = 'type' sharedx50
    ALPHA = 'alpha'
    
    SURVIVAL_SEL = 'surv'
    #####Parent Selection Parameters#####
    #TYPE = 'type' sharedx50
    #K ='k' shared
    #TRUNCATION_TYPE = 'trunc'
    #FITNESS_PROPORTIONAL_TYPE = 'fitpro' shared
    
    TERMINATION = 'term'
    #####Termination Criteria Selection#####
    #TYPE = 'type' sharedx50
    EVALUATION_LIMIT = 'evals'
    GENERATION_LIMIT = 'gens'
    TURNS_NO_CHANGE = 'homogenity'
    STOP_ON_BEST = 'stopbest'
    
    LOG = 'log'
    #####Log Parameters#####
    RESULT_LOG_FILE = 'result'
    SOLUTION_LOG_FILE = 'solution'
    GIT_LOG_HEADERS = 'logh'
    
    MAIN = 'main'
    #####Main Parameters#####
    SURVIVAL_STRATEGY = 'strat'
    TOTAL_RUNS = 'runs'
    IGNORE_BLACK_TILES = 'ignoreblack'
    
    FITNESS_TYPE = 'fittype'
    
    BAD_LIGHT_PENALTY = 'blight'
    OVERSAT_BLACK_PENALTY = 'osatb'
    UNDERSAT_BLACK_PENALTY = 'usatb'
    
    #####Shared Indicies#####
    TYPE = 'type'
    K = 'k'
    FITNESS_PROPORTIONAL_TYPE = 'fitpro'
