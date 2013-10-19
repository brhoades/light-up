#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Solution Class File
# This file houses the solution class (sol) which contains arrangments
#   for bulbs on a graph and related values.

from util import flip,delprn,maxLights
from const import *
import graph
import random
import math

class sol:
    def __init__( self, gen, **args ):
        self.graph = graph.graph( )
        self.graph.copy( gen.puz )
        
        # This will be our level in the fitness table
        self.fit=-1
        
        #We store our metrics in here for easy usage
        #these are our MOEA constraints
        self.moeaf = []

        #Who we dominate goes here, references to them
        self.dominates = []
        
        #Who dominates us goes here, references
        self.domee = []

        # Birth Generation
        self.birth=gen.num
        
        # Bad sol
        self.bad = False
        
        # Generation of origin
        self.gen = gen
        
        if 'mate' in args:
            self.breed( args['mate'][0], args['mate'][1] )
    
    # Removes references to our graph and to our gen so we can be collected by the gc
    def delete( self ):
        self.gen = None
        self.moeaf = []
        self.dominates = []
        self.graph.delete( )
    
    # Random graph solver
    def rng( self, forceValid ):
        x = self.graph.x
        y = self.graph.y
        if forceValid:
            blacktiles = []
            blacktiles.extend(list(self.graph.sqgt[gt.BLACK1]))
            blacktiles.extend(list(self.graph.sqgt[gt.BLACK2]))
            blacktiles.extend(list(self.graph.sqgt[gt.BLACK3]))
            blacktiles.extend(list(self.graph.sqgt[gt.BLACK4]))
            
            random.shuffle(blacktiles)
            
            #go through all satisifiable black tile's neighbors
            #if they have #neighbors = requirement, add bulbs
            for sqr in blacktiles:
                if len(sqr.neighbors) == sqr.type-gt.TRANSFORM:
                    for hsqr in sqr.neighbors:
                        if hsqr.type == gt.LIT or hsqr.type == gt.UNLIT:
                            hsqr.addLight( )
        
        # Bulbs used are related to # of black tiles and size of board.
        # This is a rough approximation. Overshooting it causes the board to be solved very quickly and
        #   statistically isn't interesting at all.
        maxbulbs = max(x,y)
        maxbulbs += self.graph.blacks( )
        
        #Place a random number of bulbs
        for i in range(random.randint(0,maxbulbs)):
            #(last arg) is only true when we're doing forceValid
            tx = math.floor(random.uniform(0, x))
            ty = math.floor(random.uniform(0, y))
            if not self.graph.data[tx][ty].isBlack( ) and self.graph.data[tx][ty].type != gt.BULB:
                self.graph.addLight(tx, ty)

    #FIXME: DESCRIBE
    def fitness( self ):
        for i in moeacon:
            #MAXIMIZE LIT SQUARES
            if i == LITSQ:
                self.moeaf.append(self.graph.litsq( ))
            #MINIMIZE BULBS SHINING ON EACH OTHER
            #Each bulb shining on another one gets 1
            #3 bulbs in a line, for example, get a total of 6 off
            elif i == BULBCONFLICT:
                violations = 0
                for sqr in self.graph.sqgt[gt.BULB]:
                    violations += len(sqr.owner)
                self.moeaf.append(violations)
            #MINIMIZE BLACK TILE SATISFICATION VIOLATIONS
            #Each missing light adds an additional 1
            #Each light over adds an additional 1
            #4 bulbs around a zero, for example, gets a 4
            #or a 4 bulb requirement with 0 bulbs around it gets 4
            elif i == BLACKVIO:
                violations = 0
                for sqr in self.graph.sqgt[gt.BLACK_THRESHOLD]:
                    violations += maxLights(sqr.type)-len(sqr.lights)
                self.moeaf.append(violations)
                
        ##FIXME: We shouldn't completely rebuild each time
        #self.gen.fitTable.reCheck( )
        
        #return self.level

    # Trash things and use them again later. Save a crapton of time not allocating memory and recursively
    #   destroying / creating things.
    def trash( self ):        
        self.gen.ind.remove(self)
        self.gen.fitTable.rm(self)
        self.gen.trash.append(self)
  
        self.graph.clear( )
        self.birth = -1
        self.bad = False
        self.fit = 0
  
    # Combine two objects with something akin to crossover.
    #   ideal and is completely random.
    def breed( self, p1, p2 ):
        unlitsq = list( self.graph.sqgt[gt.UNLIT] )
        random.shuffle( unlitsq )
        self.birth=self.gen.num
        
        while len(unlitsq) > 0:
            sqr = unlitsq.pop( )
            if sqr.isBlack( ):
                continue
            if flip( ):
                if p1.graph.data[sqr.x][sqr.y].type == gt.BULB:
                    self.graph.addLight( sqr.x, sqr.y, True )
            elif p2.graph.data[sqr.x][sqr.y].type == gt.BULB:
                self.graph.addLight( sqr.x, sqr.y, True )            
