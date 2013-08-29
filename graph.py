#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import const
import fileinput

#Graph class
class graph:
    def __init__( self, x, y ):
        self.data=[]
        self.data.blank( x, y )
                
        #Have we made a bad placement?
        self.bad=false
        #Is this an invalid graph?
        self.invalid=false
        #How many lights have been placed
        self.lights=0
        #How many squares are lit
        self.litsq=0
        #X Size
        self.x=x
        #Y size
        self.y=y
        #Fitness
        self.fit=-1
    
    def __init__( self, filename ):
        self.data=[]
        #self.data.blank( x, y )
                
        #Have we made a bad placement?
        self.bad=false
        #Is this an invalid graph?
        self.invalid=false
        #How many lights have been placed
        self.lights=0
        #How many squares are lit
        self.litsq=0
        #X Size
        self.x=x
        #Y size
        self.y=y
        #Fitness
        self.fit=-1
      
    def blank(self, x, y):
        ret=[]
        for i in range(x):
            ret[i]=[]
            for j in range(y):
                ret[i][j]=const.UNLIT
        return ret