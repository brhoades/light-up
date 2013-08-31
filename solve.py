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
        #Number of iterations
        self.iter=0
        #X tracker
        self.x=0
        #y tracker
        self.y=0
        #method for choosing best graph
        self.method=meth
        #puzzle we are solving
        self.puz = None
        
        #best
        self.bestLights=0
        self.bestLitsq=0
            
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
    def ideal( self, puz=None ):
        x = self.x
        y = self.y
        ret = -1
        nextBool = False

        if self.puz == None:
            self.puz = puz
            self.cleanPuz = puz
            self.data = []
            #initilize arrays on first run
            self.data = [[] for i in range(0,self.puz.x)]
            self.bestSol = [[] for i in range(0,self.puz.x)]
                
            print( "Finding ideal solution: " )
        
        if self.puz.addLight( x, y, True ):
            #print( "precrash: ", x, y, len(self.data) )
            print(self.puz)
            self.data[x].append(y)
            
        elif self.iter == 1:                            #No point in going back here if it's our first
            self.iter -= 1
            print( "Bad placement" )
        
        if self.next( ):
            self.iter += 1
            print( x, y, self.iter )
            ret = self.ideal( )
        else:
            print( "done! ", self.iter, self.lights )
            if self.betterSol( ):
                self.bestSol = deepcopy( self.data )
                self.bestLights = self.lights
                self.bestLitsq = self.litsq
            self.data = [[] for i in range(0,self.cleanPuz.x)]
            if self.iter == 1:
                del self.data
                self.data = []
                print( "Found! lamps: ", self.bestLights, " lit tiles: ", self.bestLitsq, "/", self.puz.unlitTiles() )
                return solv.DONE
            self.iter -= 1
            self.lights=0
            self.litsq=0
            del self.puz
            self.puz = self.cleanPuz
            return solv.NEXTPLACE
        
        if ret == solv.NEXTPLACE and self.iter != 1:
            print( "falling: ", self.iter )
            self.iter -= 1
            return ret
        elif ret == solv.NEXTPLACE and self.iter == 1:
            self.x = x
            self.y = y
            self.next( )
            print( "restarting: ", self.x, self.y, self.iter )
            self.ideal( )
        elif ret == solv.DONE:
            return ret
        return 1

    #Auto increment the interal x/y tracker
    def next( self ):
        if self.x < (self.puz.x-1):
            self.x += 1
        elif self.y < (self.puz.y-1):
            self.x = 0
            self.y += 1
        elif self.y >= (self.puz.y-1) and self.x >= (self.puz.x-1):
           return False
        
        print( "Next: ", self.iter )
        return True
    
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

