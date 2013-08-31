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
        #Our best solution found
        self.bestSol = []

        #Have we made a bad placement?
        self.bad=False
        #How many lights have been placed
        self.lights=0
        #How many squares are lit
        self.litsq=0
        #Fitness
        self.fit=-1
        #X tracker
        self.x=0
        #y tracker
        self.y=0
        #method for choosing best graph
        self.method=meth
        #puzzle we are solving
        self.puz = None
        
        #best
        self.bestLights=100^10
        self.bestLitsq=100^10
            
    def __str__(self):
        puz = self.puz
        ret = ""
        
        if self.lights != 0:
            sol = deepcopy(self.data)
        else:
            sol = deepcopy(self.bestSol)
        
        for i in range(0,puz.x):
            if len(sol[i]) <= 0:
                next
            for j in range(0,len(sol[i])):
                val = sol[i].pop()
                #print("Adding bulb @ (", i, ",", val, ")")
                puz.addLight(i,val)
        
        return puz.__str__()
    
    #Solve this graph and find the "best" solution, specified by the cfg file
    def ideal( self, puz ):
        self.puz = deepcopy( puz )
        self.data = []
        #initilize arrays on first run
        self.data = [[] for i in range(0,self.puz.x)]
        self.bestSol = [[] for i in range(0,self.puz.x)]
            
        print( "Finding ideal solution: " )
        
        for i in range(0, self.puz.x):
            for j in range(0, self.puz.y):
                if not self.puz.badBulbSpot( i, j ):
                    print( "START: ", i, j )
                    self.thisIdeal( i, j )
                    
        del self.data
        self.data = []
        print( "Found! lamps: ", self.bestLights, " lit tiles: ", self.bestLitsq, "/", self.puz.unlitTiles() )
        return 1

    def thisIdeal( self, x, y ):
        if self.puz.addLight( x, y, True ):
            self.data[x].append(y)
        else:
            print( "Done!" )
            return True
                  
        if not self.betterSol( ):
            return
                    
        tri = True
        for i in range(0, self.puz.x):
            for j in range(0, self.puz.y):
                if self.puz.data[i][j].type == gt.UNLIT:
                    tri &= self.thisIdeal( i, j )
                
        if tri:
            if self.betterSol( ):
                self.bestSol = deepcopy( self.data )
                self.bestLights = self.puz.lights
                self.bestLitsq = self.puz.litsq
            
        self.puz.data[x][y].rmLight( self.puz )
        self.data[x].remove(y)

        return False
    
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
        return False
    ########################################################
    #Random solver
    ########################################################
    #def solve( 
