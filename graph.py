#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import gt
import fileinput

#Graph class
class graph:
    def __init__( self, conf ):
        self.data=[]
        self.x = int(conf['x'])
        self.y = int(conf['y'])
        
        for i in range(0,(self.x-1)):
            self.data.append([])
            for j in range(0,(self.y-1)):
                self.data[i].append(gt.UNLIT)
                
        #Have we made a bad placement?
        self.bad=False
        #Is this an invalid graph?
        self.invalid=False
        #How many lights have been placed
        self.lights=0
        #How many squares are lit
        self.litsq=0

        #Fitness
        self.fit=-1
