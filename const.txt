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
    BLACK0 = 10                               # A black square that cannot be bordered by a light
    BLACK1 = 11                               # A black square that must be bordered by 1 light
    BLACK2 = 12                               # A black square that must be bordered by 2 lights
    BLACK3 = 13                               # A black square that must be bordered by 3 lights
    BLACK4 = 14                               # A black square that must be bordered by 4 lights