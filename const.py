#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

#Constants

#Graph type constants
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
    
    lookup = [NOTHING, UNLIT, LIT, BULB, TRANSFORM, BLACK0, BLACK1, \
                BLACK2, BLACK3, BLACK4, BLACK]
    
    ###
    OWNER = 0
    TYPE = 1
    
#Light placement return values
class lprets:
    BAD = 0
    LIT = 1
    YALIT = 2
    STOPPED = 3
    OFFSET = 5

#symbols
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

class solv:
    DONE = 1
    BEST = 2                     
    NOFIN = 3
    
class method:
    MINBULB = 0
    MAXBULB = 1
    ANY = 2

#Log handle indecies
class lh:
    RES = 0
    SOL = 1
