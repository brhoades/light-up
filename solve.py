#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from graph import graph
from const import (gt, lprets, solv, method)
from copy import deepcopy

class solve:
    def __init__( self, meth ):
        #Our solution will be a double array of all lamp bulbs to be placed
        self.data = []

        #Have we made a bad placement?
        self.bad=False
        #How many lights have been placed
        self.lights=0
        #How many squares are lit
        self.litsq=0
        #Fitness
        self.fit=-1
        #Number of iterations
        self.iter=0
        #X tracker
        self.x=0
        #y tracker
        self.y=0
        #method for choosing best graph
        self.method=meth
        
        #best
        self.bestLights=0
        self.bestLitsq=0
            

    #Solve this graph and find the "best" solution, specified by the cfg file
    def ideal( self, puz ):
        x = self.x
        y = self.y
        ret = -1
        nextBool = False

        #initilize arrays
        for i in range(0,puz.x):
            self.data.append([])
        
        self.bestSol=[]
        for i in range(0,puz.x):
            self.bestSol.append([])
        
        if x == 0 and y == 0:
            print( "Finding ideal solution:", end='' )
        
        ret = puz.addLight( x, y, True )
        if ret != lprets.BAD:
            self.data[x].append(y)
            self.lights += 1
            self.litsq += ret-lprets.OFFSET
        elif self.iter == 1:                            #No point in going back here if it's our first
            self.iter -= 1
        
        if self.next( puz ):
            ret = self.ideal( puz )
        else:
            if self.betterSol( ):
                self.bestSol = deepcopy( self.data )
                self.bestLights = self.lights
                self.bestLitsq = self.litsq
                for i in range(0,self.x):
                    del self.data[i]
                    self.data[i] = []
                if self.iter == 1:
                    self.data = deepcopy( self.bestSol )
                    del self.bestSol
                    return solv.DONE
                self.iter=0
                self.lights=0
                self.litsq=0
                return solv.NEXTPLACE
        
        if ret != solv.DONE and self.iter != 1:
            self.iter -= 1
            return ret
        elif ret == solv.NEXTPLACE and self.iter == 1:
            self.iter -= 1
            self.next( puz )
            self.ideal( puz )
        elif ret == solv.DONE:
            return ret
        return 1

    #Auto increment the interal x/y tracker
    def next( self, puz ):
        if self.x < (puz.x-1):
            self.x += 1
        elif self.y < (puz.y-1):
            self.x = 0
            self.y += 1
        elif self.y >= (puz.y-1) and self.x >= (puz.x-1):
           return 0
        
        self.iter += 1
        return 1
    
    #Is our current solution (self) better than our best? (self.bestSol)
    def betterSol( self ):
        if self.method == method.MINBULB:
            if (self.lights >= self.bestLights and self.litsq > self.bestLitsq) or \
                (self.lights > self.bestLights and self.litsq >= self.bestLitsq):
                return True
        elif self.method == method.MAXBULB:
            if (self.lights <= self.bestLights and self.litsq < self.bestLitsq) or \
                (self.lights < self.bestLights and self.litsq <= self.bestLitsq):
                return True
        elif self.method == method.ANY:
            if self.bestLights == 0:
                return True
            else:
                return False #Accepting our first solution here--- generally--- gives us the max lit

