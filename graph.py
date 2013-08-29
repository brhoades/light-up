#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import const

#Graph class
class graph:
    def __init_( self, x, y )
        data = []
        for i in range(x)
            data[i] = []
            for j in range(y)
                data[i][j] = const.UNLIT
                
        #Have we made a bad placement?
        self.bad = false
        #Is this an invalid graph?
        self.invalid = false
        #How many lights have been placed
        self.lights=0
        #How many squares are lit
        self.litsq=0
        #X Size
        self.x = x
        #Y size
        self.y = y
        #Fitness
        self.fit=-1
        
        #Array coords
        self.data = data